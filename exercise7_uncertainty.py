"""
Exercise 7 -- Error propagation and statistics for real measurements
======================================================================

Goal
----
Every quantitative result you produce elsewhere in this practical (a spring
constant, a mole fraction, a rotational constant, a bond length) is only
half a result without an honest uncertainty attached to it. This exercise
builds a small, reusable statistics toolkit and then applies it to real
decisions you have to make in your report:

  * How many significant figures can you actually justify?
  * With only 3 repeat measurements (Section A, task v), what is a
    defensible 95% confidence interval -- and why is it NOT just
    mean +/- std?
  * If two measured values differ, is that a real effect or could it be
    noise? (a t-test answers this quantitatively, instead of "they look
    different to me")
  * If you fit a line (calibration curve, Beer-Lambert, rotational
    spectrum regression...), what is the UNCERTAINTY on the slope and
    intercept, not just their best-fit values?

You will use these functions in your OWN reports wherever you report a
number with real experimental data behind it -- not just in this file.

Run with:  python exercise7_uncertainty.py
"""

import numpy as np


# ---------------------------------------------------------------------------
# 1. Small-N confidence intervals (Student's t, not a bare standard deviation)
# ---------------------------------------------------------------------------
# A short table of two-sided 95% critical t-values for small degrees of
# freedom (df = n - 1). You may hard-code this table -- do NOT try to derive
# the t-distribution yourself.
T_TABLE_95 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571,
              6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228}


def confidence_interval_95(values):
    """95% confidence interval for the mean of a SMALL sample.

    With few repeats (e.g. the n=3 reproducibility check in Section A) the
    sample standard deviation itself is uncertain, so you must use the
    Student's t critical value for (n-1) degrees of freedom, NOT the
    Normal-distribution value of 1.96 -- using 1.96 with n=3 dramatically
    UNDERSTATES your true uncertainty.

    Parameters
    ----------
    values : array-like
        Repeat measurements of the same quantity.

    Returns
    -------
    mean : float
    half_width : float
        The interval is (mean - half_width, mean + half_width).

    Hints
    -----
    * sample standard deviation: use ``np.std(values, ddof=1)`` (NOT
      ``ddof=0``) -- ddof=1 is the unbiased "sample" estimator, appropriate
      when you don't know the true population std.
    * standard error of the mean: sem = s / sqrt(n)
    * half_width = t_critical * sem, with t_critical from T_TABLE_95[n-1]
      (only works for n <= 11 here; that covers everything in this
      practical).
    """
    # TODO: implement using T_TABLE_95
    raise NotImplementedError("confidence_interval_95")


# ---------------------------------------------------------------------------
# 2. General error propagation (first-order / "delta method")
# ---------------------------------------------------------------------------
def propagate_product(values, uncertainties):
    """Relative-uncertainty propagation for a product/quotient of quantities.

    For z = x1 * x2 * ... * xn (or any quotient, since 1/x has the same
    relative-uncertainty rule), the RELATIVE uncertainties add in quadrature:

        (sigma_z / z)^2 = sum_i (sigma_xi / xi)^2

    This is the rule you need for e.g. k = (2*pi*c*nu)^2 * mu -- nu and mu
    each contribute a relative-uncertainty term.

    Parameters
    ----------
    values : sequence of float
        The xi values (e.g. [nu, mu]).
    uncertainties : sequence of float
        The corresponding sigma_xi, same order.

    Returns
    -------
    rel_uncertainty : float
        sigma_z / |z|, the FRACTIONAL uncertainty on the product/quotient.
        Multiply by your computed z to get the absolute uncertainty sigma_z.

    Hints
    -----
    * Build the array of (sigma_xi/xi), square it, sum, sqrt.
    """
    # TODO: implement the quadrature sum of relative uncertainties
    raise NotImplementedError("propagate_product")


def propagate_power(rel_uncertainty_x, power):
    """Relative uncertainty when a quantity is raised to a power.

    If z = x^n, then sigma_z/z = |n| * sigma_x/x. Useful because
    k = (2*pi*c*nu)^2 * mu has a nu^2 dependence -- the nu-term's
    contribution to k's relative uncertainty is DOUBLED, not just added
    once.

    Returns
    -------
    float
    """
    # TODO: implement
    raise NotImplementedError("propagate_power")


# ---------------------------------------------------------------------------
# 3. Weighted/simple linear regression WITH uncertainties on slope/intercept
# ---------------------------------------------------------------------------
def linregress_with_uncertainty(x, y):
    """Ordinary least-squares fit y = m*x + b, with standard errors on m, b.

    numpy's plain ``polyfit`` gives you best-fit m and b but throws away the
    uncertainty information. Here you recover it from the fit residuals.

    Parameters
    ----------
    x, y : array-like, same length n (n >= 3).

    Returns
    -------
    m, b : float
        Best-fit slope and intercept.
    se_m, se_b : float
        Standard errors (1-sigma) on the slope and intercept.

    Method
    ------
    1. Fit m, b with ``np.polyfit(x, y, 1)``.
    2. Compute residuals ``resid = y - (m*x + b)``.
    3. Residual variance ``s2 = sum(resid**2) / (n - 2)`` (n-2 because two
       parameters, m and b, were fit from the data).
    4. ``se_m = sqrt(s2 / sum((x - mean(x))**2))``
    5. ``se_b = se_m * sqrt(sum(x**2) / n)``

    These are the standard OLS formulas (the same ones behind
    ``scipy.stats.linregress``, which you may use to CHECK your answer, but
    implement the formulas yourself first).
    """
    # TODO: implement steps 1-5
    raise NotImplementedError("linregress_with_uncertainty")


# ---------------------------------------------------------------------------
# 4. Two-sample t-test: are two measured values really different?
# ---------------------------------------------------------------------------
def welch_t_test(mean1, sem1, n1, mean2, sem2, n2):
    """Welch's t-test for two independent measured means with their own SEMs.

    Answers: "measurement A came out different from measurement B (or from
    a literature value) -- is that a REAL difference, or could it be
    explained by noise alone?"

    Parameters
    ----------
    mean1, sem1, n1 : the sample mean, standard error of the mean, and
        sample size of measurement 1.
    mean2, sem2, n2 : same for measurement 2. (For comparing against a
        literature value with no uncertainty, set sem2=0, n2=a large number
        e.g. 1000 -- effectively treats it as exact.)

    Returns
    -------
    t_stat : float
        (mean1 - mean2) / sqrt(sem1**2 + sem2**2)
    rule_of_thumb : str
        "likely real difference" if |t_stat| > 2, else "consistent with
        noise" -- a quick, honest rule of thumb (a proper p-value needs the
        Welch-Satterthwaite degrees of freedom, which is out of scope here;
        |t| > ~2 is a good approximate 95% threshold for reasonable n).

    Hints
    -----
    * t_stat = (mean1 - mean2) / sqrt(sem1**2 + sem2**2)
    """
    # TODO: implement
    raise NotImplementedError("welch_t_test")


# ---------------------------------------------------------------------------
# Self-tests -- run `python exercise7_uncertainty.py` to grade yourself.
# Do not modify below this line.
# ---------------------------------------------------------------------------
def _report(name, ok, msg=""):
    tick = "PASS" if ok else "FAIL"
    print(f"[{tick}] {name}" + (f"  --  {msg}" if msg and not ok else ""))
    return ok


def _selftest():
    print("Running exercise7 self-tests...\n")
    results = []

    try:
        vals = [10.1, 9.8, 10.3]
        mean, hw = confidence_interval_95(vals)
        expected_mean = np.mean(vals)
        expected_sem = np.std(vals, ddof=1) / np.sqrt(3)
        expected_hw = 4.303 * expected_sem
        ok = np.isclose(mean, expected_mean) and np.isclose(hw, expected_hw, rtol=1e-3)
        results.append(_report("confidence_interval_95", ok, "check t-table lookup and sem formula"))
    except NotImplementedError:
        results.append(_report("confidence_interval_95", False, "not implemented"))
    except Exception as e:
        results.append(_report("confidence_interval_95", False, f"raised {e!r}"))

    try:
        rel = propagate_product([2.0, 5.0], [0.1, 0.2])
        expected = np.sqrt((0.1/2.0)**2 + (0.2/5.0)**2)
        ok = np.isclose(rel, expected)
        results.append(_report("propagate_product", ok, "quadrature sum wrong"))
    except NotImplementedError:
        results.append(_report("propagate_product", False, "not implemented"))
    except Exception as e:
        results.append(_report("propagate_product", False, f"raised {e!r}"))

    try:
        rel2 = propagate_power(0.05, 2)
        ok = np.isclose(rel2, 0.10)
        results.append(_report("propagate_power", ok, "should scale by |power|"))
    except NotImplementedError:
        results.append(_report("propagate_power", False, "not implemented"))
    except Exception as e:
        results.append(_report("propagate_power", False, f"raised {e!r}"))

    try:
        rng = np.random.default_rng(0)
        x = np.linspace(0, 10, 20)
        y_true = 2.5 * x + 1.0
        y = y_true + rng.normal(0, 0.3, size=x.shape)
        m, b, se_m, se_b = linregress_with_uncertainty(x, y)
        try:
            from scipy import stats
            ref = stats.linregress(x, y)
            ok = (np.isclose(m, ref.slope, rtol=1e-6) and np.isclose(b, ref.intercept, rtol=1e-6)
                  and np.isclose(se_m, ref.stderr, rtol=1e-3))
        except ImportError:
            ok = np.isclose(m, 2.5, atol=0.3) and se_m > 0 and se_b > 0
        results.append(_report("linregress_with_uncertainty", ok, "compare against scipy.stats.linregress"))
    except NotImplementedError:
        results.append(_report("linregress_with_uncertainty", False, "not implemented"))
    except Exception as e:
        results.append(_report("linregress_with_uncertainty", False, f"raised {e!r}"))

    try:
        t1 = welch_t_test(10.0, 0.5, 3, 10.1, 0.5, 3)
        t2 = welch_t_test(10.0, 0.1, 3, 15.0, 0.1, 3)
        ok = (abs(t1) < 2) and (abs(t2) > 2)
        results.append(_report("welch_t_test", ok, "check formula and threshold logic"))
    except NotImplementedError:
        results.append(_report("welch_t_test", False, "not implemented"))
    except Exception as e:
        results.append(_report("welch_t_test", False, f"raised {e!r}"))

    passed = sum(bool(r) for r in results)
    print(f"\n{passed}/{len(results)} checks passed.")
    if passed == len(results):
        print("All good -- use these functions in your report wherever you quote an uncertainty.")
    else:
        print("Keep going: fix the FAIL items above, then re-run.")


if __name__ == "__main__":
    _selftest()
