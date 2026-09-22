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

Run with:  python uncertainty.py

WRITTEN FOR YOU -- NOTHING TO IMPLEMENT
---------------------------------------
This is a library the section scripts call, not an exercise. Read the
functions so you know what the numbers you quote actually mean.

WHICH QUESTIONS IT SERVES
----------------------------
Section A, Q10, Q11 and Q12 directly. After that it is used, rather than
answered, nearly everywhere else.

    confidence_interval_95        ->  Section A Q11 and Q12
    linregress_with_uncertainty   ->  Section A Q10; Section B Q1; Section D Q6
    propagate_product / _power    ->  Section A Q10; Section E Q3
    welch_t_test                  ->  Section A Q10 and Q12

Every physical quantity you quote anywhere in the report needs an uncertainty
from this file, so finish it early: Sections B, D, E, G and H all lean on it.
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
    values = np.asarray(values, dtype=float)
    n = len(values)
    mean = np.mean(values)
    sem = np.std(values, ddof=1) / np.sqrt(n)
    half_width = T_TABLE_95[n - 1] * sem
    return mean, half_width


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
    rel = np.array([u / v for v, u in zip(values, uncertainties)])
    return np.sqrt(np.sum(rel ** 2))


# --- WRITTEN FOR YOU: plumbing, not physics. Read it and move on. ---
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
    return abs(power) * rel_uncertainty_x


# ---------------------------------------------------------------------------
# 3. Weighted/simple linear regression WITH uncertainties on slope/intercept
# ---------------------------------------------------------------------------
# --- WRITTEN FOR YOU: plumbing, not physics. Read it and move on. ---
def linregress_with_uncertainty(x, y):
    """Ordinary least-squares fit y = m*x + b, with standard errors on m, b.

    numpy's plain ``polyfit`` gives you best-fit m and b but throws away the
    uncertainty information. Here you recover it from the fit residuals.

    Parameters
    ----------
    x, y : array-like, same length n (n >= 3).

    Returns
    -------
    dict
        With keys ``slope``, ``intercept``, ``slope_err`` and
        ``intercept_err``. A dict rather than a tuple because four unlabelled
        numbers in a row are easy to unpack in the wrong order, and every
        later exercise calls this.

    Method
    ------
    1. Fit m, b with ``np.polyfit(x, y, 1)``.
    2. Compute residuals ``resid = y - (m*x + b)``.
    3. Residual variance ``s2 = sum(resid**2) / (n - 2)`` (n-2 because two
       parameters, m and b, were fit from the data).
    4. ``slope_err = sqrt(s2 / sum((x - mean(x))**2))``
    5. ``intercept_err = slope_err * sqrt(sum(x**2) / n)``
    6. Return them as
       ``{'slope': m, 'intercept': b, 'slope_err': ..., 'intercept_err': ...}``.

    These are the standard OLS formulas (the same ones behind
    ``scipy.stats.linregress``, which you may use to CHECK your answer, but
    implement the formulas yourself first).
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    n = len(x)
    m, b = np.polyfit(x, y, 1)
    resid = y - (m * x + b)
    s2 = np.sum(resid ** 2) / (n - 2)
    se_m = np.sqrt(s2 / np.sum((x - np.mean(x)) ** 2))
    se_b = se_m * np.sqrt(np.sum(x ** 2) / n)
    return {"slope": float(m), "intercept": float(b),
            "slope_err": float(se_m), "intercept_err": float(se_b)}


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
    dict
        With keys ``t`` and ``verdict``. ``t`` is
        ``(mean1 - mean2) / sqrt(sem1**2 + sem2**2)``. ``verdict`` is
        ``"likely real difference"`` when ``abs(t) > 2`` and
        ``"consistent with noise"`` otherwise -- a quick, honest rule of
        thumb. A proper p-value needs the Welch-Satterthwaite degrees of
        freedom, which is out of scope here; |t| > ~2 is a good approximate
        95% threshold for reasonable n.

    Quote the NUMBER in your report, not just the verdict. The verdict is
    there to stop a borderline t being written up as though it settled the
    question.

    Hints
    -----
    * ``t = (mean1 - mean2) / sqrt(sem1**2 + sem2**2)``
    * Return both in one dict, so a caller cannot use the verdict while
      silently ignoring the number.
    """
    t = (mean1 - mean2) / np.sqrt(sem1 ** 2 + sem2 ** 2)
    return {"t": float(t),
            "verdict": ("likely real difference" if abs(t) > 2
                        else "consistent with noise")}



if __name__ == "__main__":
    print(__doc__)
