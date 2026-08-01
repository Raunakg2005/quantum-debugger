"""
The quantum Otto engine.

A quantum Otto cycle drives a working medium (here a single qubit with tunable level spacing
``omega``) around four strokes:

1. **Adiabatic compression** ``omega_c -> omega_h`` at fixed populations (work input).
2. **Hot isochore** -- thermalize with the hot bath at ``omega_h`` (heat ``Q_h`` absorbed).
3. **Adiabatic expansion** ``omega_h -> omega_c`` (work output).
4. **Cold isochore** -- thermalize with the cold bath at ``omega_c`` (heat ``Q_c`` released).

For the qubit the efficiency has the closed form ``eta = 1 - omega_c/omega_h``, which -- when the
engine actually produces net work -- is bounded above by the **Carnot** efficiency
``1 - T_c/T_h``. This module computes the per-stroke heat and work, the efficiency, and verifies
the Carnot bound.
"""

import numpy as np


def _thermal_excited_population(omega: float, T: float) -> float:
    """Excited-state population of a qubit with gap ``omega`` at temperature ``T``:
    ``1/(1 + e^{omega/T})``."""
    return float(1.0 / (1 + np.exp(omega / T)))


def otto_cycle(omega_c: float, omega_h: float, T_c: float, T_h: float) -> dict:
    """
    Run a qubit quantum Otto cycle. Returns the heat absorbed from the hot bath ``Q_h``, released
    to the cold bath ``Q_c``, the net work output ``W = -(Q_h + Q_c)``, and the efficiency. Sign
    convention: ``W > 0`` means the cycle delivers work (engine mode).
    """
    p_h = _thermal_excited_population(omega_h, T_h)   # after hot isochore (gap omega_h)
    p_c = _thermal_excited_population(omega_c, T_c)    # after cold isochore (gap omega_c)
    Q_h = omega_h * (p_h - p_c)                        # heat in on the hot isochore
    Q_c = omega_c * (p_c - p_h)                        # heat out on the cold isochore
    W = Q_h + Q_c                                      # net work extracted (energy conservation)
    eta = W / Q_h if Q_h > 1e-12 else 0.0
    return {"Q_h": float(Q_h), "Q_c": float(Q_c), "work": float(W), "efficiency": float(eta)}


def otto_efficiency(omega_c: float, omega_h: float) -> float:
    """The closed-form qubit Otto efficiency ``eta = 1 - omega_c/omega_h`` -- set entirely by the
    compression ratio, independent of the bath temperatures."""
    return float(1 - omega_c / omega_h)


def carnot_efficiency(T_c: float, T_h: float) -> float:
    """The Carnot efficiency ``1 - T_c/T_h`` -- the universal upper bound on any heat engine."""
    return float(1 - T_c / T_h)


def is_engine(omega_c: float, omega_h: float, T_c: float, T_h: float) -> bool:
    """True iff the Otto cycle operates as an engine (positive net work) -- requires
    ``omega_c/omega_h > T_c/T_h``."""
    return otto_cycle(omega_c, omega_h, T_c, T_h)["work"] > 1e-12


def efficiency_below_carnot(omega_c: float, omega_h: float, T_c: float, T_h: float,
                            atol: float = 1e-9) -> bool:
    """Verify the second law for the Otto engine: when it produces work, its efficiency does not
    exceed the Carnot bound."""
    if not is_engine(omega_c, omega_h, T_c, T_h):
        return True
    return bool(otto_efficiency(omega_c, omega_h) <= carnot_efficiency(T_c, T_h) + atol)
