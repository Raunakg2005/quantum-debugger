"""
Graph states and their stabilizers.

A **graph state** is the entangled resource of measurement-based computing: take a graph,
put a ``|+>`` on every vertex, and apply a controlled-``Z`` on every edge,

    |G> = prod_{(i,j) in E} CZ_ij |+>^n .

It is a stabilizer state with generators ``K_v = X_v prod_{w ~ v} Z_w`` (one per vertex). The
1D chain is the **linear cluster state** and the square lattice the **2D cluster state**
(universal for computation). **Local complementation** at a vertex -- toggling the edges among
its neighbours -- maps a graph state to a *locally Clifford-equivalent* one. This module builds
graph states, verifies their stabilizers, and verifies local-complementation equivalence.
"""

import numpy as np

_H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
_P1 = {
    "X": np.array([[0, 1], [1, 0]], dtype=complex),
    "Y": np.array([[0, -1j], [1j, 0]], dtype=complex),
    "Z": np.array([[1, 0], [0, -1]], dtype=complex),
    "I": np.eye(2, dtype=complex),
}


def _embed(op, q, n):
    M = np.array([[1.0]], dtype=complex)
    for i in range(n):
        M = np.kron(_P1[op] if i == q else np.eye(2), M)  # little-endian: qubit 0 = LSB
    return M


def _cz(i, j, n):
    diag = np.ones(2 ** n)
    for b in range(2 ** n):
        if ((b >> i) & 1) and ((b >> j) & 1):
            diag[b] = -1
    return np.diag(diag)


def graph_state(edges, n: int) -> np.ndarray:
    """The graph state ``prod_{(i,j)} CZ_ij |+>^n`` for the given edge list -- the MBQC
    resource state."""
    psi = np.ones(2 ** n, dtype=complex) / np.sqrt(2 ** n)
    for i, j in edges:
        psi = _cz(i, j, n) @ psi
    return psi


def graph_state_stabilizers(edges, n: int):
    """
    The stabilizer generators ``K_v = X_v prod_{w ~ v} Z_w`` (one per vertex) of a graph state,
    returned as full ``2^n x 2^n`` matrices -- the operators that fix the state.
    """
    neighbours = {v: set() for v in range(n)}
    for i, j in edges:
        neighbours[i].add(j)
        neighbours[j].add(i)
    stabs = []
    for v in range(n):
        K = _embed("X", v, n)
        for w in neighbours[v]:
            K = K @ _embed("Z", w, n)
        stabs.append(K)
    return stabs


def verify_stabilizers(edges, n: int, atol: float = 1e-9) -> bool:
    """True iff every generator ``K_v`` fixes the graph state (``K_v|G> = |G>``) -- the defining
    stabilizer condition."""
    psi = graph_state(edges, n)
    return all(np.allclose(K @ psi, psi, atol=atol) for K in graph_state_stabilizers(edges, n))


def linear_cluster_edges(n: int):
    """Edges of the 1D linear cluster state (a path graph on ``n`` vertices)."""
    return [(i, i + 1) for i in range(n - 1)]


def cluster_2d_edges(nx: int, ny: int):
    """Edges of the 2D cluster state on an ``nx x ny`` grid (nearest-neighbour), with vertices
    indexed ``i*ny + j``."""
    edges = []
    for i in range(nx):
        for j in range(ny):
            v = i * ny + j
            if j + 1 < ny:
                edges.append((v, i * ny + (j + 1)))
            if i + 1 < nx:
                edges.append((v, (i + 1) * ny + j))
    return edges


def complete_graph_edges(n: int):
    """Edges of the complete graph ``K_n`` -- its graph state is local-Clifford equivalent to the
    ``n``-qubit GHZ state."""
    return [(i, j) for i in range(n) for j in range(i + 1, n)]


def star_graph_edges(n: int):
    """Edges of the star graph (one centre connected to ``n-1`` leaves) -- its graph state is
    exactly the GHZ state up to local Cliffords."""
    return [(0, j) for j in range(1, n)]


def graph_state_entanglement(edges, n: int) -> float:
    """
    Meyer-Wallach global entanglement of a graph state ``Q = 2(1 - (1/n) sum Tr rho_k^2)`` -- 0
    for the empty graph (product state) and near 1 for a highly connected one.
    """
    from .entangling_capability import meyer_wallach
    return meyer_wallach(graph_state(edges, n))


def local_complementation(edges, v: int, n: int):
    """
    Local complementation at vertex ``v``: toggle every edge between pairs of ``v``'s
    neighbours. Returns the new edge set. The graph states of a graph and its local complement
    are equivalent under local Clifford gates.
    """
    E = set(frozenset(e) for e in edges)
    nbrs = [w for w in range(n) if frozenset((v, w)) in E]
    for a in nbrs:
        for b in nbrs:
            if a < b:
                e = frozenset((a, b))
                if e in E:
                    E.remove(e)
                else:
                    E.add(e)
    return [tuple(sorted(e)) for e in E]


def local_clifford_equivalent(edges1, edges2, v: int, n: int, atol: float = 1e-9) -> bool:
    """
    Verify two graph states related by local complementation at ``v`` are local-Clifford
    equivalent: ``|G'> = (-i X_v)^{1/2} prod_{w~v} (i Z_w)^{1/2} |G>`` up to global phase.
    """
    g1 = graph_state(edges1, n)
    g2 = graph_state(edges2, n)
    sqrtX = np.array([[1 + 1j, 1 - 1j], [1 - 1j, 1 + 1j]]) / 2       # sqrt(X)
    sqrtZ = np.array([[1, 0], [0, 1j]], dtype=complex)               # sqrt(Z)
    U = _embed_matrix(sqrtX, v, n)
    nbrs = set()
    for i, j in edges1:
        if i == v:
            nbrs.add(j)
        elif j == v:
            nbrs.add(i)
    for w in nbrs:
        U = U @ _embed_matrix(sqrtZ.conj(), w, n)
    out = U @ g1
    # compare up to global phase
    idx = int(np.argmax(np.abs(g2)))
    if abs(out[idx]) < atol:
        return False
    return bool(np.allclose(out * (g2[idx] / out[idx]), g2, atol=1e-6))


def _embed_matrix(gate, q, n):
    M = np.array([[1.0]], dtype=complex)
    for i in range(n):
        M = np.kron(gate if i == q else np.eye(2), M)
    return M
