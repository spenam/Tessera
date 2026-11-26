#!/usr/bin/env python3
"""Tessera: a dependency-free generative tiling studio.

Supports periodic square/triangular/hexagonal tilings and an octagonal
cut-and-project quasicrystal rendered as a Voronoi tiling.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import random
from pathlib import Path
from typing import Iterable

PALETTES = {
    "mono": ["#f2efe8", "#c9c4b8", "#89877f", "#41413f", "#171717"],
    "warm": ["#f4d6a0", "#e9a15b", "#d66b4a", "#8e3b46", "#4c344d"],
    "cool": ["#d9f0ed", "#8bc8c4", "#4f91a5", "#46618a", "#30334f"],
    "primary": ["#f4d35e", "#ee964b", "#f95738", "#0d3b66", "#faf0ca"],
    "earth": ["#e6d5b8", "#b7a184", "#7f8b6d", "#52634a", "#443c32"],
    "neon": ["#f72585", "#b5179e", "#7209b7", "#4361ee", "#4cc9f0"],
}

DEFAULT_CONFIG = {
    "width": 1000,
    "height": 1000,
    "background": "#f7f5ef",
    "palette": "mono",
    "seed": 12,
    "layers": [
        {
            "type": "quasicrystal",
            "tile_size": 36,
            "order": 8,
            "window": 1.35,
            "extent": 7,
            "rotation": 0,
            "x": 0,
            "y": 0,
            "stroke": "#252525",
            "stroke_width": 0.8,
            "fill": "palette",
            "opacity": 1.0,
        }
    ],
}


def _fmt(value: float) -> str:
    return f"{value:.3f}".rstrip("0").rstrip(".")


def _transform(point, cx, cy, scale, angle, ox, oy):
    x, y = point
    a = math.radians(angle)
    c, s = math.cos(a), math.sin(a)
    return (cx + ox + scale * (x * c - y * s),
            cy + oy + scale * (x * s + y * c))


def _palette_color(layer, index, rng, palette):
    mode = layer.get("fill", "palette")
    if mode == "none":
        return "none"
    if mode == "solid":
        return layer.get("color", palette[0])
    if mode == "random":
        return rng.choice(palette)
    if mode == "alternate":
        return palette[index % len(palette)]
    return palette[(index * int(layer.get("color_step", 1))) % len(palette)]


def _polygon(points, fill, stroke, stroke_width, opacity=1.0):
    pts = " ".join(f"{_fmt(x)},{_fmt(y)}" for x, y in points)
    return (f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="{_fmt(stroke_width)}" opacity="{_fmt(opacity)}" '
            f'stroke-linejoin="round"/>')


def _square_layer(layer, width, height, rng, palette):
    size = float(layer.get("tile_size", 40))
    cols = math.ceil(width / size) + 3
    rows = math.ceil(height / size) + 3
    angle = float(layer.get("rotation", 0))
    scale = float(layer.get("scale", 1))
    ox, oy = float(layer.get("x", 0)), float(layer.get("y", 0))
    cx, cy = width / 2, height / 2
    result = []
    idx = 0
    for j in range(-rows // 2, rows // 2 + 1):
        for i in range(-cols // 2, cols // 2 + 1):
            x0, y0 = i * size, j * size
            raw = [(x0, y0), (x0 + size, y0),
                   (x0 + size, y0 + size), (x0, y0 + size)]
            pts = [_transform(p, cx, cy, scale, angle, ox, oy) for p in raw]
            fill = _palette_color(layer, idx, rng, palette)
            result.append(_polygon(pts, fill, layer.get("stroke", "#222"),
                                   float(layer.get("stroke_width", 1)), float(layer.get("opacity", 1))))
            idx += 1
    return result


def _triangular_layer(layer, width, height, rng, palette):
    size = float(layer.get("tile_size", 42))
    h = size * math.sqrt(3) / 2
    cols = math.ceil(width / size) + 5
    rows = math.ceil(height / h) + 5
    angle = float(layer.get("rotation", 0))
    scale = float(layer.get("scale", 1))
    ox, oy = float(layer.get("x", 0)), float(layer.get("y", 0))
    cx, cy = width / 2, height / 2
    result = []
    idx = 0
    for j in range(-rows // 2, rows // 2 + 1):
        for i in range(-cols // 2, cols // 2 + 1):
            x, y = i * size + (j % 2) * size / 2, j * h
            triangles = [
                [(x, y), (x + size, y), (x + size / 2, y + h)],
                [(x + size / 2, y - h), (x + size, y), (x + size / 2, y + h)],
            ]
            for tri in triangles:
                pts = [_transform(p, cx, cy, scale, angle, ox, oy) for p in tri]
                fill = _palette_color(layer, idx, rng, palette)
                result.append(_polygon(pts, fill, layer.get("stroke", "#222"),
                                       float(layer.get("stroke_width", 0.8)), float(layer.get("opacity", 1))))
                idx += 1
    return result


def _hex_layer(layer, width, height, rng, palette):
    """Voronoi cells of a triangular lattice: a regular hexagonal tiling."""
    d = float(layer.get("tile_size", 48))
    radius = d / math.sqrt(3)
    h = d * math.sqrt(3) / 2
    cols = math.ceil(width / d) + 5
    rows = math.ceil(height / h) + 5
    angle = float(layer.get("rotation", 0))
    scale = float(layer.get("scale", 1))
    ox, oy = float(layer.get("x", 0)), float(layer.get("y", 0))
    cx, cy = width / 2, height / 2
    result = []
    idx = 0
    for j in range(-rows // 2, rows // 2 + 1):
        for i in range(-cols // 2, cols // 2 + 1):
            x, y = i * d + (j % 2) * d / 2, j * h
            raw = [(x + radius * math.cos(math.radians(30 + k * 60)),
                    y + radius * math.sin(math.radians(30 + k * 60))) for k in range(6)]
            pts = [_transform(p, cx, cy, scale, angle, ox, oy) for p in raw]
            fill = _palette_color(layer, idx, rng, palette)
            result.append(_polygon(pts, fill, layer.get("stroke", "#222"),
                                   float(layer.get("stroke_width", 1)), float(layer.get("opacity", 1))))
            idx += 1
    return result


def _clip_halfplane(poly, a, b, c, eps=1e-9):
    """Clip polygon to a*x + b*y <= c (Sutherland-Hodgman)."""
    if not poly:
        return []
    out = []
    prev = poly[-1]
    prev_in = a * prev[0] + b * prev[1] <= c + eps
    for cur in poly:
        cur_in = a * cur[0] + b * cur[1] <= c + eps
        if cur_in != prev_in:
            dx, dy = cur[0] - prev[0], cur[1] - prev[1]
            denom = a * dx + b * dy
            if abs(denom) > eps:
                t = (c - a * prev[0] - b * prev[1]) / denom
                out.append((prev[0] + t * dx, prev[1] + t * dy))
        if cur_in:
            out.append(cur)
        prev, prev_in = cur, cur_in
    return out


def _octagonal_cut_project(extent, window):
    """Project accepted points of Z^4 into R^2 using an octagonal window."""
    physical = []
    internal = []
    for k in range(4):
        theta = k * math.pi / 4
        physical.append((math.cos(theta), math.sin(theta)))
        # Orthogonal complement to the physical 2D projection.
        internal.append((math.cos(3 * theta), math.sin(3 * theta)))
    points = []
    seen = set()
    for ns in itertools.product(range(-extent, extent + 1), repeat=4):
        u = sum(n * v[0] for n, v in zip(ns, internal))
        v = sum(n * vec[1] for n, vec in zip(ns, internal))
        if abs(u) > window or abs(v) > window:
            continue
        x = sum(n * vec[0] for n, vec in zip(ns, physical))
        y = sum(n * vec[1] for n, vec in zip(ns, physical))
        key = (round(x, 7), round(y, 7))
        if key not in seen:
            seen.add(key)
            points.append((x, y))
    return points


def _quasicrystal_layer(layer, width, height, rng, palette):
    """Voronoi dual of an eightfold cut-and-project point set."""
    extent = int(layer.get("extent", 6))
    window = float(layer.get("window", 1.25))
    tile_size = float(layer.get("tile_size", 34))
    points = _octagonal_cut_project(extent, window)
    # Keep only sites near the visible region, but retain a generous margin.
    radius = math.hypot(width, height) / (2 * tile_size) + 3
    points = [(x, y) for x, y in points if math.hypot(x, y) <= radius]
    if len(points) > int(layer.get("max_points", 650)):
        points = sorted(points, key=lambda p: p[0] * p[0] + p[1] * p[1])[:int(layer.get("max_points", 650))]
    if len(points) < 4:
        raise ValueError("Not enough quasicrystal sites; increase 'extent' or 'window'.")

    angle = float(layer.get("rotation", 0))
    scale = tile_size * float(layer.get("scale", 1))
    ox, oy = float(layer.get("x", 0)), float(layer.get("y", 0))
    cx, cy = width / 2, height / 2
    sites = [_transform((x, y), cx, cy, scale, angle, ox, oy) for x, y in points]
    bounds = [(-width, -height), (2 * width, -height),
              (2 * width, 2 * height), (-width, 2 * height)]
    result = []
    order = sorted(range(len(sites)), key=lambda i: sites[i][0] ** 2 + sites[i][1] ** 2)
    for idx in order:
        px, py = sites[idx]
        cell = list(bounds)
        for j, (qx, qy) in enumerate(sites):
            if idx == j:
                continue
            # |X-P|^2 <= |X-Q|^2
            a, b = 2 * (qx - px), 2 * (qy - py)
            c = qx * qx + qy * qy - px * px - py * py
            cell = _clip_halfplane(cell, a, b, c)
            if not cell:
                break
        if len(cell) >= 3:
            local_index = len(result)
            fill = _palette_color(layer, local_index, rng, palette)
            result.append(_polygon(cell, fill, layer.get("stroke", "#222"),
                                   float(layer.get("stroke_width", 0.7)), float(layer.get("opacity", 1))))
    return result


def render(config: dict) -> str:
    """Render a configuration dictionary to a standalone SVG string."""
    width, height = int(config.get("width", 1000)), int(config.get("height", 1000))
    if width <= 0 or height <= 0:
        raise ValueError("Canvas width and height must be positive.")
    palette_name = config.get("palette", "mono")
    palette = config.get("custom_palette") or PALETTES.get(palette_name)
    if not palette:
        raise ValueError(f"Unknown palette: {palette_name}")
    rng = random.Random(config.get("seed", 0))
    chunks = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<rect width="100%" height="100%" fill="{config.get("background", "#ffffff")}"/>'
    ]
    renderers = {
        "square": _square_layer,
        "triangular": _triangular_layer,
        "hexagonal": _hex_layer,
        "quasicrystal": _quasicrystal_layer,
    }
    for layer in config.get("layers", []):
        kind = layer.get("type")
        if kind not in renderers:
            raise ValueError(f"Unknown tiling type: {kind}. Choose from {', '.join(renderers)}.")
        chunks.extend(renderers[kind](layer, width, height, rng, palette))
    chunks.append("</svg>")
    return "\n".join(chunks)


def preset(name: str) -> dict:
    presets = {
        "square": {"width": 1000, "height": 1000, "background": "#f7f5ef", "palette": "mono",
                   "seed": 3, "layers": [{"type": "square", "tile_size": 55, "rotation": 0,
                   "fill": "alternate", "stroke": "#333333", "stroke_width": 1}]},
        "triangular": {"width": 1000, "height": 1000, "background": "#151515", "palette": "neon",
                       "seed": 8, "layers": [{"type": "triangular", "tile_size": 62, "rotation": 0,
                       "fill": "palette", "stroke": "#151515", "stroke_width": 1.5}]},
        "hexagonal": {"width": 1000, "height": 1000, "background": "#f4f0e8", "palette": "warm",
                      "seed": 2, "layers": [{"type": "hexagonal", "tile_size": 76, "rotation": 0,
                      "fill": "palette", "stroke": "#493b35", "stroke_width": 1.2}]},
        "quasi": DEFAULT_CONFIG,
        "composition": {"width": 1000, "height": 1000, "background": "#101820", "palette": "cool",
                        "seed": 22, "layers": [
                            {"type": "hexagonal", "tile_size": 92, "rotation": 15, "scale": 1.0,
                             "fill": "none", "stroke": "#6aa6a1", "stroke_width": 1.1, "opacity": 0.8},
                            {"type": "quasicrystal", "tile_size": 31, "extent": 7, "window": 1.3,
                             "rotation": 0, "fill": "alternate", "stroke": "#d9f0ed",
                             "stroke_width": 0.65, "opacity": 0.9}
                        ]}
    }
    if name not in presets:
        raise ValueError(f"Unknown preset '{name}'. Available: {', '.join(presets)}")
    return json.loads(json.dumps(presets[name]))


def main():
    parser = argparse.ArgumentParser(description="Tessera — minimal generative tiling studio")
    parser.add_argument("--preset", choices=["square", "triangular", "hexagonal", "quasi", "composition"],
                        help="render a built-in example")
    parser.add_argument("--config", help="path to a JSON configuration file")
    parser.add_argument("-o", "--output", default="artwork.svg", help="output SVG path (default: artwork.svg)")
    parser.add_argument("--list-presets", action="store_true", help="list built-in presets")
    args = parser.parse_args()
    if args.list_presets:
        print("square, triangular, hexagonal, quasi, composition")
        return
    if args.config and args.preset:
        parser.error("Use either --config or --preset, not both.")
    if args.config:
        config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    else:
        config = preset(args.preset or "quasi")
    svg = render(config)
    Path(args.output).write_text(svg, encoding="utf-8")
    print(f"Saved {args.output}")


if __name__ == "__main__":
    main()
