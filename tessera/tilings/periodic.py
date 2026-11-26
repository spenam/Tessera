"""Periodic lattices and arbitrary regular-polygon motif fields."""
import math
from ..geometry import regular_polygon

def square(width, height, size, **_):
    cols, rows = math.ceil(width/size)+3, math.ceil(height/size)+3
    return [[(i*size,j*size),((i+1)*size,j*size),
             ((i+1)*size,(j+1)*size),(i*size,(j+1)*size)]
            for j in range(-rows//2,rows//2+1)
            for i in range(-cols//2,cols//2+1)]

def triangular(width, height, size, **_):
    h=size*math.sqrt(3)/2
    cols,rows=math.ceil(width/size)+5,math.ceil(height/h)+5
    cells=[]
    for j in range(-rows//2,rows//2+1):
        for i in range(-cols//2,cols//2+1):
            x,y=i*size+(j%2)*size/2,j*h
            cells.extend([[(x,y),(x+size,y),(x+size/2,y+h)],
                          [(x+size/2,y-h),(x+size,y),(x+size/2,y+h)]])
    return cells

def hexagonal(width, height, size, **_):
    radius,h=size/math.sqrt(3),size*math.sqrt(3)/2
    cols,rows=math.ceil(width/size)+5,math.ceil(height/h)+5
    cells=[]
    for j in range(-rows//2,rows//2+1):
        for i in range(-cols//2,cols//2+1):
            x,y=i*size+(j%2)*size/2,j*h
            cells.append([(x+radius*math.cos(math.radians(30+60*k)),
                           y+radius*math.sin(math.radians(30+60*k))) for k in range(6)])
    return cells

def polygon_field(width, height, size, sides=5, arrangement="square",
                  polygon_rotation=0, **_):
    """Regular n-gon motifs on a simple point layout.

    This is an exploratory motif field, not an edge-to-edge plane tiling.
    Use the ``uniform`` generator for mathematically constrained mixed-polygon
    tilings made from regular triangles, squares, hexagons, octagons and dodecagons.
    """
    sides = int(sides)
    if not 3 <= sides <= 128:
        raise ValueError("sides must be between 3 and 128")
    if arrangement not in {"square", "triangular"}:
        raise ValueError("arrangement must be 'square' or 'triangular'")
    row_step = size if arrangement == "square" else size * math.sqrt(3) / 2
    cols, rows = math.ceil(width / size) + 4, math.ceil(height / row_step) + 4
    cells = []
    for j in range(-rows // 2, rows // 2 + 1):
        for i in range(-cols // 2, cols // 2 + 1):
            center = (i * size + ((j % 2) * size / 2 if arrangement == "triangular" else 0),
                      j * row_step)
            parent = regular_polygon(sides, size * 0.48, polygon_rotation, center)
            cells.append(parent)
    return cells
