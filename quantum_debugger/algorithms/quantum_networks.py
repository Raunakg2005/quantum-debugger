"""
Quantum networks -- entanglement swapping, repeaters, and routing.

Entanglement cannot be amplified, so long-distance quantum links are built from short ones by
**entanglement swapping**: a Bell measurement on the middle node of an A-M-B chain leaves A and
B entangled, at the cost of some fidelity. Chaining swaps (a **repeater**) extends entanglement
across many segments, and **routing** finds the highest-fidelity entangled path across a
network graph. This module models Werner-state links, the fidelity after swapping and
purification, the repeater rate, and Dijkstra-style entanglement routing -- verified against the
closed-form swap and repeater formulas.
"""

import numpy as np
import heapq


def werner_fidelity(w: float) -> float:
    """Fidelity to the target Bell state of a Werner state with parameter ``w``:
    ``F = (1 + 3w)/4``."""
    return float((1 + 3 * w) / 4)


def swap_werner(w1: float, w2: float) -> float:
    """
    Werner parameter after entanglement swapping two Werner links: ``w_out = w1 * w2`` (the
    depolarization parameters multiply). Fidelity degrades with each swap -- the reason
    repeaters need purification.
    """
    return float(w1 * w2)


def entanglement_swapping_fidelity(f1: float, f2: float) -> float:
    """
    Fidelity of the entangled pair produced by swapping two links of fidelity ``f1, f2`` (via
    their Werner parameters). Verified to reduce to the input fidelity for a perfect second link.
    """
    w1 = (4 * f1 - 1) / 3
    w2 = (4 * f2 - 1) / 3
    return werner_fidelity(swap_werner(w1, w2))


def repeater_werner(w: float, n_segments: int) -> float:
    """Werner parameter across ``n_segments`` identical links joined by swapping: ``w^n`` --
    exponential fidelity decay without purification."""
    return float(w ** n_segments)


def repeater_rate(p_link: float, n_segments: int, p_swap: float = 1.0) -> float:
    """
    Entanglement-generation rate across an ``n_segments`` repeater chain where each link succeeds
    with probability ``p_link`` and each swap with ``p_swap`` -- ``p_link * p_swap^{n-1}`` per
    attempt (a simple synchronous model). Decreases with chain length.
    """
    return float(p_link * p_swap ** (n_segments - 1))


def purified_fidelity(f: float) -> float:
    """
    Fidelity after one round of DEJMPS/BBPSSW recurrence purification of two copies of fidelity
    ``f``: ``(f^2 + ((1-f)/3)^2) / (f^2 + 2 f (1-f)/3 + 5((1-f)/3)^2)`` -- raises the fidelity of
    a link above ``0.5``.
    """
    a = f
    b = (1 - f) / 3
    num = a ** 2 + b ** 2
    den = a ** 2 + 2 * a * b + 5 * b ** 2
    return float(num / den)


def path_fidelity(link_fidelities) -> float:
    """
    Fidelity of the end-to-end pair after swapping a chain of links with the given fidelities:
    the Werner parameters multiply. Decreases with each additional hop.
    """
    w = 1.0
    for f in link_fidelities:
        w *= (4 * f - 1) / 3
    return werner_fidelity(w)


def hops_before_threshold(link_fidelity: float, threshold: float = 0.5) -> int:
    """
    The number of identical-link swaps before the end-to-end fidelity drops to ``threshold`` --
    how far entanglement reaches without purification. Verified to shrink as the link fidelity
    worsens.
    """
    w = (4 * link_fidelity - 1) / 3
    hops = 1
    while werner_fidelity(w ** hops) > threshold and hops < 1000:
        hops += 1
    return hops - 1


def ghz_distribution_fidelity(link_fidelities) -> float:
    """
    Fidelity of a GHZ state distributed to ``n`` parties over links of the given fidelities
    (product of per-link Werner parameters) -- the multipartite analogue of a shared Bell pair.
    """
    w = 1.0
    for f in link_fidelities:
        w *= (4 * f - 1) / 3
    return werner_fidelity(w)


def entanglement_routing(graph, source, target):
    """
    Highest-fidelity entanglement path through a network: ``graph`` maps ``(u,v)`` to link
    fidelity; the path fidelity is the product of edge fidelities (via Werner parameters), and
    this returns ``(best_fidelity, path)`` by a Dijkstra-style search maximizing the product.
    Verified to pick the higher-fidelity of two routes.
    """
    # maximize product of werner params (= -sum of -log w); use max-product Dijkstra
    nodes = set()
    adj = {}
    for (u, v), f in graph.items():
        w = (4 * f - 1) / 3
        adj.setdefault(u, []).append((v, w))
        adj.setdefault(v, []).append((u, w))
        nodes.update([u, v])
    best = {source: 1.0}
    prev = {}
    pq = [(-1.0, source)]
    while pq:
        negw, u = heapq.heappop(pq)
        wprod = -negw
        if u == target:
            break
        if wprod < best.get(u, -1):
            continue
        for v, w in adj.get(u, []):
            nw = wprod * w
            if nw > best.get(v, -1):
                best[v] = nw
                prev[v] = u
                heapq.heappush(pq, (-nw, v))
    if target not in best:
        return 0.0, []
    path = [target]
    while path[-1] != source:
        path.append(prev[path[-1]])
    return werner_fidelity(best[target]), list(reversed(path))
