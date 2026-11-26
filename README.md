# Tessera

**A tiny, parametric tiling laboratory in pure Python.**

Tessera generates periodic and aperiodic geometric tilings as standalone SVG artwork. It uses only the Python standard library: no NumPy, no Matplotlib, no browser runtime, and no build step.

## Features

- **Periodic:** square grid, triangular tessellation, and regular hexagonal Voronoi tiling.
- **Aperiodic:** an eightfold cut-and-project point set, converted into a Voronoi tiling (an octagonal quasicrystal construction).
- **Composition:** stack multiple tiling layers, each with its own scale, rotation, offset, palette, stroke, and opacity.
- **Parametric:** edit a small JSON file to generate variations reproducibly.
- **Export:** clean, scalable SVG files that open in browsers, Inkscape, Illustrator, and most vector editors.
- **Automation:** run from the command line or import `render()` from another Python script.

## Requirements

Python 3.9 or newer. No third-party packages.

## Quick start

```bash
python tessera.py --preset quasi -o artwork.svg
```

Other presets:

```bash
python tessera.py --preset square -o square.svg
python tessera.py --preset triangular -o triangles.svg
python tessera.py --preset hexagonal -o hexagons.svg
python tessera.py --preset composition -o composition.svg
```

List presets:

```bash
python tessera.py --list-presets
```

## Make your own composition

Copy `examples/composition.json` and edit its parameters:

```bash
python tessera.py --config examples/composition.json -o my-tiling.svg
```

A configuration has a canvas and an ordered list of layers. Layers are drawn in order, so later layers appear on top.

```json
{
  "width": 1200,
  "height": 900,
  "background": "#f7f5ef",
  "palette": "earth",
  "seed": 17,
  "layers": [
    {
      "type": "hexagonal",
      "tile_size": 74,
      "rotation": 0,
      "fill": "none",
      "stroke": "#444444",
      "stroke_width": 1
    },
    {
      "type": "quasicrystal",
      "tile_size": 30,
      "extent": 7,
      "window": 1.3,
      "rotation": 11,
      "x": 0,
      "y": 0,
      "fill": "palette",
      "stroke": "#222222",
      "stroke_width": 0.7,
      "opacity": 0.92
    }
  ]
}
```

### Common layer parameters

| Parameter | Meaning |
|---|---|
| `type` | `square`, `triangular`, `hexagonal`, or `quasicrystal` |
| `tile_size` | Base spacing / scale of the tiling |
| `scale` | Additional layer scale multiplier |
| `rotation` | Rotation in degrees |
| `x`, `y` | Pixel offset from canvas center |
| `fill` | `palette`, `alternate`, `solid`, `random`, or `none` |
| `color` | Fill color when `fill` is `solid` |
| `stroke` | Polygon outline color |
| `stroke_width` | Outline width in SVG units |
| `opacity` | Layer opacity from 0 to 1 |

### Aperiodic parameters

The `quasicrystal` layer uses a four-dimensional integer lattice projected into physical space and filtered through an internal-space acceptance window.

| Parameter | Meaning |
|---|---|
| `extent` | Integer-lattice search radius; larger values can reveal more of the pattern |
| `window` | Acceptance-window half-width in internal space |
| `max_points` | Safety limit on the number of Voronoi sites (default 650) |

The resulting point set has octagonal (eightfold) symmetry and is not periodic. Its Voronoi dual produces a patch of polygonal cells. Increase `extent` if the patch looks sparse; increase `window` to admit more sites. Larger values cost more computation.

### Palettes

Built-in palettes: `mono`, `warm`, `cool`, `primary`, `earth`, `neon`.

You can also define your own:

```json
"custom_palette": ["#f2e8cf", "#a7c957", "#6a994e", "#386641"]
```

Fill modes:
- `palette`: cycle through the chosen palette.
- `alternate`: cycle through palette colors by tile.
- `solid`: use the layer's `color`.
- `random`: seeded random palette selection.
- `none`: transparent fill.

## Use as a Python module

```python
import json
from tessera import render

config = json.load(open("examples/quasi.json", encoding="utf-8"))
svg_text = render(config)

with open("output.svg", "w", encoding="utf-8") as f:
    f.write(svg_text)
```

You can generate a batch of artworks by varying a few parameters:

```python
import random
from tessera import preset, render

rng = random.Random(42)
for i in range(20):
    config = preset("quasi")
    layer = config["layers"][0]
    layer["rotation"] = rng.randrange(0, 360)
    layer["window"] = rng.uniform(0.9, 1.6)
    layer["tile_size"] = rng.randrange(24, 45)
    config["seed"] = i
    with open(f"variation-{i:02d}.svg", "w", encoding="utf-8") as f:
        f.write(render(config))
```

## Project structure

```text
tessera/
├── tessera.py
├── README.md
├── LICENSE
├── .gitignore
├── examples/
│   ├── square.json
│   ├── triangular.json
│   ├── hexagonal.json
│   ├── quasi.json
│   └── composition.json
└── tests/
    └── test_tessera.py
```

## Mathematical notes

- Square and triangular layers are regular periodic tessellations of the Euclidean plane.
- The hexagonal layer is the Voronoi tessellation of a triangular lattice.
- The aperiodic layer is based on an octagonal cut-and-project construction: integer points from `Z^4` are projected into a physical plane, while an acceptance condition in the complementary internal plane selects the point set. The Voronoi cells of those sites form the visible tiling patch.
- The cut-and-project layer is a finite window into an infinite quasiperiodic structure. It is not a Penrose rhomb tiling; it is an octagonal quasicrystal Voronoi tiling.

## Design philosophy

Tessera is intentionally small. It favors inspectable code, editable JSON, deterministic output, and vector graphics over a large UI or dependency stack.

## Ideas to extend

- Add Penrose rhomb deflation and substitution rules.
- Add Ammann–Beenker rhomb tiles as an explicit edge-to-edge tile set.
- Add SVG metadata for parameter provenance.
- Add a small gallery generator for parameter sweeps.
- Add color mappings based on tile geometry or local neighborhoods.

## License

MIT. See `LICENSE`.
