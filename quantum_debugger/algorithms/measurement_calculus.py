"""
The measurement calculus -- patterns and causal flow.

A one-way computation is specified by a **measurement pattern**: entangle a set of qubits into
a graph state (``E`` commands), measure the non-output qubits in chosen bases (``M`` commands),
and apply Pauli corrections conditioned on outcomes (``X``/``Z`` commands). Whether a pattern runs
*deterministically* (independent of the random outcomes, after corrections) is decided by the
existence of a **causal flow** (Danos-Kashefi): a function ``f`` from measured qubits to
successors with a compatible partial order such that

    f(i) ~ i,   i < f(i),   and every neighbour k of f(i) satisfies i <= k.

This module represents patterns, and finds/verifies a causal flow -- verified for the linear
cluster (``f(i) = i+1``), which is exactly why the cluster runs deterministic single-qubit
teleportation.
"""


def measurement_pattern(entangle_edges, measured, outputs, angles):
    """
    A measurement pattern as a dict: the entangling ``edges``, the ordered ``measured`` qubits
    with their X-Y ``angles``, and the ``outputs``. The declarative description of a one-way
    computation.
    """
    return {
        "edges": list(entangle_edges),
        "measured": list(measured),
        "outputs": list(outputs),
        "angles": dict(zip(measured, angles)),
    }


def _neighbours(edges, n):
    nb = {v: set() for v in range(n)}
    for i, j in edges:
        nb[i].add(j)
        nb[j].add(i)
    return nb


def causal_flow(edges, inputs, outputs, n):
    """
    Find a causal flow ``(f, order)`` for an open graph ``(edges, inputs, outputs)`` on ``n``
    qubits, or ``None`` if none exists. ``f`` maps each non-output qubit to a successor; ``order``
    is the induced depth layering. A graph with a flow yields a deterministic MBQC pattern.
    """
    nb = _neighbours(edges, n)
    non_outputs = [v for v in range(n) if v not in outputs]
    non_inputs = set(v for v in range(n) if v not in inputs)
    f = {}
    order = {v: 0 for v in range(n)}
    # greedy: for each measured qubit, pick a neighbour in non_inputs not yet used as an image
    used = set()
    for v in non_outputs:
        cand = [w for w in nb[v] if w in non_inputs and w not in used]
        if not cand:
            return None
        w = min(cand)
        f[v] = w
        used.add(w)
        order[w] = order[v] + 1
    if not verify_flow(edges, f, order, outputs, n):
        return None
    return f, order


def verify_flow(edges, f, order, outputs, n) -> bool:
    """
    Verify the causal-flow conditions for a candidate ``f`` and depth ``order``: ``f(i)`` is a
    neighbour of ``i``, ``i`` is measured before ``f(i)``, and every neighbour ``k`` of ``f(i)``
    (other than ``i``) is measured no earlier than ``i``.
    """
    nb = _neighbours(edges, n)
    for i, fi in f.items():
        if fi not in nb[i]:
            return False
        if not order[i] < order[fi]:
            return False
        for k in nb[fi]:
            if k != i and not order[i] <= order[k]:
                return False
    return True


def has_flow(edges, inputs, outputs, n) -> bool:
    """True iff the open graph admits a causal flow -- i.e. the pattern can be made
    deterministic. Verified true for the linear cluster."""
    return causal_flow(edges, inputs, outputs, n) is not None


def pattern_depth(edges, inputs, outputs, n) -> int:
    """The depth (number of measurement layers) of the flow-induced schedule -- the parallel time
    of the one-way computation."""
    res = causal_flow(edges, inputs, outputs, n)
    if res is None:
        return -1
    _, order = res
    return int(max(order.values()) + 1)
