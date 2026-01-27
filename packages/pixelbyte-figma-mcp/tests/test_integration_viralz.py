"""Integration test using real ViralZ Figma design."""
import pytest
import os
import json
import sys

sys.path.insert(0, '..')

from figma_mcp import figma_list_assets, FigmaListAssetsInput

# Skip if no API token
pytestmark = pytest.mark.skipif(
    not os.getenv('FIGMA_PERSONAL_ACCESS_TOKEN'),
    reason="FIGMA_PERSONAL_ACCESS_TOKEN not set"
)


class TestViralZDesign:
    """Test asset detection on ViralZ design."""

    FILE_KEY = "ElHzcNWC8pSYTz2lhPP9h0"
    NODE_ID = "3:217"  # iPhone 13 & 14 - 6 screen

    @pytest.fixture
    def asset_params(self):
        """Common parameters for asset listing."""
        return FigmaListAssetsInput(
            file_key=self.FILE_KEY,
            node_id=self.NODE_ID,
            include_icons=True,
            include_images=True,
            include_vectors=False,
            include_exports=True,
            response_format="json"
        )

    @pytest.mark.asyncio
    async def test_bar_chart_detected_as_export(self, asset_params):
        """Node 6:34 (bar chart) should be in exports list."""
        result = await figma_list_assets(asset_params)
        data = json.loads(result)

        # Find bar chart in exports
        exports = data.get('assets', {}).get('exports', [])
        export_ids = [e['nodeId'] for e in exports]

        # Node 6:34 should be detected
        assert '6:34' in export_ids, \
            f"Bar chart (6:34) not found in exports. Found: {export_ids}"

    @pytest.mark.asyncio
    async def test_bar_chart_not_in_icons(self, asset_params):
        """Node 6:34 (bar chart) should NOT be in icons list."""
        result = await figma_list_assets(asset_params)
        data = json.loads(result)

        # Bar chart should NOT be in icons
        icons = data.get('assets', {}).get('icons', [])
        icon_ids = [i['nodeId'] for i in icons]

        assert '6:34' not in icon_ids, \
            f"Bar chart (6:34) incorrectly classified as icon"
