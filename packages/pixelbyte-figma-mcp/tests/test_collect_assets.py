"""Tests for _collect_all_assets function."""
import pytest
import sys
sys.path.insert(0, '..')

from figma_mcp import _collect_all_assets


class TestCollectAllAssets:
    """Test asset collection with various node configurations."""

    def test_node_with_export_settings_is_collected(self):
        """A node with exportSettings should appear in exports list."""
        node = {
            'id': '6:34',
            'name': 'Bar Chart',
            'type': 'FRAME',
            'absoluteBoundingBox': {'width': 65, 'height': 98},
            'exportSettings': [
                {'format': 'PNG', 'constraint': {'type': 'SCALE', 'value': 1.0}}
            ],
            'children': [
                {'id': '6:35', 'name': 'Bar 1', 'type': 'RECTANGLE'},
                {'id': '6:36', 'name': 'Bar 2', 'type': 'RECTANGLE'},
                {'id': '6:37', 'name': 'Bar 3', 'type': 'RECTANGLE'},
            ]
        }

        assets = {'images': [], 'icons': [], 'vectors': [], 'exports': []}
        _collect_all_assets(node, 'test_file_key', assets, include_icons=True, include_vectors=False)

        # Node with exportSettings MUST be in exports
        assert len(assets['exports']) == 1
        assert assets['exports'][0]['nodeId'] == '6:34'
        assert assets['exports'][0]['nodeName'] == 'Bar Chart'

    def test_small_chart_not_classified_as_icon(self):
        """A 65x98 chart frame should NOT be classified as icon."""
        node = {
            'id': '6:34',
            'name': 'Bar Chart',
            'type': 'FRAME',
            'absoluteBoundingBox': {'width': 65, 'height': 98},
            'exportSettings': [
                {'format': 'PNG', 'constraint': {'type': 'SCALE', 'value': 1.0}}
            ],
            'children': [
                {'id': '6:35', 'name': 'Bar 1', 'type': 'VECTOR'},
                {'id': '6:36', 'name': 'Bar 2', 'type': 'VECTOR'},
                {'id': '6:37', 'name': 'Bar 3', 'type': 'VECTOR'},
            ]
        }

        assets = {'images': [], 'icons': [], 'vectors': [], 'exports': []}
        _collect_all_assets(node, 'test_file_key', assets, include_icons=True, include_vectors=False)

        # Should be in exports, NOT in icons
        assert len(assets['exports']) == 1
        assert len(assets['icons']) == 0  # Chart should NOT be misclassified as icon

    def test_icon_with_export_settings_collected_in_both(self):
        """BUG TEST: Icon frame with exportSettings should appear in BOTH icons AND exports.

        This is the actual bug: when a node is classified as icon, the function
        returns early and never checks for export settings. Nodes with exportSettings
        should ALWAYS be collected in exports, regardless of icon classification.
        """
        # This node IS a valid icon (square 24x24 with vector children)
        # BUT it also has exportSettings configured
        node = {
            'id': '1:100',
            'name': 'mynaui:check-circle',  # Has icon naming pattern
            'type': 'FRAME',
            'absoluteBoundingBox': {'width': 24, 'height': 24},
            'exportSettings': [
                {'format': 'SVG', 'constraint': {'type': 'SCALE', 'value': 1.0}}
            ],
            'children': [
                {'id': '1:101', 'name': 'Circle', 'type': 'VECTOR'},
                {'id': '1:102', 'name': 'Check', 'type': 'VECTOR'},
            ]
        }

        assets = {'images': [], 'icons': [], 'vectors': [], 'exports': []}
        _collect_all_assets(node, 'test_file_key', assets, include_icons=True, include_vectors=False)

        # Node should be in icons (correct behavior)
        assert len(assets['icons']) == 1
        assert assets['icons'][0]['nodeId'] == '1:100'

        # BUG: Node with exportSettings MUST ALSO be in exports
        # Currently fails because icon detection returns early before checking exports
        assert len(assets['exports']) == 1, "Icon with exportSettings should also appear in exports list"
        assert assets['exports'][0]['nodeId'] == '1:100'

    def test_square_frame_with_vectors_and_exports(self):
        """BUG TEST: Square frame (64x64) with vectors and export settings.

        This frame is icon-sized (64x64, 1:1 ratio) with vector children,
        so it will be classified as icon. But it also has exportSettings,
        which should still be collected.
        """
        node = {
            'id': '2:200',
            'name': 'Logo Mark',  # No ':' but is icon-sized with vectors
            'type': 'FRAME',
            'absoluteBoundingBox': {'width': 64, 'height': 64},
            'exportSettings': [
                {'format': 'PNG', 'constraint': {'type': 'SCALE', 'value': 2.0}},
                {'format': 'SVG', 'constraint': {'type': 'SCALE', 'value': 1.0}}
            ],
            'children': [
                {'id': '2:201', 'name': 'Shape 1', 'type': 'VECTOR'},
                {'id': '2:202', 'name': 'Shape 2', 'type': 'ELLIPSE'},
            ]
        }

        assets = {'images': [], 'icons': [], 'vectors': [], 'exports': []}
        _collect_all_assets(node, 'test_file_key', assets, include_icons=True, include_vectors=False)

        # This will be classified as icon due to size (64x64) + vector children
        assert len(assets['icons']) == 1

        # BUG: exportSettings should still be collected even when classified as icon
        assert len(assets['exports']) == 1, "Frame with exportSettings should be in exports even if classified as icon"
