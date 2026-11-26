"""Octagonal cut-and-project sites and their Voronoi polygon patch."""
import itertools, math
from ..geometry import clip_halfplane

def octagonal_cut_project(extent=7, window=1.35):
    physical, internal=[],[]
    for k in range(4):
        t=k*math.pi/4
        physical.append((math.cos(t),math.sin(t)))
        internal.append((math.cos(3*t),math.sin(3*t)))
    points,seen=[],set()
    for ns in itertools.product(range(-extent,extent+1),repeat=4):
        u=sum(n*v[0] for n,v in zip(ns,internal))
        v=sum(n*q[1] for n,q in zip(ns,internal))
        if abs(u)>window or abs(v)>window: continue
        x=sum(n*q[0] for n,q in zip(ns,physical))
        y=sum(n*q[1] for n,q in zip(ns,physical))
        key=(round(x,7),round(y,7))
        if key not in seen:
            seen.add(key); points.append((x,y))
    return points

def voronoi_cells(sites,bounds):
    cells=[]
    for i,(px,py) in enumerate(sites):
        cell=list(bounds)
        for j,(qx,qy) in enumerate(sites):
            if i==j: continue
            a,b=2*(qx-px),2*(qy-py)
            c=qx*qx+qy*qy-px*px-py*py
            cell=clip_halfplane(cell,a,b,c)
            if not cell: break
        if len(cell)>=3: cells.append(cell)
    return cells

def quasicrystal(width,height,size,extent=7,window=1.35,max_points=650,**_):
    pts=octagonal_cut_project(int(extent),float(window))
    radius=math.hypot(width,height)/(2*size)+3
    pts=[p for p in pts if math.hypot(*p)<=radius]
    pts.sort(key=lambda p:p[0]**2+p[1]**2)
    pts=pts[:int(max_points)]
    if len(pts)<4: raise ValueError("Too few sites; increase extent or window.")
    sites=[(width/2+x*size,height/2+y*size) for x,y in pts]
    bounds=[(-width,-height),(2*width,-height),(2*width,2*height),(-width,2*height)]
    return voronoi_cells(sites,bounds)
