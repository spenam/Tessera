"""Palettes and fill selection."""
import random
PALETTES = {
 "mono":["#f2efe8","#c9c4b8","#89877f","#41413f","#171717"],
 "warm":["#f4d6a0","#e9a15b","#d66b4a","#8e3b46","#4c344d"],
 "cool":["#d9f0ed","#8bc8c4","#4f91a5","#46618a","#30334f"],
 "primary":["#f4d35e","#ee964b","#f95738","#0d3b66","#faf0ca"],
 "earth":["#e6d5b8","#b7a184","#7f8b6d","#52634a","#443c32"],
 "neon":["#f72585","#b5179e","#7209b7","#4361ee","#4cc9f0"]
}
def color_for(layer, index, rng, palette):
    mode = layer.get("fill", "palette")
    if mode == "none": return "none"
    if mode == "solid": return layer.get("color", palette[0])
    if mode == "random": return rng.choice(palette)
    if mode == "alternate": return palette[index % len(palette)]
    return palette[(index*int(layer.get("color_step", 1))) % len(palette)]
