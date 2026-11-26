import math
import unittest

from tessera import preset, render, uniform_catalogue, uniform_counts, known_uniform_counts, generate_uniform
from tessera.geometry import regular_polygon
from tessera.tilings.periodic import polygon_field


class TesseraTests(unittest.TestCase):
    def test_any_polygon_side_count(self):
        for n in (3, 4, 5, 7, 11, 32, 128):
            self.assertEqual(len(regular_polygon(n, 10)), n)

    def test_periodic_presets(self):
        for name in ("square", "triangular", "hexagonal"):
            self.assertIn("</svg>", render(preset(name)))

    def test_polygon_field_preserves_regular_odd_polygons(self):
        cells = polygon_field(1, 1, 100, sides=11, arrangement="square")
        self.assertTrue(cells)
        self.assertTrue(all(len(cell) == 11 for cell in cells))

    def test_quasicrystal(self):
        config = preset("quasi")
        config["width"] = config["height"] = 300
        config["layers"][0].update(extent=5, max_points=150)
        self.assertIn("<polygon", render(config))

    def test_invalid_sides(self):
        config = preset("polygon")
        config["layers"][0]["sides"] = 2
        with self.assertRaises(ValueError):
            render(config)

    def test_mixed_hexagon_square_triangle_tiling(self):
        cells = generate_uniform("6-4-3/m30/r(c2)", 420, 420, 42, 6)
        self.assertTrue(cells)
        self.assertEqual(set(map(len, cells)), {3, 4, 6})

    def test_octagon_square_tiling(self):
        cells = generate_uniform("8-4/m90/r(h4)", 420, 420, 42, 6)
        self.assertTrue(cells)
        self.assertEqual(set(map(len, cells)), {4, 8})

    def test_k4_reference_tiling(self):
        entry = next(x for x in uniform_catalogue(4) if x["k"] == 4)
        cells = generate_uniform(entry["notation"], 420, 420, 42, 7)
        self.assertTrue(cells)
        self.assertEqual(set(map(len, cells)), {3, 6})

    def test_equal_edge_length_and_regular_polygons(self):
        cells = generate_uniform("6-4-3/m30/r(c2)", 300, 300, 36, 4)
        lengths = []
        for cell in cells:
            side_lengths = [math.dist(cell[i], cell[(i + 1) % len(cell)]) for i in range(len(cell))]
            lengths.extend(side_lengths)
            self.assertLess(max(side_lengths) - min(side_lengths), 1e-6)
        common = lengths[0]
        self.assertTrue(all(abs(length - common) < 1e-6 for length in lengths))

    def test_all_starter_catalogue_entries_generate(self):
        for entry in uniform_catalogue(4):
            with self.subTest(tiling_id=entry["id"]):
                cells = generate_uniform(entry["notation"], 260, 260, 30, 2)
                self.assertTrue(cells)

    def test_catalogue_explores_through_k4(self):
        counts = uniform_counts()
        self.assertEqual(counts[1], 11)
        self.assertEqual(counts[2], 4)
        self.assertEqual(counts[3], 3)
        self.assertEqual(counts[4], 1)
        self.assertEqual(max(item["k"] for item in uniform_catalogue(4)), 4)
        self.assertEqual(known_uniform_counts(), {1: 11, 2: 20, 3: 61, 4: 151})

    def test_invalid_repeat_count(self):
        with self.assertRaises(ValueError):
            generate_uniform("6-4-3/m30/r(c2)", 300, 300, 36, -1)

    def test_uniform_preset_renders(self):
        self.assertIn("</svg>", render(preset("mixed-hexagon")))
        self.assertIn("</svg>", render(preset("four-uniform")))


if __name__ == "__main__":
    unittest.main()
