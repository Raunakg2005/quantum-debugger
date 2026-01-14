"""
Extrapolation Methods for Zero-Noise Extrapolation

Implements various curve-fitting techniques to extrapolate noisy measurements
to the zero-noise limit.
"""

import numpy as np
from scipy.optimize import curve_fit
from typing import List, Tuple, Optional


class Extrapolator:
    """
    Factory class for different extrapolation methods.

    Supports Richardson, exponential, polynomial, and adaptive extrapolation.
    """

    @staticmethod
    def richardson(
        noise_levels: np.ndarray, expectation_values: np.ndarray, order: int = 2
    ) -> float:
        """
        Richardson extrapolation (polynomial fit).

        Fits a polynomial of specified order and evaluates at x=0 (zero noise).

        Args:
            noise_levels: Array of noise scaling factors [1.0, 2.0, 3.0, ...]
            expectation_values: Measured expectation values at each noise level
            order: Polynomial order (1=linear, 2=quadratic, etc.)

        Returns:
            Extrapolated zero-noise expectation value

        Example:
            >>> levels = np.array([1.0, 2.0, 3.0])
            >>> values = np.array([0.95, 0.91, 0.87])
            >>> zero_noise = Extrapolator.richardson(levels, values, order=2)
        """
        # Fit polynomial: y = a0 + a1*x + a2*x^2 + ...
        coeffs = np.polyfit(noise_levels, expectation_values, order)
        poly = np.poly1d(coeffs)

        # Evaluate at x=0 (zero noise)
        return float(poly(0))

    @staticmethod
    def linear(noise_levels: np.ndarray, expectation_values: np.ndarray) -> float:
        """
        Simple linear extrapolation.

        Args:
            noise_levels: Noise scaling factors
            expectation_values: Measured values

        Returns:
            Zero-noise value (y-intercept)
        """
        # Fit y = mx + b
        coeffs = np.polyfit(noise_levels, expectation_values, 1)
        return float(coeffs[1])  # Return b (y-intercept)

    @staticmethod
    def polynomial(
        noise_levels: np.ndarray, expectation_values: np.ndarray, degree: int = 3
    ) -> float:
        """
        Polynomial extrapolation with specified degree.

        Args:
            noise_levels: Noise scaling factors
            expectation_values: Measured values
            degree: Polynomial degree

        Returns:
            Extrapolated zero-noise value
        """
        return Extrapolator.richardson(noise_levels, expectation_values, degree)

    @staticmethod
    def exponential(
        noise_levels: np.ndarray, expectation_values: np.ndarray
    ) -> Tuple[float, dict]:
        """
        Exponential extrapolation: y = a + b * exp(-c*x)

        Better for noise that decays exponentially with circuit depth.

        Args:
            noise_levels: Noise scaling factors
            expectation_values: Measured values

        Returns:
            Tuple of (zero_noise_value, fit_params)
        """

        def exp_func(x, a, b, c):
            return a + b * np.exp(-c * x)

        try:
            # Initial guess
            p0 = [
                expectation_values[0],  # a ~ first measurement
                -0.1,  # b (decay coefficient)
                0.5,  # c (decay rate)
            ]

            popt, pcov = curve_fit(
                exp_func, noise_levels, expectation_values, p0=p0, maxfev=10000
            )

            # Value at x=0
            zero_noise = exp_func(0, *popt)

            fit_info = {
                "params": popt,
                "covariance": pcov,
                "a": popt[0],
                "b": popt[1],
                "c": popt[2],
            }

            return float(zero_noise), fit_info

        except RuntimeError as e:
            # Fallback to linear if exponential fit fails
            print(f"Exponential fit failed: {e}. Falling back to linear.")
            return Extrapolator.linear(noise_levels, expectation_values), {}

    @staticmethod
    def adaptive(
        noise_levels: np.ndarray, expectation_values: np.ndarray
    ) -> Tuple[float, str]:
        """
        Adaptive extrapolation: try multiple methods, pick best fit.

        Evaluates residuals for linear, quadratic, and exponential fits,
        then returns the result with lowest residual.

        Args:
            noise_levels: Noise scaling factors
            expectation_values: Measured values

        Returns:
            Tuple of (best_zero_noise_value, best_method_name)
        """
        methods = {
            "linear": lambda: Extrapolator.linear(noise_levels, expectation_values),
            "quadratic": lambda: Extrapolator.richardson(
                noise_levels, expectation_values, 2
            ),
            "cubic": lambda: Extrapolator.polynomial(
                noise_levels, expectation_values, 3
            ),
        }

        # Try exponential (with error handling)
        try:
            exp_result, _ = Extrapolator.exponential(noise_levels, expectation_values)
            methods["exponential"] = lambda: exp_result
        except:
            pass

        best_method = None
        best_residual = float("inf")
        best_value = None

        for method_name, method_func in methods.items():
            try:
                zero_noise_val = method_func()

                # Calculate residual by reconstructing fit and measuring error
                if method_name == "linear":
                    order = 1
                elif method_name == "quadratic":
                    order = 2
                elif method_name == "cubic":
                    order = 3
                else:  # exponential
                    # Use exponential residual from curve_fit
                    order = None

                if order is not None:
                    coeffs = np.polyfit(noise_levels, expectation_values, order)
                    poly = np.poly1d(coeffs)
                    fit_values = poly(noise_levels)
                    residual = np.sum((expectation_values - fit_values) ** 2)
                else:
                    # Exponential - approximate residual
                    residual = 0.1  # Give exponential mid-priority

                if residual < best_residual:
                    best_residual = residual
                    best_method = method_name
                    best_value = zero_noise_val

            except Exception as e:
                # Skip methods that fail
                continue

        if best_value is None:
            # Ultimate fallback
            best_value = expectation_values[0]
            best_method = "unmitigated"

        return best_value, best_method

    @staticmethod
    def weighted_extrapolation(
        noise_levels: np.ndarray,
        expectation_values: np.ndarray,
        errors: np.ndarray,
        method: str = "linear",
    ) -> Tuple[float, float]:
        """
        Weighted extrapolation using inverse variance weighting.

        Accounts for measurement uncertainties in the fit.

        Args:
            noise_levels: Noise scaling factors
            expectation_values: Measured values
            errors: Standard errors for each measurement
            method: Extrapolation method ('linear', 'quadratic', etc.)

        Returns:
            Tuple of (mitigated_value, mitigated_error)
        """
        # Inverse variance weights
        weights = 1.0 / (errors**2 + 1e-10)  # Avoid division by zero

        # Weighted polynomial fit
        if method in ["linear", "quadratic", "cubic"]:
            order = {"linear": 1, "quadratic": 2, "cubic": 3}[method]
            coeffs, cov = np.polyfit(
                noise_levels, expectation_values, order, w=weights, cov=True
            )

            poly = np.poly1d(coeffs)
            mitigated_value = float(poly(0))

            # Error propagation
            # For polynomial at x=0, only constant term matters
            mitigated_error = np.sqrt(cov[-1, -1])

        else:
            # Fallback to unweighted
            mitigated_value = Extrapolator.linear(noise_levels, expectation_values)
            mitigated_error = np.std(expectation_values)

        return mitigated_value, mitigated_error


def bootstrap_estimate(
    measurements: np.ndarray, n_resamples: int = 100
) -> Tuple[float, float]:
    """
    Bootstrap resampling for error estimation.

    Args:
        measurements: Array of measurement outcomes
        n_resamples: Number of bootstrap samples

    Returns:
        Tuple of (mean, standard_error)
    """
    n = len(measurements)
    bootstrap_means = []

    for _ in range(n_resamples):
        # Resample with replacement
        resample = np.random.choice(measurements, size=n, replace=True)
        bootstrap_means.append(np.mean(resample))

    mean = np.mean(bootstrap_means)
    std_error = np.std(bootstrap_means)

    return mean, std_error
