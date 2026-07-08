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

    def test_compare_side_by_side_pads_images_to_same_height(self):
        left = np.zeros((2, 3, 3), dtype=np.uint8)
        right = np.ones((4, 2, 3), dtype=np.uint8) * 255

        out = ops.compare_side_by_side(left, right)

        self.assertEqual(out.shape, (4, 6, 3))
        np.testing.assert_array_equal(out[:2, :3], left)

    def test_edit_mask_adds_and_removes_rectangles(self):
        mask = np.zeros((5, 5), dtype=np.uint8)

        added = ops.edit_mask_rect(mask, (1, 1, 3, 2), add=True)
        removed = ops.edit_mask_rect(added, (2, 1, 1, 2), add=False)

        self.assertEqual(int(added.sum() / 255), 6)
        self.assertEqual(int(removed.sum() / 255), 4)

    def test_histogram_image_returns_rgb_visualization(self):
        img = np.array([[0, 255], [128, 128]], dtype=np.uint8)

        out = ops.histogram_image(img, width=256, height=100)

        self.assertEqual(out.shape, (100, 256, 3))
        self.assertEqual(out.dtype, np.uint8)


if __name__ == "__main__":
    unittest.main()
