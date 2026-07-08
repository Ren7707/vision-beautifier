import unittest

import numpy as np

from src.beautify import ops


class OpsTest(unittest.TestCase):
    def test_adjust_brightness_contrast_clips_uint8_values(self):
        img = np.array([[[10, 20, 30], [240, 250, 255]]], dtype=np.uint8)

        out = ops.adjust_brightness_contrast(img, brightness=20, contrast=1.2)

        self.assertEqual(out.dtype, np.uint8)
        np.testing.assert_array_equal(out, np.array([[[32, 44, 56], [255, 255, 255]]], dtype=np.uint8))

    def test_crop_region_returns_requested_rectangle(self):
        img = np.arange(4 * 5 * 3, dtype=np.uint8).reshape(4, 5, 3)

        out = ops.crop_region(img, x=1, y=1, width=3, height=2)

        np.testing.assert_array_equal(out, img[1:3, 1:4])

    def test_measure_mask_reports_area_centroid_perimeter_and_shape_scores(self):
        mask = np.zeros((6, 6), dtype=np.uint8)
        mask[1:4, 2:5] = 255

        result = ops.measure_mask(mask)

        self.assertEqual(result["area"], 9)
        self.assertEqual(result["centroid"], (3.0, 2.0))
        self.assertGreater(result["perimeter"], 0)
        self.assertGreater(result["rectangularity"], 0.9)
        self.assertGreater(result["circularity"], 0)


if __name__ == "__main__":
    unittest.main()
