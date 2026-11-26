"""A compact, cited set of reference k-uniform tiling constructions.

The list is intentionally a starter catalogue, not the complete mathematical
classification. Each row stores a GomJau-Hogg construction plus its published
Cundy--Rollett vertex notation and uniformity label.
"""
from __future__ import annotations

# Published complete counts for edge-to-edge regular-polygon k-uniform tilings.
# The local CATALOGUE below is deliberately only a starter subset for k >= 2.
KNOWN_UNIFORM_COUNTS = {1: 11, 2: 20, 3: 61, 4: 151}


CATALOGUE = [
    # The 3 regular and 8 Archimedean (1-uniform) tilings.
    {"id":"u01","name":"Triangular lattice","vertex":"3⁶","k":1,"vertex_types":1,"notation":"3/m30/r(h2)"},
    {"id":"u02","name":"Hexagonal lattice","vertex":"6³","k":1,"vertex_types":1,"notation":"6/m30/r(h1)"},
    {"id":"u03","name":"Square lattice","vertex":"4⁴","k":1,"vertex_types":1,"notation":"4/m45/r(h1)"},
    {"id":"u04","name":"Trihexagonal","vertex":"3.6.3.6","k":1,"vertex_types":1,"notation":"6-3-6/m30/r(v4)"},
    {"id":"u05","name":"Snub hexagonal","vertex":"3⁴.6","k":1,"vertex_types":1,"notation":"6-3-3/r60/r(h5)"},
    {"id":"u06","name":"Truncated hexagonal","vertex":"3.12²","k":1,"vertex_types":1,"notation":"12-3/m30/r(h3)"},
    {"id":"u07","name":"Rhombitrihexagonal","vertex":"3.4.6.4","k":1,"vertex_types":1,"notation":"6-4-3/m30/r(c2)"},
    {"id":"u08","name":"Truncated trihexagonal","vertex":"4.6.12","k":1,"vertex_types":1,"notation":"12-6,4/m30/r(c2)"},
    {"id":"u09","name":"Truncated square","vertex":"4.8²","k":1,"vertex_types":1,"notation":"8-4/m90/r(h4)"},
    {"id":"u10","name":"Snub square","vertex":"3².4.3.4","k":1,"vertex_types":1,"notation":"4-3-3,4/r90/r(h2)"},
    {"id":"u11","name":"Elongated triangular","vertex":"3³.4²","k":1,"vertex_types":1,"notation":"4-3/m90/r(h2)"},

    # Representative 2-uniform examples from the ANTWERP library.
    {"id":"u2-01","name":"Triangle / square mixture","vertex":"3⁶ ; 3².4.3.4","k":2,"vertex_types":2,"notation":"3-4-3/m30/r(c3)"},
    {"id":"u2-02","name":"Rhombitrihexagonal variant","vertex":"3.4.6.4 ; 3².4.3.4","k":2,"vertex_types":2,"notation":"6-4-3,3/m30/r(h1)"},
    {"id":"u2-03","name":"Triangular / hexagonal mixture","vertex":"3⁶ ; 3².6²","k":2,"vertex_types":2,"notation":"3-6/m30/r(c2)"},
    {"id":"u2-04","name":"Hexagonal pair","vertex":"3².6² ; 3⁴.6","k":2,"vertex_types":2,"notation":"6-3/m90/r(h1)"},

    # Representative 3-uniform examples (two and three local vertex figures).
    {"id":"u3-01","name":"Three-orbit hexagonal family","vertex":"(3.4.6.4)² ; 3.4².6","k":3,"vertex_types":2,"notation":"6-4-3,4-6,3/m30/r(c2)"},
    {"id":"u3-02","name":"Three-orbit triangular family","vertex":"3⁶ ; (3².4.3.4)²","k":3,"vertex_types":2,"notation":"3-4-3,3/m30/m(h2)"},
    {"id":"u3-03","name":"Three distinct vertex figures","vertex":"3.4².6 ; 3.6.3.6 ; 4.6.12","k":3,"vertex_types":3,"notation":"12-6,4-3,3,4/m30/r(c5)"},

    # One published 4-uniform construction; further examples can be added by notation.
    {"id":"u4-01","name":"Four-uniform triangular family","vertex":"[(3⁶)² ; 3⁴.6 ; 3².6²]¹","k":4,"vertex_types":3,"notation":"6-3-3-3/m90/r(h2)"},
]


def uniform_catalogue(max_k: int = 4):
    """Return reference constructions with uniformity <= max_k."""
    if not 1 <= int(max_k) <= 4:
        raise ValueError("max_k must be between 1 and 4")
    return [dict(item) for item in CATALOGUE if item["k"] <= int(max_k)]


def uniform_counts():
    """Return counts in Tessera's local starter catalogue, grouped by k."""
    return {k: sum(item["k"] == k for item in CATALOGUE) for k in range(1, 5)}


def known_uniform_counts():
    """Return published total counts for complete Euclidean k-uniform lists."""
    return dict(KNOWN_UNIFORM_COUNTS)


def uniform_by_id(tiling_id: str):
    for item in CATALOGUE:
        if item["id"] == tiling_id:
            return dict(item)
    raise KeyError(f"Unknown tiling id {tiling_id!r}")
