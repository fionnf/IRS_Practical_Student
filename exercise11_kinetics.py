"""
Exercise 11 -- Following a reaction in real time with ATR-FTIR
===============================================================

Goal
----
Every spectrum you have analysed so far was a snapshot. An ATR crystal will
happily record one spectrum every few seconds while chemistry happens on top
of it, and that turns the spectrometer into a kinetics instrument: you watch
one band shrink and another grow, and extract a rate constant.

This is the computational companion to Section J of the practical. You will:

  * load a whole time series of spectra,
  * integrate a chosen band at each time point (with a local baseline),
  * fit the decay to a first-order rate law and get k with a real uncertainty,
  * check the order of the reaction rather than assuming it.

Before you start
-----------------
Complete `exercise7_uncertainty.py` first -- this file uses its regression
and error-propagation tools.

Your data should be a folder of `.dpt` files, one per time point, plus the
acquisition time of each. If your instrument names them sequentially and
records a constant interval, the times are just `n * interval`; if it stamps
each file, read the stamps and use those (they are more honest, because
acquisition is never perfectly periodic).

Run with:  python exercise11_kinetics.py
"""

import numpy as np
import matplotlib.pyplot as plt

import irtools as ir
import exercise7_uncertainty as unc


# ---------------------------------------------------------------------------
# 1. Loading a time series
# ---------------------------------------------------------------------------
def load_series(paths, times):
    """Load a list of absorbance files into one array, with their times.

    Parameters
    ----------
    paths : list of str
        One ``.dpt`` file per time point, in order. Each is a two-column
        (wavenumber, absorbance) file.
    times : array-like
        Acquisition time of each spectrum, in SECONDS, measured from the start
        of the reaction (not from when you started the instrument -- state your
        zero and be consistent).

    Returns
    -------
    wn : ndarray, shape (n_points,)
        The wavenumber axis (taken from the first file).
    A : ndarray, shape (n_times, n_points)
        Absorbance, one row per time point.
    t : ndarray, shape (n_times,)

    Hints
    -----
    * ``ir.load_dpt(path, column=None)`` gives you both columns.
    * Check that every file shares the same wavenumber axis; if the instrument
      changed resolution mid-series they will not, and you must interpolate
      (you wrote ``common_grid`` for this in exercise 6).
    """
    # TODO: implement me
    raise NotImplementedError("load_series")


# ---------------------------------------------------------------------------
# 2. Integrating a band, with a local baseline
# ---------------------------------------------------------------------------
def band_area(wn, A, lo, hi):
    """Integrated area of the band between ``lo`` and ``hi`` cm^-1.

    Peak HEIGHT is easy but fragile: it moves if the band shifts or broadens.
    Integrated AREA is the more robust observable for kinetics, and it is what
    is proportional to concentration when a band changes shape as well as size.

    Subtract a straight local baseline first: draw a line between the
    absorbance at ``lo`` and at ``hi``, and integrate what lies above it.
    Without this, a drifting baseline is indistinguishable from reaction.

    Parameters
    ----------
    wn : ndarray            wavenumber axis (may run either direction).
    A : ndarray             absorbance, same length.
    lo, hi : float          integration limits in cm^-1 (lo < hi).

    Returns
    -------
    float : the baseline-corrected integrated area.

    Hints
    -----
    * Mask with ``(wn >= lo) & (wn <= hi)``.
    * Sort the masked wavenumber/absorbance together so the axis is ascending
      before you integrate, or ``np.trapz`` will return a negative area.
    * Straight baseline through the two endpoints:
      ``base = A0 + (A1 - A0) * (w - w0) / (w1 - w0)``.
    * Trapezoidal integration is ``np.trapezoid(y, x)`` on NumPy 2.0 and
      later. Older NumPy spells the same function ``np.trapz``; if you want
      your code to run on both, pick it up once at the top of the file with
      ``trapz = getattr(np, "trapezoid", None) or np.trapz``.
    """
    # TODO: implement me
    raise NotImplementedError("band_area")


def area_series(wn, A, lo, hi):
    """Apply :func:`band_area` to every row of ``A``. Returns a 1-D array."""
    # TODO: implement me
    raise NotImplementedError("area_series")


# ---------------------------------------------------------------------------
# 3. Fitting a first-order rate law
# ---------------------------------------------------------------------------
def fit_first_order(t, area):
    """Fit area(t) = area0 * exp(-k t) by linearising, and return k +/- sigma.

    Taking logs turns the exponential into a straight line:

        ln(area) = ln(area0) - k t

    so an ordinary least-squares fit of ``ln(area)`` against ``t`` has slope
    ``-k``. Reuse ``unc.linregress_with_uncertainty`` so you get the standard
    error on the slope for free.

    Parameters
    ----------
    t : ndarray       times, seconds.
    area : ndarray    integrated band areas, same length. Must be positive.

    Returns
    -------
    k, se_k : float   rate constant in s^-1 and its 1-sigma uncertainty.
    area0, se_area0 : float
        The fitted area at t=0 and its uncertainty (from the intercept:
        ``area0 = exp(intercept)``, and by propagation
        ``se_area0 = area0 * se_intercept``).

    A WARNING worth understanding
    -----------------------------
    Linearising is convenient but it re-weights your data: taking logs makes
    the SMALL, late-time, noisiest points count as much as the large early
    ones. It is the standard undergraduate treatment and it is fine here, but
    if any of your areas approach the noise floor, drop those points and say
    that you did (Q4 asks about exactly this).
    """
    # TODO: implement me
    raise NotImplementedError("fit_first_order")


def half_life(k, se_k):
    """t_half = ln(2)/k, with propagated uncertainty.

    Since t_half depends on k^(-1), the RELATIVE uncertainty is unchanged:
    use ``unc.propagate_power(se_k/k, 1)``.

    Returns
    -------
    t_half, se_t_half : float, in seconds.
    """
    # TODO: implement me
    raise NotImplementedError("half_life")


# ---------------------------------------------------------------------------
# 4. Is it actually first order?
# ---------------------------------------------------------------------------
def order_test(t, area):
    """Compare first-order and second-order linearisations of the same data.

    A decaying curve looks broadly similar for several rate laws, so "it went
    down smoothly" is not evidence of first order. Test it:

      * first order  -> ln(area)  is linear in t
      * second order -> 1/area    is linear in t

    Fit BOTH with ``unc.linregress_with_uncertainty`` and compare how well each
    describes the data, using the RMS residual of each fit (smaller is better).

    Returns
    -------
    dict with keys "first" and "second", each a dict containing
    ``slope``, ``se_slope`` and ``rms_resid``.

    Hints
    -----
    * Compute residuals yourself: ``y - (m*t + b)`` for each model.
    * Do not compare the two R^2 values directly -- they are computed on
      different y-variables (ln(area) vs 1/area) and are not comparable.
      The RMS residual has the same problem in principle, so ALSO look at
      whether either residual plot shows systematic curvature. That is the
      real test, and Q5 asks you to plot it.
    """
    # TODO: implement me
    raise NotImplementedError("order_test")


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------
def main():
    # -----------------------------------------------------------------
    # STEP 1 -- load your series.
    # Replace with your own filenames and measured times.
    # -----------------------------------------------------------------
    paths = []   # TODO: e.g. [f"kinetics_{i:03d}.dpt" for i in range(30)]
    times = []   # TODO: e.g. np.arange(30) * 15.0   (seconds)
    if not paths:
        raise SystemExit("List your time-series files and their times first.")

    wn, A, t = load_series(paths, times)
    print(f"Loaded {len(t)} spectra spanning {t[-1]-t[0]:.0f} s")

    # -----------------------------------------------------------------
    # STEP 2 -- pick your bands and plot the whole series.
    #
    # Plot every spectrum on one axis, coloured by time (a colormap works
    # well). You should be able to SEE the isosbestic behaviour if there is
    # any.
    #   Q1. Which band decays and which grows? Assign both to the species you
    #       expect from the chemistry. Is there an isosbestic point -- a
    #       wavenumber where all the curves cross? What does its presence (or
    #       absence) tell you about how many species are present?
    # -----------------------------------------------------------------
    lo_decay, hi_decay = None, None   # TODO: integration limits for the decaying band
    lo_grow, hi_grow = None, None     # TODO: and for the growing band
    # TODO: your stacked time-series plot here

    # -----------------------------------------------------------------
    # STEP 3 -- integrate and fit.
    #   Q2. Plot the integrated area of your decaying band against time, and
    #       overlay the fitted first-order curve. Report k +/- sigma_k in s^-1
    #       and the half-life with its uncertainty, correctly rounded.
    #   Q3. Do the same for the GROWING band. Should the two rate constants
    #       agree? Compare them with `unc.welch_t_test` and comment on what a
    #       significant difference would imply about the mechanism.
    # -----------------------------------------------------------------
    areas = area_series(wn, A, lo_decay, hi_decay)
    k, se_k, a0, se_a0 = fit_first_order(t, areas)
    th, se_th = half_life(k, se_k)
    print(f"k = {k:.3e} +/- {se_k:.1e} s^-1")
    print(f"t_1/2 = {th:.1f} +/- {se_th:.1f} s")

    # -----------------------------------------------------------------
    # STEP 4 -- honesty about the fit.
    #   Q4. How many of your late-time points are within a factor of ~3 of
    #       your measured noise floor (Section A)? Refit with those points
    #       excluded and report how much k changes. If it changes by more than
    #       its own uncertainty, your original fit was being driven by noise.
    #   Q5. Plot the residuals of the first-order fit against time. Are they
    #       scattered randomly about zero, or do they curve? Then run
    #       `order_test` and report both linearisations. On the evidence, is
    #       first order the right rate law -- and how confident can you
    #       honestly be from a single run?
    # -----------------------------------------------------------------
    res = order_test(t, areas)
    print("first-order  slope %.3e +/- %.1e, rms %.4f"
          % (res["first"]["slope"], res["first"]["se_slope"], res["first"]["rms_resid"]))
    print("second-order slope %.3e +/- %.1e, rms %.4f"
          % (res["second"]["slope"], res["second"]["se_slope"], res["second"]["rms_resid"]))

    # -----------------------------------------------------------------
    # STEP 5 (if you ran the reaction at two temperatures)
    #   Q6. From k at two temperatures, estimate the activation energy via
    #       the two-point Arrhenius relation
    #           ln(k2/k1) = -(Ea/R) (1/T2 - 1/T1).
    #       Propagate both rate-constant uncertainties into Ea. Two points is
    #       the bare minimum for an Arrhenius analysis -- state clearly what
    #       that does to the reliability of your Ea, and what you would need
    #       to do better.
    # -----------------------------------------------------------------

    print("\nExercise 11 complete once STEPs 1-4 run and Q1-Q5 are answered.")


# ---------------------------------------------------------------------------
# Self-tests -- run `python exercise11_kinetics.py` to grade yourself.
# Do not modify below this line.
# ---------------------------------------------------------------------------
def _report(name, ok, msg=""):
    tick = "PASS" if ok else "FAIL"
    print(f"[{tick}] {name}" + (f"  --  {msg}" if msg and not ok else ""))
    return ok


def _selftest():
    print("Running exercise11 self-tests...\n")
    results = []

    # band_area: a triangle of known area sitting on a sloping baseline
    try:
        wn = np.linspace(1600, 1800, 401)
        peak = np.clip(1.0 - np.abs(wn - 1700) / 50.0, 0, None)   # area = 50
        slope = 0.3 + 0.002 * (wn - 1600)
        a = band_area(wn, peak + slope, 1650, 1750)
        ok = np.isclose(a, 50.0, rtol=0.02)
        results.append(_report("band_area", ok, "expected ~50 after baseline removal"))
    except NotImplementedError:
        results.append(_report("band_area", False, "not implemented"))
    except Exception as e:
        results.append(_report("band_area", False, f"raised {e!r}"))

    # descending wavenumber axis must give the same answer
    try:
        wn = np.linspace(1800, 1600, 401)
        peak = np.clip(1.0 - np.abs(wn - 1700) / 50.0, 0, None)
        a = band_area(wn, peak, 1650, 1750)
        ok = np.isclose(a, 50.0, rtol=0.02)
        results.append(_report("band_area (descending axis)", ok,
                               "must handle a high->low wavenumber axis"))
    except NotImplementedError:
        results.append(_report("band_area (descending axis)", False, "not implemented"))
    except Exception as e:
        results.append(_report("band_area (descending axis)", False, f"raised {e!r}"))

    # fit_first_order on a clean exponential
    try:
        t = np.linspace(0, 300, 40)
        k_true, a0_true = 0.008, 12.0
        area = a0_true * np.exp(-k_true * t)
        k, se_k, a0, se_a0 = fit_first_order(t, area)
        ok = (np.isclose(k, k_true, rtol=1e-6) and np.isclose(a0, a0_true, rtol=1e-6)
              and se_k >= 0)
        results.append(_report("fit_first_order", ok, "should recover k and area0 exactly"))
    except NotImplementedError:
        results.append(_report("fit_first_order", False, "not implemented"))
    except Exception as e:
        results.append(_report("fit_first_order", False, f"raised {e!r}"))

    try:
        th, se_th = half_life(0.008, 0.0004)
        ok = (np.isclose(th, np.log(2) / 0.008, rtol=1e-9)
              and np.isclose(se_th / th, 0.0004 / 0.008, rtol=1e-6))
        results.append(_report("half_life", ok, "relative uncertainty must be preserved"))
    except NotImplementedError:
        results.append(_report("half_life", False, "not implemented"))
    except Exception as e:
        results.append(_report("half_life", False, f"raised {e!r}"))

    # order_test must prefer first order on first-order data
    try:
        t = np.linspace(0, 300, 40)
        area = 12.0 * np.exp(-0.008 * t)
        r = order_test(t, area)
        ok = (r["first"]["rms_resid"] < r["second"]["rms_resid"]
              and np.isclose(-r["first"]["slope"], 0.008, rtol=1e-6))
        results.append(_report("order_test", ok,
                               "first order should fit first-order data better"))
    except NotImplementedError:
        results.append(_report("order_test", False, "not implemented"))
    except Exception as e:
        results.append(_report("order_test", False, f"raised {e!r}"))

    passed = sum(bool(r) for r in results)
    print(f"\n{passed}/{len(results)} checks passed.")
    if passed == len(results):
        print("All good -- now run main() on your own time series.")
    else:
        print("Keep going: fix the FAIL items above, then re-run.")


if __name__ == "__main__":
    _selftest()
