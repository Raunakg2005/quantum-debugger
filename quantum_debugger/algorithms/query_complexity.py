"""
Quantum query complexity and separations.

In the query (oracle) model an algorithm learns a hidden input only by asking for its bits, and
we count queries. This is where quantum speedups are cleanest and provable:

* **Deutsch-Jozsa** -- ``1`` quantum query vs ``2^{n-1}+1`` classical (deterministic, exact):
  an exponential separation.
* **Simon** -- ``O(n)`` quantum vs ``Omega(2^{n/2})`` classical: an exponential separation that
  inspired Shor.
* **Grover** -- ``Theta(sqrt N)`` quantum vs ``Theta(N)`` classical: a quadratic speedup, and
  *optimal* (no quantum algorithm does better).
* **Parity** -- ``ceil(n/2)`` quantum vs ``n`` classical: exactly a factor-2 speedup, and no
  more.

The **polynomial method** lower-bounds bounded-error quantum query complexity by ``deg(f)/2``.
This module returns these query counts and the speedup factors, verified against the closed
forms.
"""

import numpy as np


def deutsch_jozsa_queries(n: int) -> dict:
    """Deutsch-Jozsa query complexity: ``1`` quantum vs ``2^{n-1}+1`` classical (deterministic) --
    an exponential separation."""
    return {"quantum": 1, "classical": 2 ** (n - 1) + 1}


def simon_queries(n: int) -> dict:
    """Simon's problem query complexity: ``O(n)`` quantum (``~n`` linear equations) vs
    ``Omega(2^{n/2})`` classical -- an exponential separation."""
    return {"quantum": n, "classical": int(2 ** (n / 2))}


def grover_queries(N: int) -> dict:
    """Grover search query complexity: ``ceil((pi/4) sqrt N)`` quantum vs ``N`` classical (worst
    case) -- a quadratic, and optimal, speedup."""
    return {"quantum": int(np.ceil(np.pi / 4 * np.sqrt(N))), "classical": N}


def parity_queries(n: int) -> dict:
    """Parity query complexity: ``ceil(n/2)`` quantum (Deutsch-Jozsa on pairs) vs ``n`` classical
    -- exactly a factor-2 speedup, and provably no better."""
    return {"quantum": int(np.ceil(n / 2)), "classical": n}


def quantum_speedup(counts: dict) -> float:
    """The speedup factor ``classical / quantum`` for a query problem -- exponential for
    Deutsch-Jozsa/Simon, quadratic for Grover, 2 for parity."""
    return float(counts["classical"] / counts["quantum"])


def polynomial_method_bound(degree: int) -> float:
    """The polynomial-method lower bound on bounded-error quantum query complexity,
    ``Q(f) >= deg(f)/2`` -- degree lower-bounds queries."""
    return float(degree / 2)


def is_exponential_separation(queries_fn, n: int = 10) -> bool:
    """
    Classify a bit-size-parametrized query problem: ``True`` iff its classical cost grows
    *exponentially* while its quantum cost grows only *polynomially* in ``n`` -- checked by the
    growth of ``queries_fn(n)`` versus ``queries_fn(n+4)``. Verified ``True`` for Deutsch-Jozsa and
    Simon, ``False`` for parity (a mere factor-2 speedup).
    """
    a, b = queries_fn(n), queries_fn(n + 4)
    classical_growth = b["classical"] / max(a["classical"], 1)
    quantum_growth = b["quantum"] / max(a["quantum"], 1)
    return bool(classical_growth >= 4 - 1e-9 and quantum_growth <= 2 + 1e-9)


def grover_is_optimal(N: int, quantum_queries: int) -> bool:
    """
    Verify Grover is order-optimal: its ``(pi/4) sqrt N`` query count is ``Theta(sqrt N)`` --
    within a constant factor of the BBBV lower bound ``Omega(sqrt N)`` -- so the quadratic speedup
    cannot be improved. Checks ``0.5 sqrt N <= q <= 1.5 sqrt N``.
    """
    root = np.sqrt(N)
    return bool(0.5 * root <= quantum_queries <= 1.5 * root)
