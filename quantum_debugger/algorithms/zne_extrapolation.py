"""
Zero-noise extrapolation -- the extrapolation models.

ZNE runs a circuit at several noise scales ``lambda_1 < lambda_2 < ...`` and
extrapolates the expectation value back to ``lambda = 0``. The estimate is only as
good as the fitting model, so this module provides the standard ones -- Richardson
(exact polynomial elimination), least-squares polynomial, and an exponential ansatz
-- plus an adaptive selector that picks the model with the smallest leave-one-out
error. Each is verified against data it should fit exactly: Richardson and the
polynomial fit recover the ``lambda=0`` value of any polynomial of matching degree,
and the exponential fit inverts ``A + B e^{-c lambda}`` exactly.
"""

import numpy as np


def richardson_extrapolate(scales, values) -> float:
    """
    Richardson extrapolation: the unique degree-``(n-1)`` polynomial through the ``n``
    points ``(scale, value)`` evaluated at ``lambda = 0`` (Lagrange interpolation at 0).
    Exact when the noise dependence is a polynomial of degree ``<= n-1``.
    """
    x = np.asarray(scales, dtype=float)
    y = np.asarray(values, dtype=float)
    n = len(x)
    result = 0.0
    for i in range(n):
        # Lagrange basis L_i(0) = prod_{j!=i} (0 - x_j)/(x_i - x_j)
        li = 1.0
        for j in range(n):
            if j != i:
                li *= (0.0 - x[j]) / (x[i] - x[j])
        result += y[i] * li
    return float(result)


def polynomial_extrapolate(scales, values, degree: int = 2) -> float:
    """
    Least-squares polynomial ZNE: fit a degree-``degree`` polynomial to the (scale,
    value) data and evaluate it at ``lambda = 0``. More robust than Richardson when the
    data are noisy and over-determined. Exact for a polynomial of degree ``<= degree``.
    """
    x = np.asarray(scales, dtype=float)
    y = np.asarray(values, dtype=float)
    coeffs = np.polyfit(x, y, degree)
    return float(np.polyval(coeffs, 0.0))


def exponential_extrapolate(scales, values) -> dict:
    """
    Exponential ZNE: fit ``E(lambda) = A + B e^{-c lambda}`` (the decay expected when a
    depolarizing-like channel damps the signal geometrically in the noise scale) and
    return the zero-noise value ``A + B``. Returns a dict with ``value`` and the fitted
    ``A, B, c``. Exact when the data follow that form.
    """
    x = np.asarray(scales, dtype=float)
    y = np.asarray(values, dtype=float)

    def model(c):
        # For fixed c the model is linear in (A, B): solve, return residual.
        basis = np.vstack([np.ones_like(x), np.exp(-c * x)]).T
        (A, B), *_ = np.linalg.lstsq(basis, y, rcond=None)
        return A, B, np.sum((basis @ [A, B] - y) ** 2)

    # 1-D search over the rate c (the only nonlinear parameter).
    cs = np.linspace(1e-3, 10.0, 4000)
    best = min(cs, key=lambda c: model(c)[2])
    A, B, _ = model(best)
    return {"value": float(A + B), "A": float(A), "B": float(B), "c": float(best)}


def adaptive_extrapolate(scales, values) -> dict:
    """
    Adaptive ZNE: try the linear, quadratic, and exponential models, score each by its
    leave-one-out prediction error, and return the zero-noise estimate from the best
    one. Returns ``value``, the chosen ``model`` name, and the per-model errors -- so the
    extrapolation model is selected by the data instead of assumed.
    """
    x = np.asarray(scales, dtype=float)
    y = np.asarray(values, dtype=float)
    n = len(x)

    def loo_error(fit_at_zero):
        errs = []
        for k in range(n):
            mask = np.arange(n) != k
            # refit without point k, predict it
            try:
                pred = fit_at_zero(x[mask], y[mask], predict_x=x[k])
                errs.append((pred - y[k]) ** 2)
            except Exception:
                return np.inf
        return float(np.mean(errs))

    def poly_predict(deg):
        def f(xx, yy, predict_x):
            return np.polyval(np.polyfit(xx, yy, deg), predict_x)
        return f

    def exp_predict(xx, yy, predict_x):
        cs = np.linspace(1e-3, 10.0, 800)

        def resid(c):
            basis = np.vstack([np.ones_like(xx), np.exp(-c * xx)]).T
            ab, *_ = np.linalg.lstsq(basis, yy, rcond=None)
            return ab, np.sum((basis @ ab - yy) ** 2)
        best = min(cs, key=lambda c: resid(c)[1])
        ab, _ = resid(best)
        return ab[0] + ab[1] * np.exp(-best * predict_x)

    candidates = {
        "linear": (loo_error(poly_predict(1)), lambda: polynomial_extrapolate(x, y, 1)),
        "quadratic": (loo_error(poly_predict(2)), lambda: polynomial_extrapolate(x, y, 2)),
        "exponential": (loo_error(exp_predict), lambda: exponential_extrapolate(x, y)["value"]),
    }
    errors = {k: v[0] for k, v in candidates.items()}
    chosen = min(errors, key=errors.get)
    return {"value": float(candidates[chosen][1]()), "model": chosen, "errors": errors}
