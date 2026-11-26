"""Shared geometry helpers."""
import math

def regular_polygon(sides, radius, rotation=0.0, center=(0.0, 0.0)):
    """Vertices of a regular n-gon, for any n >= 3."""
    if not 3 <= int(sides) <= 128:
        raise ValueError("sides must be between 3 and 128")
    cx, cy = center
    return [(cx + radius*math.cos(math.radians(rotation)+2*math.pi*i/sides),
             cy + radius*math.sin(math.radians(rotation)+2*math.pi*i/sides))
            for i in range(sides)]

def transform(points, center, scale=1.0, rotation=0.0, offset=(0.0, 0.0)):
    cx, cy = center
    ox, oy = offset
    a = math.radians(rotation)
    c, s = math.cos(a), math.sin(a)
    return [(cx+ox+scale*(x*c-y*s), cy+oy+scale*(x*s+y*c)) for x, y in points]

def clip_halfplane(poly, a, b, c, eps=1e-9):
    """Sutherland-Hodgman clipping against a*x + b*y <= c."""
    if not poly:
        return []
    out, prev = [], poly[-1]
    prev_in = a*prev[0]+b*prev[1] <= c+eps
    for cur in poly:
        cur_in = a*cur[0]+b*cur[1] <= c+eps
        if cur_in != prev_in:
            dx, dy = cur[0]-prev[0], cur[1]-prev[1]
            den = a*dx+b*dy
            if abs(den) > eps:
                t = (c-a*prev[0]-b*prev[1])/den
                out.append((prev[0]+t*dx, prev[1]+t*dy))
        if cur_in:
            out.append(cur)
        prev, prev_in = cur, cur_in
    return out
