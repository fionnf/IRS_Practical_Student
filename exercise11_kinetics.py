"""
Exercise 11 -- Watching a reaction happen, in real time
========================================================

Goal
----
Every spectrum you have analysed so far was a snapshot. An ATR crystal will
happily record one spectrum every few seconds while chemistry happens on top
of it, and that turns the spectrometer into a kinetics instrument: you watch
one band shrink and another grow, and extract a rate constant from it.

This is the companion to Section E, the hydrolysis of acetic anhydride:

    (CH3CO)2O  +  H2O  -->  2 CH3COOH

With water in large excess the reaction is pseudo-first-order in anhydride.
The anhydride carbonyl pair near 1820 and 1750 cm^-1 decays while the acid
carbonyl near 1710 cm^-1 grows in.

There are five functions to write, and they are short. Read them in order;
each one feeds the next.

    load_series      a folder of spectra -> one array, with its time axis
    band_area        the area of one band, above a local baseline
    area_series      band_area applied to every time point
    fit_first_order  area(t) -> k, its uncertainty, and the half-life
    find_isosbestic  the wavenumber where the spectra all cross

Before you start
-----------------
Finish `exercise7_uncertainty.py` first: `fit_first_order` uses its
regression routine, so this file will not work until that one does.

You need no data of your own to practise. If the folders `kinetics_298K/`
and `kinetics_308K/` are not there, they are generated for you the first time
you run this.

Run with:  python exercise11_kinetics.py

WHICH QUESTIONS THIS ANSWERS
----------------------------
Section E, Q1 to Q5

    STEP 1, overlay the run          ->  Section E Q1
    STEP 2, the isosbestic point     ->  Section E Q2
    STEP 3, k and the half-life      ->  Section E Q3
    STEP 4, residuals and the refit  ->  Section E Q4
    STEP 5, activation energy        ->  Section E Q5

The manual's question numbers are the only ones that count. This file used to
carry its own Q1, Q2, Q3 that meant something different from the manual's, so
those are now plain bullets under each step.
"""

import os

import numpy as np
import matplotlib.pyplot as plt

import irtools as ir
import exercise7_uncertainty as unc

# Band windows for this reaction, in cm^-1. Adjust them to YOUR spectra: these
# are sensible starting values, not gospel.
ANHYDRIDE_BAND = (1780, 1860)     # the 1820 C=O of the anhydride
ACID_BAND = (1680, 1740)          # the 1710 C=O of the acid product
# An isosbestic point lies BETWEEN the band that falls and the band that
# rises, so search between the acid C=O at 1710 and the anhydride C=O at 1750.
ISOSBESTIC_WINDOW = (1710, 1760)


# ---------------------------------------------------------------------------
# 1. Loading a whole run
# ---------------------------------------------------------------------------
def load_series(folder):
    """Load one time-resolved run from ``folder``.

    The folder holds one ``.dpt`` file per time point plus a ``times.csv``
    listing them, which is what the instrument writes out:

        filename,time_s
        spec_000.dpt,0.0
        spec_001.dpt,15.0

    Reading the times from that file rather than assuming a constant interval
    matters, because acquisition is never perfectly periodic.

    Parameters
    ----------
    folder : str
        Directory containing the run.

    Returns
    -------
    wn : ndarray, shape (n_points,)
        Wavenumber axis, taken from the first file.
    A : ndarray, shape (n_times, n_points)
        Absorbance, one ROW per time point.
    t : ndarray, shape (n_times,)
        Acquisition time in seconds.

    Hints
    -----
    * Read ``times.csv`` with the standard library: skip the header line, then
      split each remaining line on the comma.
    * ``ir.load_dpt(path, column=None)`` gives you both columns of a file.
    * ``np.vstack`` stacks a list of 1-D spectra into the 2-D array you want.
    """
    # TODO: implement me
    raise NotImplementedError("load_series")


# ---------------------------------------------------------------------------
# 2. The area of one band
# ---------------------------------------------------------------------------
def band_area(wn, A, lo, hi):
    """Integrated area of the band between ``lo`` and ``hi`` cm^-1.

    Peak HEIGHT is easy but fragile: it moves if the band shifts or broadens.
    Integrated AREA is the more robust observable for kinetics, and it is what
    stays proportional to concentration when a band changes shape as well as
    size.

    Subtract a straight local baseline first: draw a line between the
    absorbance at ``lo`` and the absorbance at ``hi``, and integrate only what
    lies above it. Without this, a drifting baseline is indistinguishable from
    reaction, and the ATR crystal does drift as the sample warms.

    Parameters
    ----------
    wn : ndarray
        Wavenumber axis. It may run either way, low-to-high or high-to-low;
        your code must cope with both, because instruments write both.
    A : ndarray
        Absorbance for ONE time point, same length as ``wn``.
    lo, hi : float
        Integration limits in cm^-1, with ``lo < hi``.

    Returns
    -------
    float
        The baseline-corrected area. Always positive for a real band.

    Hints
    -----
    * Select the window with a boolean mask: ``(wn >= lo) & (wn <= hi)``.
    * For the baseline, ``np.interp`` needs an ASCENDING x, so sort the window
      first, or use ``np.argsort``.
    * Integrate with ``np.trapezoid`` (``np.trapz`` on older NumPy). It returns
      a negative area on a descending axis, so take ``abs`` of the result.
    """
    # TODO: implement me
    raise NotImplementedError("band_area")


# ---------------------------------------------------------------------------
# 3. That band, at every time point
# ---------------------------------------------------------------------------
def area_series(wn, A, lo, hi):
    """Apply :func:`band_area` to every row of ``A``.

    Returns a 1-D array of areas, one per time point, in the same order as the
    rows. This is a two-line function; a list comprehension over the rows and
    ``np.array`` around it is the whole thing.
    """
    # TODO: implement me
    raise NotImplementedError("area_series")


# ---------------------------------------------------------------------------
# 4. The rate constant
# ---------------------------------------------------------------------------
def fit_first_order(t, area):
    """Fit ``area(t) = area0 * exp(-k t)`` and return everything it implies.

    Taking logs turns the exponential into a straight line,

        ln(area) = ln(area0) - k * t

    so an ordinary linear regression gives you both parameters and, through
    ``unc.linregress_with_uncertainty``, honest standard errors on them.

    Parameters
    ----------
    t : array-like
        Times in seconds.
    area : array-like
        Band areas at those times. All must be POSITIVE, or the log is
        undefined; drop any non-positive point before fitting and say in your
        report how many you dropped.

    Returns
    -------
    dict
        With keys ``k``, ``k_err`` (s^-1), ``area0``, and ``half_life``,
        ``half_life_err`` (s). One call gives you every number the report
        asks for, so you never have to remember a tuple order.

    Hints
    -----
    * ``fit = unc.linregress_with_uncertainty(t, np.log(area))``.
    * The slope is ``-k``, so ``k = -fit['slope']`` and
      ``k_err = fit['slope_err']``.
    * ``area0 = exp(fit['intercept'])``.
    * ``half_life = ln(2)/k``. Since it is inversely proportional to k, its
      RELATIVE uncertainty equals that of k: ``half_life_err =
      half_life * k_err / k``.

    Note on the method
    ------------------
    Log-linearising is not free: it weights the small, noisy, late-time points
    far more heavily than a direct fit to the exponential would. That is a
    real bias, not a technicality, and the report asks you to measure how much
    it moves your answer.
    """
    # TODO: implement me
    raise NotImplementedError("fit_first_order")


# ---------------------------------------------------------------------------
# 5. The isosbestic point
# ---------------------------------------------------------------------------
def find_isosbestic(wn, A, lo, hi):
    """Find the wavenumber in ``[lo, hi]`` where every spectrum has the same
    absorbance.

    If the whole run is described by ONE changing quantity -- the extent of
    reaction -- then every spectrum is a weighted sum of the same two
    end-member spectra, and there is a wavenumber where those two end members
    happen to absorb equally. Every spectrum passes through that point. It is
    strong evidence that one reactant goes cleanly to one product with no
    accumulating intermediate, and its ABSENCE is the interesting result.

    Parameters
    ----------
    wn, A : as returned by :func:`load_series`.
    lo, hi : float
        The window to search, in cm^-1.

    Returns
    -------
    float
        The wavenumber in the window where the spread across time points is
        smallest.

    Hints
    -----
    * The spread at each wavenumber is ``A.std(axis=0)`` -- one number per
      column. Take it over the window only.
    * ``np.argmin`` gives you the index; convert it back to a wavenumber.

    Why the window is an argument and not the whole spectrum
    --------------------------------------------------------
    Search everywhere and you will find the flat baseline, where every
    spectrum agrees because nothing is happening there. Search across the two
    anhydride bands and you will find the quiet valley between them, which is
    not a crossing either. Neither is an isosbestic point. Restricting the
    search to the region between the falling band and the rising one is what
    makes the answer mean something -- so be ready to justify your window in
    the report.
    """
    # TODO: implement me
    raise NotImplementedError("find_isosbestic")


# ---------------------------------------------------------------------------
# Putting it together
# ---------------------------------------------------------------------------
def main():
    """Work through your own run, or the practice run if you have no data yet."""
    folder = "kinetics_298K"          # swap for your own run
    wn, A, t = load_series(folder)
    print(f"{A.shape[0]} spectra, {A.shape[1]} points each, "
          f"t = 0 to {t[-1]:.0f} s")

    # -----------------------------------------------------------------
    # STEP 1 -- look before you fit.
    #   Overlay every tenth spectrum. You should SEE the anhydride pair at
    #   1820/1750 fall and the acid at 1710 rise.
    # -----------------------------------------------------------------
    plt.figure()
    for i in range(0, len(t), 10):
        plt.plot(wn, A[i], label=f"{t[i]:.0f} s")
    plt.xlim(1900, 1600)
    plt.xlabel("wavenumber / cm$^{-1}$")
    plt.ylabel("absorbance")
    plt.legend(fontsize="small")
    plt.title("Hydrolysis of acetic anhydride, followed on the ATR")

    # -----------------------------------------------------------------
    # STEP 2 -- the isosbestic point.
    # -----------------------------------------------------------------
    iso = find_isosbestic(wn, A, *ISOSBESTIC_WINDOW)
    print(f"isosbestic point at {iso:.0f} cm^-1")
    plt.axvline(iso, color="k", ls=":", lw=1)

    # -----------------------------------------------------------------
    # STEP 3 -- the rate constant.
    # -----------------------------------------------------------------
    areas = area_series(wn, A, *ANHYDRIDE_BAND)
    fit = fit_first_order(t, areas)
    print(f"k         = {fit['k']:.3e} +/- {fit['k_err']:.1e} s^-1")
    print(f"t_1/2     = {fit['half_life']:.0f} +/- {fit['half_life_err']:.0f} s")

    # -----------------------------------------------------------------
    # STEP 4 -- be honest about the fit.
    #   Plot the residuals of ln(area) against time. Scattered about zero, or
    #   curved? Then refit with the late, noise-dominated points dropped and
    #   report how much k moves. If it moves by more than its own uncertainty,
    #   your first fit was being driven by noise.
    # -----------------------------------------------------------------
    resid = np.log(areas) - (np.log(fit["area0"]) - fit["k"] * t)
    plt.figure()
    plt.axhline(0, color="k", lw=0.8)
    plt.plot(t, resid, "o")
    plt.xlabel("time / s")
    plt.ylabel("residual in ln(area)")
    plt.title("Is it really first order?")

    # -----------------------------------------------------------------
    # STEP 5 -- activation energy, if you ran a second temperature.
    #   Two-point Arrhenius: ln(k2/k1) = -(Ea/R) (1/T2 - 1/T1). Propagate both
    #   rate-constant uncertainties into Ea. Two points is the bare minimum,
    #   so say plainly what that does to the reliability of the answer.
    # -----------------------------------------------------------------
    plt.show()


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

    # load_series: on the practice run, which is generated if absent
    try:
        if not os.path.isdir("kinetics_298K"):
            import generate_demo_data
            generate_demo_data.main()
        wn, A, t = load_series("kinetics_298K")
        ok = (A.ndim == 2 and A.shape[0] == len(t) == 61
              and A.shape[1] == len(wn) and t[0] == 0.0 and t[1] == 15.0)
        results.append(_report("load_series", ok,
                               "expected 61 spectra with t = 0, 15, 30, ... s"))
    except NotImplementedError:
        results.append(_report("load_series", False, "not implemented"))
    except Exception as e:
        results.append(_report("load_series", False, f"raised {e!r}"))

    # band_area: a triangle of known area sitting on a sloping baseline
    try:
        wn = np.linspace(1600, 1800, 401)
        peak = np.clip(1.0 - np.abs(wn - 1700) / 50.0, 0, None)   # area = 50
        slope = 0.3 + 0.002 * (wn - 1600)
        a = band_area(wn, peak + slope, 1650, 1750)
        ok = np.isclose(a, 50.0, rtol=0.02)
        results.append(_report("band_area", ok,
                               "expected ~50 after the baseline is removed"))
    except NotImplementedError:
        results.append(_report("band_area", False, "not implemented"))
    except Exception as e:
        results.append(_report("band_area", False, f"raised {e!r}"))

    # the same band on a descending axis must give the same answer
    try:
        wn = np.linspace(1800, 1600, 401)
        peak = np.clip(1.0 - np.abs(wn - 1700) / 50.0, 0, None)
        a = band_area(wn, peak, 1650, 1750)
        ok = np.isclose(a, 50.0, rtol=0.02)
        results.append(_report("band_area (descending axis)", ok,
                               "must handle a high->low wavenumber axis"))
    except NotImplementedError:
        results.append(_report("band_area (descending axis)", False,
                               "not implemented"))
    except Exception as e:
        results.append(_report("band_area (descending axis)", False,
                               f"raised {e!r}"))

    # area_series: three identical rows must give three identical areas
    try:
        wn = np.linspace(1600, 1800, 401)
        peak = np.clip(1.0 - np.abs(wn - 1700) / 50.0, 0, None)
        A = np.vstack([peak, 0.5 * peak, 0.25 * peak])
        got = area_series(wn, A, 1650, 1750)
        ok = (len(got) == 3 and np.allclose(got, [50.0, 25.0, 12.5], rtol=0.02))
        results.append(_report("area_series", ok,
                               "areas should scale with the rows: 50, 25, 12.5"))
    except NotImplementedError:
        results.append(_report("area_series", False, "not implemented"))
    except Exception as e:
        results.append(_report("area_series", False, f"raised {e!r}"))

    # fit_first_order on a clean exponential
    try:
        t = np.linspace(0, 300, 40)
        k_true, a0_true = 0.008, 12.0
        fit = fit_first_order(t, a0_true * np.exp(-k_true * t))
        ok = (np.isclose(fit["k"], k_true, rtol=1e-6)
              and np.isclose(fit["area0"], a0_true, rtol=1e-6)
              and np.isclose(fit["half_life"], np.log(2) / k_true, rtol=1e-6)
              and fit["k_err"] >= 0)
        results.append(_report("fit_first_order", ok,
                               "should recover k, area0 and the half-life exactly"))
    except NotImplementedError:
        results.append(_report("fit_first_order", False, "not implemented"))
    except Exception as e:
        results.append(_report("fit_first_order", False, f"raised {e!r}"))

    # half-life uncertainty must keep the relative uncertainty of k
    try:
        t = np.linspace(0, 300, 40)
        rng = np.random.default_rng(0)
        area = 12.0 * np.exp(-0.008 * t) * (1 + rng.normal(0, 0.02, t.shape))
        fit = fit_first_order(t, area)
        ok = np.isclose(fit["half_life_err"] / fit["half_life"],
                        fit["k_err"] / fit["k"], rtol=1e-6)
        results.append(_report("fit_first_order (half-life error)", ok,
                               "t_1/2 and k must share a relative uncertainty"))
    except NotImplementedError:
        results.append(_report("fit_first_order (half-life error)", False,
                               "not implemented"))
    except Exception as e:
        results.append(_report("fit_first_order (half-life error)", False,
                               f"raised {e!r}"))

    # find_isosbestic: two end members crossing at a known wavenumber
    try:
        wn = np.linspace(1600, 1900, 601)
        a = np.exp(-((wn - 1820) / 30.0) ** 2)
        b = np.exp(-((wn - 1710) / 30.0) ** 2)
        A = np.vstack([(1 - x) * a + x * b for x in np.linspace(0, 1, 11)])
        # the two end members cross midway between the band centres
        got = find_isosbestic(wn, A, 1740, 1800)
        ok = abs(got - 1765.0) < 10.0
        results.append(_report("find_isosbestic", ok,
                               "these two bands cross near 1765 cm^-1"))
    except NotImplementedError:
        results.append(_report("find_isosbestic", False, "not implemented"))
    except Exception as e:
        results.append(_report("find_isosbestic", False, f"raised {e!r}"))

    passed = sum(bool(r) for r in results)
    print(f"\n{passed}/{len(results)} checks passed.")
    if passed == len(results):
        print("All good -- now run main() on your own run.")
    else:
        print("Keep going: fix the FAIL items above, then re-run.")


if __name__ == "__main__":
    import sys

    if "run" in sys.argv[1:]:
        main()
    else:
        _selftest()
        print("\nTo run the analysis on your own data:  python exercise11_kinetics.py run")
