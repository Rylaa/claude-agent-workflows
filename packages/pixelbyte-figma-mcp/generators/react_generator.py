"""
React Code Generator - Recursive JSX rendering with full property support.

Generates React component code (with or without Tailwind CSS) from Figma node trees.
Supports: fills (solid, gradient, image), strokes, corner radius, shadows,
blur, opacity, blend modes, rotation, padding, auto-layout, text styling,
hyperlinks, line clamping, and paragraph spacing.
"""

import re
from typing import Dict, Any, Optional

# Import shared constants and CSS helpers from base module
from generators.base import (
    TAILWIND_WEIGHT_MAP,
    TAILWIND_ALIGN_MAP,
    MAX_CHILDREN_LIMIT,
    _get_background_css,
    _extract_stroke_data,
    _extract_effects_data,
    _corner_radii_to_css,
    _transform_to_css,
    _blend_mode_to_css,
    _rgba_to_hex,
    _text_case_to_css,
    _text_decoration_to_css,
)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

_ROOT_CLASSNAME_LITERAL_RE = re.compile(r'className="([^"]*)"')
_ROOT_CLASSNAME_EXPR_RE = re.compile(r'className=\{([^}]*)\}')
_ROOT_OPEN_TAG_RE = re.compile(r'(<[A-Za-z][\w:-]*)([^>]*?)(/?)>')


def _format_px(value: Any) -> Optional[str]:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if abs(number - round(number)) < 0.01:
        return f"{int(round(number))}px"
    return f"{number:.2f}".rstrip("0").rstrip(".") + "px"


def _is_freeform_layout(layout_mode: Optional[str]) -> bool:
    return layout_mode in (None, "", "NONE")


def _absolute_offsets(node: Dict[str, Any], parent_node: Optional[Dict[str, Any]]) -> tuple[Optional[str], Optional[str]]:
    if not parent_node:
        return None, None

    node_bbox = node.get("absoluteBoundingBox")
    parent_bbox = parent_node.get("absoluteBoundingBox")
    if not isinstance(node_bbox, dict) or not isinstance(parent_bbox, dict):
        return None, None

    left = _format_px(float(node_bbox.get("x", 0)) - float(parent_bbox.get("x", 0)))
    top = _format_px(float(node_bbox.get("y", 0)) - float(parent_bbox.get("y", 0)))
    return left, top


def _relative_transform_matrix(node: Dict[str, Any]) -> Optional[str]:
    relative = node.get("relativeTransform")
    if not isinstance(relative, list) or len(relative) < 2:
        return None
    row0 = relative[0]
    row1 = relative[1]
    if not isinstance(row0, list) or not isinstance(row1, list):
        return None
    if len(row0) < 3 or len(row1) < 3:
        return None

    try:
        m00 = float(row0[0])
        m01 = float(row0[1])
        m02 = float(row0[2])
        m10 = float(row1[0])
        m11 = float(row1[1])
        m12 = float(row1[2])
    except (TypeError, ValueError):
        return None

    # CSS matrix(a, b, c, d, tx, ty) maps from the same 2x3 affine representation.
    return f"matrix({m00:.6f}, {m10:.6f}, {m01:.6f}, {m11:.6f}, {m02:.2f}, {m12:.2f})"


def _attach_component_classname(inner_jsx: str) -> str:
    """Merge component className prop into the first render root element."""
    if "{className}" in inner_jsx or "${className}" in inner_jsx:
        return inner_jsx

    replaced = False

    def _replace_literal(match: re.Match[str]) -> str:
        nonlocal replaced
        if replaced:
            return match.group(0)
        replaced = True
        existing = match.group(1).strip()
        if existing:
            return f'className={{`${{className}} {existing}`.trim()}}'
        return "className={className}"

    result = _ROOT_CLASSNAME_LITERAL_RE.sub(_replace_literal, inner_jsx, count=1)
    if replaced:
        return result

    def _replace_expr(match: re.Match[str]) -> str:
        nonlocal replaced
        if replaced:
            return match.group(0)
        replaced = True
        existing = match.group(1).strip()
        return "className={[" + existing + ", className].filter(Boolean).join(' ')}"

    result = _ROOT_CLASSNAME_EXPR_RE.sub(_replace_expr, inner_jsx, count=1)
    if replaced:
        return result

    def _insert_classname(match: re.Match[str]) -> str:
        nonlocal replaced
        if replaced:
            return match.group(0)
        replaced = True
        tag_start, attrs, self_close = match.group(1), match.group(2), match.group(3)
        attrs = attrs or ""
        close = " />" if self_close else ">"
        return f"{tag_start}{attrs} className={{className}}{close}"

    return _ROOT_OPEN_TAG_RE.sub(_insert_classname, inner_jsx, count=1)

def generate_react_code(
    node: Dict[str, Any],
    component_name: str,
    use_tailwind: bool = True,
    hard_fidelity_profile: bool = False,
) -> str:
    """Generate detailed React component code from Figma node with all nested children."""
    # Generate the inner JSX content recursively
    inner_jsx = recursive_node_to_jsx(
        node,
        indent=6,
        use_tailwind=use_tailwind,
        parent_node=None,
        hard_fidelity_profile=hard_fidelity_profile,
    )
    inner_jsx = _attach_component_classname(inner_jsx)

    if use_tailwind:
        code = f'''import React from 'react';

interface {component_name}Props {{
  className?: string;
}}

export const {component_name}: React.FC<{component_name}Props> = ({{
  className = '',
}}) => {{
  return (
{inner_jsx}
  );
}};

export default {component_name};
'''
    else:
        code = f'''import React from 'react';

interface {component_name}Props {{
  className?: string;
}}

export const {component_name}: React.FC<{component_name}Props> = ({{
  className = '',
}}) => {{
  return (
{inner_jsx}
  );
}};

export default {component_name};
'''
    return code


def _vector_to_inline_svg(node: Dict[str, Any], prefix: str, use_tailwind: bool) -> Optional[str]:
    """Generate inline SVG JSX for VECTOR/BOOLEAN_OPERATION nodes when geometry exists."""
    fill_geometry = node.get('fillGeometry', [])
    stroke_geometry = node.get('strokeGeometry', [])
    if not fill_geometry and not stroke_geometry:
        return None

    bbox = node.get('absoluteBoundingBox', {})
    width = int(bbox.get('width', 24)) or 24
    height = int(bbox.get('height', 24)) or 24

    fill_color = 'currentColor'
    for fill in node.get('fills', []):
        if fill.get('type') == 'SOLID' and fill.get('visible', True):
            fill_color = _rgba_to_hex(fill.get('color', {}))
            break

    stroke_color = 'none'
    stroke_width = max(1, int(node.get('strokeWeight', 1) or 1))
    for stroke in node.get('strokes', []):
        if stroke.get('type') == 'SOLID' and stroke.get('visible', True):
            stroke_color = _rgba_to_hex(stroke.get('color', {}))
            break

    svg_lines = []
    if use_tailwind:
        svg_lines.append(
            f'{prefix}<svg className="w-[{width}px] h-[{height}px]" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">'
        )
    else:
        svg_lines.append(
            f'{prefix}<svg style={{{{ width: \'{width}px\', height: \'{height}px\' }}}} viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">'
        )

    for geom in fill_geometry[:200]:
        path_data = geom.get('path', '')
        if path_data:
            safe_path = str(path_data).replace('"', '&quot;')
            svg_lines.append(f'{prefix}  <path d="{safe_path}" fill="{fill_color}" />')

    for geom in stroke_geometry[:200]:
        path_data = geom.get('path', '')
        if path_data:
            safe_path = str(path_data).replace('"', '&quot;')
            svg_lines.append(
                f'{prefix}  <path d="{safe_path}" fill="none" stroke="{stroke_color}" strokeWidth="{stroke_width}" />'
            )

    svg_lines.append(f'{prefix}</svg>')
    return '\n'.join(svg_lines)


def recursive_node_to_jsx(
    node: Dict[str, Any],
    indent: int = 6,
    use_tailwind: bool = True,
    parent_node: Optional[Dict[str, Any]] = None,
    hard_fidelity_profile: bool = False,
) -> str:
    """Recursively generate detailed JSX code for nested children with all styles."""
    if node.get("visible", True) is False:
        return ""

    lines = []
    prefix = ' ' * indent
    node_type = node.get('type', '')
    name = node.get('name', 'Unknown')

    # Get all styles
    bbox = node.get('absoluteBoundingBox', {})
    width = int(bbox.get('width', 0))
    height = int(bbox.get('height', 0))

    # Fills (with gradient support)
    fills = node.get('fills', [])
    bg_value, bg_type = _get_background_css(node)

    # Strokes (comprehensive)
    stroke_data = _extract_stroke_data(node)
    stroke_color = ''
    stroke_weight = stroke_data['weight'] if stroke_data else 0
    stroke_align = stroke_data['align'] if stroke_data else 'INSIDE'
    stroke_dashes = stroke_data['dashes'] if stroke_data else []
    stroke_individual = stroke_data.get('individualWeights', {}) if stroke_data else {}
    if stroke_data and stroke_data['colors']:
        first_stroke = stroke_data['colors'][0]
        if first_stroke.get('type') == 'SOLID':
            stroke_color = first_stroke.get('color', '')

    # Effects (shadows and blurs)
    effects_data = _extract_effects_data(node)
    shadow_css = ''
    layer_blur_css = ''
    backdrop_blur_css = ''
    if effects_data['shadows']:
        shadow_parts = []
        for shadow in effects_data['shadows']:
            offset = shadow.get('offset', {'x': 0, 'y': 0})
            shadow_type = shadow.get('type', 'DROP_SHADOW')
            inset_prefix = 'inset ' if shadow_type == 'INNER_SHADOW' else ''
            shadow_parts.append(
                f"{inset_prefix}{int(offset.get('x', 0))}px {int(offset.get('y', 0))}px {int(shadow.get('radius', 0))}px {int(shadow.get('spread', 0))}px {shadow.get('color', '#000')}"
            )
        shadow_css = ', '.join(shadow_parts)
    if effects_data['blurs']:
        for blur in effects_data['blurs']:
            if blur.get('type') == 'LAYER_BLUR':
                layer_blur_css = f"blur({int(blur.get('radius', 0))}px)"
            elif blur.get('type') == 'BACKGROUND_BLUR':
                backdrop_blur_css = f"blur({int(blur.get('radius', 0))}px)"

    # Corner radius (with individual corners support)
    corner_radius_css = _corner_radii_to_css(node)

    # Transform (rotation, scale)
    transform_css = _transform_to_css(node)

    # Blend mode
    blend_mode = node.get('blendMode', 'PASS_THROUGH')
    blend_mode_css = _blend_mode_to_css(blend_mode)

    # Opacity
    opacity = node.get('opacity', 1)

    # Layout
    layout_mode = node.get('layoutMode')
    gap = node.get('itemSpacing', 0)
    padding_top = node.get('paddingTop', 0)
    padding_right = node.get('paddingRight', 0)
    padding_bottom = node.get('paddingBottom', 0)
    padding_left = node.get('paddingLeft', 0)

    # Alignment
    primary_align = node.get('primaryAxisAlignItems', 'MIN')
    counter_align = node.get('counterAxisAlignItems', 'MIN')
    layout_positioning = node.get('layoutPositioning')
    is_absolute_child = layout_positioning == 'ABSOLUTE'
    parent_layout_mode = parent_node.get('layoutMode') if parent_node else None
    force_absolute_for_freeform = (
        hard_fidelity_profile
        and parent_node is not None
        and _is_freeform_layout(parent_layout_mode)
        and layout_positioning != 'AUTO'
    )
    use_absolute_offsets = is_absolute_child or force_absolute_for_freeform
    left_px, top_px = _absolute_offsets(node, parent_node) if use_absolute_offsets else (None, None)

    matrix_transform_css: Optional[str] = None
    if hard_fidelity_profile and use_absolute_offsets:
        matrix_transform_css = _relative_transform_matrix(node)
        size = node.get("size")
        if matrix_transform_css and isinstance(size, dict):
            size_x = size.get("x")
            size_y = size.get("y")
            try:
                if size_x is not None:
                    width = int(round(float(size_x)))
                if size_y is not None:
                    height = int(round(float(size_y)))
            except (TypeError, ValueError):
                pass
            left_px = "0px"
            top_px = "0px"

    if node_type == 'TEXT':
        text = node.get('characters', name)
        style = node.get('style', {})
        font_size = style.get('fontSize', 16)
        font_weight = style.get('fontWeight', 400)
        font_family = style.get('fontFamily', '')
        line_height = style.get('lineHeightPx')
        letter_spacing = style.get('letterSpacing', 0)
        text_align = style.get('textAlignHorizontal', 'LEFT').lower()
        text_case = style.get('textCase', 'ORIGINAL')
        text_decoration = style.get('textDecoration', 'NONE')

        # Get hyperlink if present
        hyperlink = node.get('hyperlink')
        hyperlink_url = None
        if hyperlink and hyperlink.get('type') == 'URL':
            hyperlink_url = hyperlink.get('url', '')

        # Get text color from fills
        text_color = ''
        if fills and fills[0].get('type') == 'SOLID' and fills[0].get('visible', True):
            text_color = _rgba_to_hex(fills[0].get('color', {}))

        # Convert text case and decoration to CSS
        text_transform = _text_case_to_css(text_case)
        text_dec_value = _text_decoration_to_css(text_decoration)

        if use_tailwind:
            weight_class = TAILWIND_WEIGHT_MAP.get(font_weight, 'font-normal')
            align_class = TAILWIND_ALIGN_MAP.get(text_align.upper(), '')

            # Tailwind text-transform classes
            transform_map = {'uppercase': 'uppercase', 'lowercase': 'lowercase', 'capitalize': 'capitalize'}
            transform_class = transform_map.get(text_transform, '') if text_transform else ''

            # Tailwind text-decoration classes
            decoration_map = {'underline': 'underline', 'line-through': 'line-through'}
            decoration_class = decoration_map.get(text_dec_value, '') if text_dec_value else ''

            classes = [f'text-[{int(font_size)}px]', weight_class]
            if text_color:
                classes.append(f'text-[{text_color}]')
            if line_height:
                classes.append(f'leading-[{int(line_height)}px]')
            if letter_spacing:
                classes.append(f'tracking-[{letter_spacing:.2f}px]')
            if align_class:
                classes.append(align_class)
            if transform_class:
                classes.append(transform_class)
            if decoration_class:
                classes.append(decoration_class)

            # Line clamp (maxLines + textTruncation)
            max_lines = style.get('maxLines')
            text_truncation = style.get('textTruncation', 'DISABLED')
            if max_lines and max_lines > 0:
                classes.append(f'line-clamp-{max_lines}')
                if text_truncation == 'ENDING':
                    classes.append('text-ellipsis')

            # Paragraph spacing (margin-bottom)
            paragraph_spacing = style.get('paragraphSpacing', 0)
            if paragraph_spacing and paragraph_spacing > 0:
                classes.append(f'mb-[{int(paragraph_spacing)}px]')

            if use_absolute_offsets:
                classes.append('absolute')
                if matrix_transform_css:
                    classes.append('left-[0px]')
                    classes.append('top-[0px]')
                else:
                    if left_px:
                        classes.append(f'left-[{left_px}]')
                    if top_px:
                        classes.append(f'top-[{top_px}]')

            class_str = ' '.join(filter(None, classes))
            # Escape text for JSX
            escaped_text = text.replace('{', '{{').replace('}', '}}').replace('<', '&lt;').replace('>', '&gt;')

            # Wrap in anchor tag if hyperlink present
            if hyperlink_url:
                lines.append(f'{prefix}<a href="{hyperlink_url}" className="{class_str}" target="_blank" rel="noopener noreferrer">{escaped_text}</a>')
            else:
                lines.append(f'{prefix}<span className="{class_str}">{escaped_text}</span>')
        else:
            styles = [f"fontSize: '{int(font_size)}px'", f"fontWeight: {font_weight}"]
            if text_color:
                styles.append(f"color: '{text_color}'")
            if font_family:
                styles.append(f"fontFamily: '{font_family}'")
            if line_height:
                styles.append(f"lineHeight: '{int(line_height)}px'")
            if letter_spacing:
                styles.append(f"letterSpacing: '{letter_spacing:.2f}px'")
            if text_align != 'left':
                styles.append(f"textAlign: '{text_align}'")
            if text_transform:
                styles.append(f"textTransform: '{text_transform}'")
            if text_dec_value:
                styles.append(f"textDecoration: '{text_dec_value}'")

            # Line clamp (maxLines + textTruncation)
            max_lines = style.get('maxLines')
            text_truncation = style.get('textTruncation', 'DISABLED')
            if max_lines and max_lines > 0:
                styles.append("display: '-webkit-box'")
                styles.append(f"WebkitLineClamp: {max_lines}")
                styles.append("WebkitBoxOrient: 'vertical'")
                styles.append("overflow: 'hidden'")
                if text_truncation == 'ENDING':
                    styles.append("textOverflow: 'ellipsis'")

            # Paragraph spacing (margin-bottom)
            paragraph_spacing = style.get('paragraphSpacing', 0)
            if paragraph_spacing and paragraph_spacing > 0:
                styles.append(f"marginBottom: '{int(paragraph_spacing)}px'")

            if use_absolute_offsets:
                styles.append("position: 'absolute'")
                if matrix_transform_css:
                    styles.append("left: '0px'")
                    styles.append("top: '0px'")
                    styles.append(f"transform: '{matrix_transform_css}'")
                    styles.append("transformOrigin: 'top left'")
                else:
                    if left_px:
                        styles.append(f"left: '{left_px}'")
                    if top_px:
                        styles.append(f"top: '{top_px}'")

            style_str = ', '.join(styles)
            escaped_text = text.replace('{', '{{').replace('}', '}}').replace('<', '&lt;').replace('>', '&gt;')

            # Wrap in anchor tag if hyperlink present
            if hyperlink_url:
                lines.append(f'{prefix}<a href="{hyperlink_url}" style={{{{ {style_str} }}}} target="_blank" rel="noopener noreferrer">{escaped_text}</a>')
            else:
                lines.append(f'{prefix}<span style={{{{ {style_str} }}}}>{escaped_text}</span>')

    elif node_type == 'VECTOR' or node_type == 'BOOLEAN_OPERATION':
        lines.append(f'{prefix}{{/* Icon: {name} */}}')
        inline_svg = _vector_to_inline_svg(node, prefix, use_tailwind)
        if inline_svg:
            lines.append(inline_svg)
        elif use_tailwind:
            classes = []
            if width:
                classes.append(f'w-[{width}px]')
            if height:
                classes.append(f'h-[{height}px]')
            if bg_value and bg_type == 'color':
                classes.append(f'bg-[{bg_value}]')
            class_str = ' '.join(filter(None, classes))
            lines.append(f'{prefix}<div className="{class_str}" />')
        else:
            styles = []
            if width:
                styles.append(f"width: '{width}px'")
            if height:
                styles.append(f"height: '{height}px'")
            if bg_value and bg_type == 'color':
                styles.append(f"backgroundColor: '{bg_value}'")
            style_str = ', '.join(styles) if styles else "width: '0px'"
            lines.append(f'{prefix}<div style={{{{ {style_str} }}}} />')

    else:
        # Container element (FRAME, GROUP, COMPONENT, INSTANCE, RECTANGLE, etc.)
        if use_tailwind:
            classes = []
            inline_styles = []  # For properties that can't be expressed in Tailwind alone

            if width:
                classes.append(f'w-[{width}px]')
            if height:
                classes.append(f'h-[{height}px]')

            if node.get("clipsContent"):
                classes.append("overflow-hidden")

            if node.get("children") and (
                any(child.get("layoutPositioning") == "ABSOLUTE" for child in node.get("children", []))
                or (hard_fidelity_profile and _is_freeform_layout(layout_mode))
            ) and not use_absolute_offsets:
                classes.append("relative")

            # Background (solid color, gradient, image, or layered)
            if bg_value and bg_type:
                if bg_type == 'color':
                    classes.append(f'bg-[{bg_value}]')
                elif bg_type in ('gradient', 'image', 'layered'):
                    # Gradients, images, and layered backgrounds need inline style
                    inline_styles.append(f"background: '{bg_value}'")

            # Corner radius (with individual corners)
            if corner_radius_css:
                classes.append(f'rounded-[{corner_radius_css}]')

            # Strokes
            if stroke_color and stroke_weight:
                has_dashes = bool(stroke_dashes)
                if stroke_individual:
                    # Individual border widths
                    for side, tw_prefix in [('top', 'border-t'), ('right', 'border-r'), ('bottom', 'border-b'), ('left', 'border-l')]:
                        w = stroke_individual.get(side, 0)
                        if w:
                            classes.append(f'{tw_prefix}-[{w}px]')
                else:
                    classes.append(f'border-[{stroke_weight}px]')
                classes.append(f'border-[{stroke_color}]')
                if has_dashes:
                    inline_styles.append("borderStyle: 'dashed'")
                # Border position (only INSIDE is default in CSS)
                if stroke_align == 'OUTSIDE':
                    inline_styles.append("boxSizing: 'content-box'")

            # Shadows
            if shadow_css:
                classes.append(f'shadow-[{shadow_css}]')

            # Blur filters
            if layer_blur_css:
                inline_styles.append(f"filter: '{layer_blur_css}'")
            if backdrop_blur_css:
                inline_styles.append(f"backdropFilter: '{backdrop_blur_css}'")

            # Transform (rotation, scale)
            if matrix_transform_css:
                inline_styles.append(f"transform: '{matrix_transform_css}'")
                inline_styles.append("transformOrigin: 'top left'")
            elif transform_css:
                inline_styles.append(f"transform: '{transform_css}'")

            # Blend mode
            if blend_mode_css:
                classes.append(f'mix-blend-{blend_mode_css}')

            # Opacity
            if opacity < 1:
                classes.append(f'opacity-[{opacity}]')

            # Layout
            if layout_mode:
                classes.append('flex')
                classes.append('flex-col' if layout_mode == 'VERTICAL' else 'flex-row')
                if gap:
                    classes.append(f'gap-[{gap}px]')
                # Alignment
                justify_map = {'MIN': 'justify-start', 'CENTER': 'justify-center', 'MAX': 'justify-end', 'SPACE_BETWEEN': 'justify-between'}
                items_map = {'MIN': 'items-start', 'CENTER': 'items-center', 'MAX': 'items-end'}
                classes.append(justify_map.get(primary_align, ''))
                classes.append(items_map.get(counter_align, ''))

            # Padding
            if padding_top or padding_right or padding_bottom or padding_left:
                if padding_top:
                    classes.append(f'pt-[{padding_top}px]')
                if padding_right:
                    classes.append(f'pr-[{padding_right}px]')
                if padding_bottom:
                    classes.append(f'pb-[{padding_bottom}px]')
                if padding_left:
                    classes.append(f'pl-[{padding_left}px]')

            # Flex child properties (layoutGrow, layoutPositioning, layoutAlign)
            layout_grow = node.get('layoutGrow', 0)
            layout_align = node.get('layoutAlign')

            if layout_grow and layout_grow > 0:
                classes.append('grow')  # Tailwind: flex-grow: 1
            if use_absolute_offsets:
                classes.append('absolute')
                if matrix_transform_css:
                    classes.append('left-[0px]')
                    classes.append('top-[0px]')
                else:
                    if left_px:
                        classes.append(f'left-[{left_px}]')
                    if top_px:
                        classes.append(f'top-[{top_px}]')
            if layout_align == 'STRETCH':
                classes.append('self-stretch')
            elif layout_align == 'INHERIT':
                classes.append('self-auto')

            class_str = ' '.join(filter(None, classes))

            # Combine className and style if needed
            if inline_styles:
                style_str = ', '.join(inline_styles)
                lines.append(f'{prefix}<div className="{class_str}" style={{{{ {style_str} }}}}>')
            else:
                lines.append(f'{prefix}<div className="{class_str}">')
        else:
            styles = []
            if width:
                styles.append(f"width: '{width}px'")
            if height:
                styles.append(f"height: '{height}px'")
            if node.get("clipsContent"):
                styles.append("overflow: 'hidden'")

            if node.get("children") and (
                any(child.get("layoutPositioning") == "ABSOLUTE" for child in node.get("children", []))
                or (hard_fidelity_profile and _is_freeform_layout(layout_mode))
            ) and not use_absolute_offsets:
                styles.append("position: 'relative'")

            # Background (solid color, gradient, image, or layered)
            if bg_value and bg_type:
                if bg_type == 'color':
                    styles.append(f"backgroundColor: '{bg_value}'")
                elif bg_type in ('gradient', 'image', 'layered'):
                    # Gradients, images, and layered backgrounds use 'background' shorthand
                    styles.append(f"background: '{bg_value}'")

            # Corner radius (with individual corners)
            if corner_radius_css:
                styles.append(f"borderRadius: '{corner_radius_css}'")

            # Strokes
            if stroke_color and stroke_weight:
                styles.append(f"border: '{stroke_weight}px solid {stroke_color}'")
                if stroke_align == 'OUTSIDE':
                    styles.append("boxSizing: 'content-box'")

            # Shadows
            if shadow_css:
                styles.append(f"boxShadow: '{shadow_css}'")

            # Blur filters
            if layer_blur_css:
                styles.append(f"filter: '{layer_blur_css}'")
            if backdrop_blur_css:
                styles.append(f"backdropFilter: '{backdrop_blur_css}'")

            # Transform (rotation, scale)
            if matrix_transform_css:
                styles.append(f"transform: '{matrix_transform_css}'")
                styles.append("transformOrigin: 'top left'")
            elif transform_css:
                styles.append(f"transform: '{transform_css}'")

            # Blend mode
            if blend_mode_css:
                styles.append(f"mixBlendMode: '{blend_mode_css}'")

            # Opacity
            if opacity < 1:
                styles.append(f"opacity: {opacity}")

            # Layout
            if layout_mode:
                styles.append("display: 'flex'")
                styles.append(f"flexDirection: '{'column' if layout_mode == 'VERTICAL' else 'row'}'")
                if gap:
                    styles.append(f"gap: '{gap}px'")
                # Alignment
                justify_map = {'MIN': 'flex-start', 'CENTER': 'center', 'MAX': 'flex-end', 'SPACE_BETWEEN': 'space-between'}
                items_map = {'MIN': 'flex-start', 'CENTER': 'center', 'MAX': 'flex-end'}
                styles.append(f"justifyContent: '{justify_map.get(primary_align, 'flex-start')}'")
                styles.append(f"alignItems: '{items_map.get(counter_align, 'flex-start')}'")

            # Padding
            if padding_top or padding_right or padding_bottom or padding_left:
                styles.append(f"padding: '{padding_top}px {padding_right}px {padding_bottom}px {padding_left}px'")

            # Flex child properties (layoutGrow, layoutPositioning, layoutAlign)
            layout_grow = node.get('layoutGrow', 0)
            layout_align = node.get('layoutAlign')

            if layout_grow and layout_grow > 0:
                styles.append(f"flexGrow: {layout_grow}")
            if use_absolute_offsets:
                styles.append("position: 'absolute'")
                if matrix_transform_css:
                    styles.append("left: '0px'")
                    styles.append("top: '0px'")
                else:
                    if left_px:
                        styles.append(f"left: '{left_px}'")
                    if top_px:
                        styles.append(f"top: '{top_px}'")
            if layout_align == 'STRETCH':
                styles.append("alignSelf: 'stretch'")
            elif layout_align == 'INHERIT':
                styles.append("alignSelf: 'auto'")

            style_str = ', '.join(styles)
            lines.append(f'{prefix}<div style={{{{ {style_str} }}}}>')

        # Recursively add children
        children = node.get('children', [])
        for child in children[:MAX_CHILDREN_LIMIT]:  # Safety limit
            child_jsx = recursive_node_to_jsx(
                child,
                indent + 2,
                use_tailwind,
                parent_node=node,
                hard_fidelity_profile=hard_fidelity_profile,
            )
            if child_jsx:
                lines.append(child_jsx)

        lines.append(f'{prefix}</div>')

    return '\n'.join(lines)


# ---------------------------------------------------------------------------
# Backward-compatible aliases (match the original underscore-prefixed names)
# ---------------------------------------------------------------------------

_generate_react_code = generate_react_code
_recursive_node_to_jsx = recursive_node_to_jsx
