import unittest
from tessera import preset, render


class TesseraTests(unittest.TestCase):
    def test_periodic_presets_render_svg(self):
        for name in ("square", "triangular", "hexagonal"):
            svg = render(preset(name))
            self.assertIn("<svg", svg)
            self.assertIn("</svg>", svg)
            self.assertIn("<polygon", svg)

    def test_quasicrystal_renders_svg(self):
        config = preset("quasi")
        config["width"] = 320
        config["height"] = 320
        config["layers"][0]["extent"] = 5
        config["layers"][0]["max_points"] = 180
        svg = render(config)
        self.assertIn("<svg", svg)
        self.assertIn("<polygon", svg)

    def test_unknown_tiling_fails(self):
        with self.assertRaises(ValueError):
            render({"layers": [{"type": "not-a-tiling"}]})


if __name__ == "__main__":
    unittest.main()
