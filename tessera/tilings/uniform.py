"""Edge-to-edge regular-polygon tilings generated from GomJau-Hogg notation.

The notation/placement model follows the freely published ANTWERP project by
Harry Hogg (MIT), and Gomez-Jauregui et al., Symmetry 13 (2021), 2376.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Iterable

Point = tuple[float, float]
Polygon = list[Point]
TAU = math.tau
SUPPORTED = {3, 4, 6, 8, 12}


def _angle(x: float, y: float) -> float:
    """ANTWERP-compatible polar angle range, approximately [-90°, 270°)."""
    a = math.atan2(y, x)
    if -1e-3 < a < 1e-3:
        return 0.0
    if a < -math.pi / 2 - 1e-3:
        return a + TAU
    return a


def _dist(a: Point, b: Point) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def _mean(points: Polygon) -> Point:
    return (sum(p[0] for p in points) / len(points),
            sum(p[1] for p in points) / len(points))


def _rotate_point(p: Point, angle: float, origin: Point = (0.0, 0.0)) -> Point:
    x, y = p[0] - origin[0], p[1] - origin[1]
    c, s = math.cos(angle), math.sin(angle)
    return (origin[0] + c*x - s*y, origin[1] + s*x + c*y)


def _reflect_point(p: Point, a: Point, b: Point) -> Point:
    dx, dy = b[0] - a[0], b[1] - a[1]
    den = dx*dx + dy*dy
    if den < 1e-18:
        raise ValueError("Reflection axis has zero length")
    t = ((p[0]-a[0])*dx + (p[1]-a[1])*dy) / den
    qx, qy = a[0] + t*dx, a[1] + t*dy
    return (2*qx-p[0], 2*qy-p[1])


@dataclass
class Edge:
    a: Point
    b: Point
    connected: bool = False

    @property
    def midpoint(self) -> Point:
        return ((self.a[0]+self.b[0])/2, (self.a[1]+self.b[1])/2)

    @property
    def angle(self) -> float:
        # For a half-edge transform point, ANTWERP uses the edge direction,
        # not the polar angle of the edge midpoint.
        return _angle(self.b[0] - self.a[0], self.b[1] - self.a[1])

    @property
    def radial_angle(self) -> float:
        mx, my = self.midpoint
        return _angle(mx, my)

    @property
    def length(self) -> float:
        return _dist(self.a, self.b)

    @property
    def max_radius(self) -> float:
        return max(math.hypot(*self.a), math.hypot(*self.b))

    @property
    def min_radius(self) -> float:
        return min(math.hypot(*self.a), math.hypot(*self.b))


class Patch:
    """Mutable set of polygon tiles and their boundary edges."""
    def __init__(self, polygons: Iterable[Polygon] = (), tol: float = 1e-5):
        self.polygons: list[Polygon] = []
        self.edges: list[Edge] = []
        self.tol = tol
        self.disconnected_max: float | None = None
        self.disconnected_min: float | None = None
        self._centers: set[tuple[int, int]] = set()
        self._center_scale = 1.0 / max(tol, 1e-12)
        for poly in polygons:
            self.add(poly)

    def clone(self) -> "Patch":
        return Patch([[tuple(p) for p in poly] for poly in self.polygons], self.tol)

    def add(self, polygon: Polygon) -> None:
        center = _mean(polygon)
        key = (round(center[0] * self._center_scale),
               round(center[1] * self._center_scale))
        if key in self._centers:
            return
        self._centers.add(key)
        poly = [tuple(p) for p in polygon]
        self.polygons.append(poly)
        self.edges.extend(Edge(poly[i], poly[(i+1) % len(poly)]) for i in range(len(poly)))

    def edges_for_polygons(self, polygons: Iterable[Polygon]) -> list[Edge]:
        wanted = {(poly[i], poly[(i+1) % len(poly)])
                  for poly in polygons for i in range(len(poly))}
        return [edge for edge in self.edges if (edge.a, edge.b) in wanted]

    def sorted_edges(self, polygons: Iterable[Polygon] | None = None) -> list[Edge]:
        edges = self.edges if polygons is None else self.edges_for_polygons(polygons)
        return sorted(edges, key=lambda e: (0 if abs(e.a[0]) < self.tol and abs(e.b[0]) < self.tol else 1,
                                             e.radial_angle))

    def connect(self) -> None:
        # Midpoint + length buckets make matching linear-time. Rounded values are
        # much tighter than the geometric tolerance used for transform points.
        buckets: dict[tuple[float, float, float, float], list[Edge]] = {}
        for edge in self.edges:
            if edge.connected:
                continue
            a = (round(edge.a[0], 6), round(edge.a[1], 6))
            b = (round(edge.b[0], 6), round(edge.b[1], 6))
            lo, hi = (a, b) if a <= b else (b, a)
            key = (lo[0], lo[1], hi[0], hi[1])
            buckets.setdefault(key, []).append(edge)
        self.disconnected_max = None
        self.disconnected_min = None
        for candidates in buckets.values():
            while len(candidates) >= 2:
                a = candidates.pop()
                b = candidates.pop()
                a.connected = b.connected = True
            if candidates:
                edge = candidates[0]
                self.disconnected_max = max(self.disconnected_max or 0.0, edge.max_radius)
                self.disconnected_min = min(self.disconnected_min if self.disconnected_min is not None else float("inf"), edge.min_radius)

    def transformed(self, kind: str, angle: float = 0.0,
                     origin: Point = (0.0, 0.0), axis: tuple[Point, Point] | None = None) -> list[Polygon]:
        if kind == "rotate":
            return [[_rotate_point(p, angle, origin) for p in poly] for poly in self.polygons]
        if kind == "reflect":
            if axis is None:
                raise ValueError("Reflection requires an axis")
            return [[_reflect_point(p, axis[0], axis[1]) for p in poly] for poly in self.polygons]
        raise ValueError(f"Unknown transform {kind!r}")

    def merge(self, polygons: Iterable[Polygon]) -> None:
        for poly in polygons:
            self.add(poly)

    def transform_point(self, action: str, angle: float = 0.0,
                        point: Point = (0.0, 0.0), point_angle: float = 0.0,
                        point_type: str = "h") -> None:
        if action == "r":
            # Eccentric rotations are half-turns in the notation.
            copies = self.transformed("rotate", math.pi, point)
            self.merge(copies)
            return
        mirror_angle = point_angle if point_type == "h" else point_angle + math.pi/2
        dx, dy = math.cos(mirror_angle), math.sin(mirror_angle)
        copies = self.transformed("reflect", axis=((point[0]-dx, point[1]-dy),
                                                     (point[0]+dx, point[1]+dy)))
        self.merge(copies)

    def vertices_for_transforms(self) -> list[tuple[Point, float, str, int]]:
        raw: list[tuple[Point, float, str]] = []
        for poly in self.polygons:
            c = _mean(poly)
            raw.append((c, _angle(*c), "c"))
        for e in self.edges:
            m = e.midpoint
            raw.extend([(e.a, _angle(*e.a), "v"), (m, e.angle, "h"), (e.b, _angle(*e.b), "v")])
        dedup: list[tuple[Point, float, str]] = []
        seen: set[tuple[int, int]] = set()
        for item in raw:
            p = item[0]
            if _dist(p, (0.0,0.0)) <= self.tol:
                continue
            key = (round(p[0] / self.tol), round(p[1] / self.tol))
            if key not in seen:
                seen.add(key)
                dedup.append(item)
        dedup.sort(key=lambda item: (round(item[1], 10), math.hypot(*item[0])))
        counters = {"c": 0, "v": 0, "h": 0}
        result = []
        for p, a, typ in dedup:
            counters[typ] += 1
            result.append((p, a, typ, counters[typ]))
        return result


def _regular_seed(sides: int, radius: float) -> Polygon:
    adjustments = {3: 0.5775, 4: 0.95, 6: 1.0, 8: 1.0, 12: 1.15}
    if sides not in SUPPORTED:
        raise ValueError("GomJau-Hogg seed polygons must have 3, 4, 6, 8 or 12 sides")
    r = radius * adjustments[sides]
    poly = [(math.cos(TAU*i/sides)*r, math.sin(TAU*i/sides)*r) for i in range(sides)]
    if sides == 3:
        poly = [_rotate_point(p, math.pi/3) for p in poly]
        poly = [(x+r,y) for x,y in poly]
        poly = [_rotate_point(p, -math.pi/3) for p in poly]
    else:
        rot = math.pi/sides
        poly = [_rotate_point(p, rot) for p in poly]
    return poly


def _from_edge(sides: int, edge: Edge) -> Polygon:
    if sides not in SUPPORTED:
        raise ValueError("Tiles must have 3, 4, 6, 8 or 12 sides")
    v1, v2 = edge.b, edge.a
    length = edge.length
    turn = TAU / sides
    a = math.atan2(v2[1]-v1[1], v2[0]-v1[0]) + turn
    points = [v1, v2]
    while len(points) < sides:
        prev = points[-1]
        points.append((prev[0] + math.cos(a)*length, prev[1] + math.sin(a)*length))
        a += turn
    return points


@dataclass
class Transform:
    action: str
    angle: float
    point_type: str | None = None
    point_index: int = 0
    source: str = ""
    point: tuple[Point, float, str, int] | None = None


_TRANSFORM = re.compile(r"^([mr])([\d.]*)?(?:\(([chv])?(\d+)?\))?$", re.I)


def parse_notation(notation: str):
    if not isinstance(notation, str) or not notation.strip():
        raise ValueError("A non-empty GomJau-Hogg notation is required")
    phases, *transform_text = notation.strip().split("/")
    groups = []
    for part in phases.split("-"):
        try:
            groups.append([int(x) if x else 0 for x in part.split(",")])
        except ValueError as exc:
            raise ValueError(f"Invalid shape phase {part!r}") from exc
    if not groups or len(groups[0]) != 1 or groups[0][0] not in SUPPORTED:
        raise ValueError("Notation must begin with seed 3, 4, 6, 8 or 12 followed by '-'")
    transforms = []
    for token in transform_text:
        if not token:
            # Preserve empty transform slots only as a no-op; ANTWERP examples use //.
            continue
        match = _TRANSFORM.match(token)
        if not match:
            raise ValueError(f"Invalid transform token {token!r}")
        action, deg, ptype, pindex = match.groups()
        angle = math.radians(float(deg or 180))
        if angle <= 0:
            raise ValueError(f"Transform angle must be positive in {token!r}")
        transforms.append(Transform(action.lower(), angle, ptype.lower() if ptype else None,
                                    int(pindex or 0), token))
    return groups[0][0], groups[1:], transforms


def generate_uniform(notation: str, width: float = 1000, height: float = 1000,
                     tile_size: float = 90, max_repeat: int = 6) -> list[Polygon]:
    """Generate a bounded patch from GomJau-Hogg notation.

    The algorithm grows an edge-to-edge regular-polygon patch by attaching shapes
    along exposed sides, then applies the requested mirror/rotation symmetries.
    The patch is cropped by the SVG viewport; it is not a proof of global validity
    for arbitrary user-entered notation.
    """
    if width <= 0 or height <= 0 or tile_size <= 0:
        raise ValueError("width, height and tile_size must be positive")
    if not isinstance(max_repeat, int) or max_repeat < 0:
        raise ValueError("max_repeat must be a non-negative integer")
    seed, phases, transforms = parse_notation(notation)
    tol = max(1e-7, tile_size*1e-7)
    root = Patch(tol=tol)
    root.add(_regular_seed(seed, tile_size/2))
    root.connect()

    # Placement phases: each phase places polygons on the available sides of the
    # immediately preceding phase. A zero skips the next available edge.
    last_phase = list(root.polygons)
    for phase in phases:
        phase_shapes: list[Polygon] = []
        phase_edges = root.sorted_edges(last_phase)
        skip_count = 0
        for n in phase:
            if n == 0:
                skip_count += 1
                continue
            if n not in SUPPORTED:
                raise ValueError("Tiles must have 3, 4, 6, 8 or 12 sides")
            chosen = None
            remaining_skip = skip_count
            for edge in phase_edges:
                # Only consume sides that are still exposed in the global patch.
                if not edge.connected:
                    if remaining_skip:
                        remaining_skip -= 1
                    else:
                        chosen = edge
                        break
            if chosen is not None:
                poly = _from_edge(n, chosen)
                before = len(root.polygons)
                root.add(poly)
                if len(root.polygons) > before:
                    phase_shapes.append(poly)
                    root.connect()
                # The phase_edges list is updated via the `connected` reference
                # to root edges only when it shares those Edge objects. Build it
                # directly from root edges to preserve the connected flags.
                phase_edges = root.sorted_edges(last_phase)
        if phase_shapes:
            last_phase = phase_shapes

    root.connect()
    vertices = root.vertices_for_transforms()
    for transform in transforms:
        if transform.point_index:
            selected = next((v for v in vertices if v[2] == transform.point_type and v[3] == transform.point_index), None)
            if selected is None:
                raise ValueError(f"No {transform.point_type}{transform.point_index} transform point for {transform.source!r}")
            transform.point = selected
            p, a, typ, _ = selected
            root.transform_point(transform.action, point=p, point_angle=a, point_type=typ)
        else:
            angle = transform.angle
            if transform.action == "r":
                while angle < TAU - 1e-12:
                    root.merge(root.transformed("rotate", angle))
                    angle *= 2
            else:
                while angle < TAU - 1e-12:
                    dx, dy = math.cos(angle-math.pi/2), math.sin(angle-math.pi/2)
                    root.merge(root.transformed("reflect", axis=((-dx,-dy),(dx,dy))))
                    angle *= 2
        root.connect()
        vertices = root.vertices_for_transforms()

    if len(transforms) > 1 and max_repeat:
        limit = math.hypot(width, height)/2
        previous_signature = None
        for _ in range(max_repeat):
            if root.disconnected_min is None or root.disconnected_min >= limit:
                break
            old_count = len(root.polygons)
            for transform in transforms:
                if transform.point_index:
                    if transform.point is None:
                        continue
                    p, a, typ, _ = transform.point
                    root.transform_point(transform.action, point=p, point_angle=a, point_type=typ)
                elif transform.action == "r":
                    angle = transform.angle
                    while angle < TAU - 1e-12:
                        root.merge(root.transformed("rotate", angle))
                        angle *= 2
                else:
                    angle = transform.angle
                    while angle < TAU - 1e-12:
                        dx, dy = math.cos(angle-math.pi/2), math.sin(angle-math.pi/2)
                        root.merge(root.transformed("reflect", axis=((-dx,-dy),(dx,dy))))
                        angle *= 2
            root.connect()
            signature = (len(root.polygons), round(root.disconnected_min or 0, 7), round(root.disconnected_max or 0, 7))
            if len(root.polygons) == old_count or signature == previous_signature:
                break
            previous_signature = signature

    return root.polygons
