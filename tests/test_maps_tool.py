import os
import unittest
from unittest.mock import patch

from engine.tools.adapters.maps_tool import GoogleMapsSearchTool


class GoogleMapsSearchToolTests(unittest.TestCase):
    def test_is_disabled_by_default(self):
        with patch.dict(os.environ, {}, clear=True):
            result = GoogleMapsSearchTool().run(keyword="cafes", lat="-23", lon="-46")

        self.assertFalse(result.success)
        self.assertIn("MAPS_SCRAPER_DISABLED", result.error or "")

    def test_rejects_depth_above_governed_limit(self):
        with patch.dict(os.environ, {"THSYR_MAPS_SCRAPER_ENABLED": "true"}, clear=True):
            result = GoogleMapsSearchTool().run(
                keyword="cafes", lat="-23", lon="-46", depth=6
            )

        self.assertFalse(result.success)
        self.assertEqual(result.error, "DEPTH_LIMIT_EXCEEDED")


if __name__ == "__main__":
    unittest.main()
