"""SVG renderer. Algorithms return polygons; this module styles and serializes."""
import random
from .geometry import transform
from .style import PALETTES,color_for
from .tilings import periodic,aperiodic,uniform

def _uniform(width, height, size, notation, max_repeat=6, **_):
    return uniform.generate_uniform(notation, width, height, size, max_repeat=max_repeat)


GENERATORS={"square":periodic.square,"triangular":periodic.triangular,
            "hexagonal":periodic.hexagonal,"polygon":periodic.polygon_field,
            "quasicrystal":aperiodic.quasicrystal,"uniform":_uniform}

def _fmt(x): return f"{x:.3f}".rstrip("0").rstrip(".")

def _svg_polygon(points,fill,stroke,stroke_width,opacity):
    coords=" ".join(f"{_fmt(x)},{_fmt(y)}" for x,y in points)
    return (f'<polygon points="{coords}" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="{_fmt(stroke_width)}" opacity="{_fmt(opacity)}" '
            'stroke-linejoin="round"/>')

def render(config):
    width,height=int(config.get("width",1000)),int(config.get("height",1000))
    if width<=0 or height<=0: raise ValueError("Canvas dimensions must be positive.")
    palette=config.get("custom_palette") or PALETTES.get(config.get("palette","mono"))
    if not palette: raise ValueError("Unknown palette.")
    rng=random.Random(config.get("seed",0))
    out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
         f'<rect width="100%" height="100%" fill="{config.get("background","#fff")}"/>']
    style_keys={"type","tile_size","rotation","scale","x","y","stroke","stroke_width",
                "fill","color","color_step","opacity"}
    for layer in config.get("layers",[]):
        kind=layer.get("type")
        if kind not in GENERATORS:
            raise ValueError(f"Unknown layer {kind!r}; choose {', '.join(GENERATORS)}")
        size=float(layer.get("tile_size",40))
        if size<=0: raise ValueError("tile_size must be positive.")
        polygons=GENERATORS[kind](width,height,size,
            **{k:v for k,v in layer.items() if k not in style_keys})
        for index,poly in enumerate(polygons):
            pts=transform(poly,(width/2,height/2),float(layer.get("scale",1)),
                          float(layer.get("rotation",0)),
                          (float(layer.get("x",0)),float(layer.get("y",0))))
            out.append(_svg_polygon(pts,color_for(layer,index,rng,palette),
                layer.get("stroke","#222"),float(layer.get("stroke_width",1)),
                float(layer.get("opacity",1))))
    out.append("</svg>")
    return "\n".join(out)
