"""Built-in starter configurations."""
from copy import deepcopy
PRESETS={
"square":{"width":1000,"height":1000,"background":"#f7f5ef","palette":"mono","seed":3,
 "layers":[{"type":"square","tile_size":55,"fill":"alternate","stroke":"#333","stroke_width":1}]},
"triangular":{"width":1000,"height":1000,"background":"#151515","palette":"neon","seed":8,
 "layers":[{"type":"triangular","tile_size":62,"fill":"palette","stroke":"#151515","stroke_width":1.5}]},
"hexagonal":{"width":1000,"height":1000,"background":"#f4f0e8","palette":"warm","seed":2,
 "layers":[{"type":"hexagonal","tile_size":76,"fill":"palette","stroke":"#493b35","stroke_width":1.2}]},
"quasi":{"width":1000,"height":1000,"background":"#f7f5ef","palette":"cool","seed":12,
 "layers":[{"type":"quasicrystal","tile_size":36,"extent":7,"window":1.35,
 "fill":"palette","stroke":"#252525","stroke_width":0.8}]},
"polygon":{"width":1000,"height":1000,"background":"#f7f5ef","palette":"warm","seed":42,
 "layers":[{"type":"polygon","sides":7,"arrangement":"triangular","tile_size":62,
 "polygon_rotation":15,"fill":"alternate","stroke":"#493b35","stroke_width":1}]},
"composition":{"width":1000,"height":1000,"background":"#101820","palette":"cool","seed":22,
 "layers":[{"type":"hexagonal","tile_size":92,"rotation":15,"fill":"none",
 "stroke":"#6aa6a1","stroke_width":1.1,"opacity":0.8},
 {"type":"polygon","sides":9,"arrangement":"triangular","tile_size":65,
 "polygon_rotation":10,"fill":"alternate","stroke":"#d9f0ed","stroke_width":0.65,"opacity":0.9}]},
"mixed-hexagon":{"width":1000,"height":1000,"background":"#f7f5ef","palette":"cool","seed":7,
 "layers":[{"type":"uniform","notation":"6-4-3/m30/r(c2)","tile_size":70,"max_repeat":12,
 "fill":"palette","stroke":"#283746","stroke_width":0.9}]},
"four-uniform":{"width":1000,"height":1000,"background":"#f7f5ef","palette":"warm","seed":4,
 "layers":[{"type":"uniform","notation":"6-3-3-3/m90/r(h2)","tile_size":70,"max_repeat":12,
 "fill":"palette","stroke":"#493b35","stroke_width":0.9}]}
}
def preset(name):
    if name not in PRESETS: raise ValueError(f"Unknown preset {name!r}: {', '.join(PRESETS)}")
    return deepcopy(PRESETS[name])
