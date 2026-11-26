"""Command line interface."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .catalogue import uniform_by_id, uniform_catalogue, uniform_counts, known_uniform_counts
from .presets import PRESETS, preset
from .render import render


def _list_uniform(max_k: int) -> None:
    rows = uniform_catalogue(max_k)
    print(f"Starter catalogue: {len(rows)} reference constructions (k <= {max_k})")
    counts = uniform_counts()
    print("Available locally: " + ", ".join(f"k={k}: {counts[k]} / {known_uniform_counts()[k]} known" for k in range(1, max_k + 1)))
    print()
    for item in rows:
        print(f"{item['id']:7} k={item['k']}  {item['vertex']:<35}  {item['name']}")
        print(f"         {item['notation']}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Tessera — regular-polygon tiling explorer (periodic, aperiodic and k-uniform)"
    )
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--preset", choices=sorted(PRESETS))
    source.add_argument("--config", help="JSON configuration file")
    source.add_argument("--uniform", metavar="ID", help="render a catalogue entry, e.g. u07 or u4-01")
    source.add_argument("--notation", help="render a custom GomJau-Hogg notation")
    parser.add_argument("-o", "--output", default="artwork.svg")
    parser.add_argument("--list-presets", action="store_true")
    parser.add_argument("--list-uniform", action="store_true", help="list reference k-uniform constructions")
    parser.add_argument("--max-k", type=int, default=4, help="maximum k for --list-uniform (1–4)")
    parser.add_argument("--width", type=int, default=1000, help="canvas width for --uniform/--notation")
    parser.add_argument("--height", type=int, default=1000, help="canvas height for --uniform/--notation")
    parser.add_argument("--tile-size", type=float, default=70, help="common polygon edge length")
    parser.add_argument("--max-repeat", type=int, default=6, help="symmetry expansion iterations")
    args = parser.parse_args()

    if args.list_presets:
        print(", ".join(sorted(PRESETS)))
        return
    if args.list_uniform:
        if not 1 <= args.max_k <= 4:
            parser.error("--max-k must be between 1 and 4")
        _list_uniform(args.max_k)
        return

    if args.uniform or args.notation:
        if args.width <= 0 or args.height <= 0 or args.tile_size <= 0 or args.max_repeat < 0:
            parser.error("canvas dimensions and tile size must be positive; max-repeat cannot be negative")
        item = uniform_by_id(args.uniform) if args.uniform else None
        notation = item["notation"] if item else args.notation
        config = {
            "width": args.width,
            "height": args.height,
            "background": "#f7f5ef",
            "palette": "cool",
            "seed": 7,
            "layers": [{
                "type": "uniform",
                "notation": notation,
                "tile_size": args.tile_size,
                "max_repeat": args.max_repeat,
                "fill": "palette",
                "stroke": "#283746",
                "stroke_width": 0.9,
            }],
        }
    elif args.config:
        config = json.loads(Path(args.config).read_text(encoding="utf8"))
    else:
        config = preset(args.preset or "quasi")

    Path(args.output).write_text(render(config), encoding="utf8")
    label = f"{args.uniform} ({item['name']})" if args.uniform else ("custom notation" if args.notation else "configuration")
    print(f"Saved {args.output} from {label}")
