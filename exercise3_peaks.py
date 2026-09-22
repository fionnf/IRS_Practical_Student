"""
Exercise 3 -- Peaks, baselines and reading the spectrum like a chemist
======================================================================

Goal
----
A spectrum is only useful once you can (a) flatten its baseline, (b) locate
its peaks automatically, and (c) assign those peaks to chemical groups.

New tools you may use here: `scipy.signal.find_peaks`. Everything else builds
on your own `irtools` + `compute_spectrum` from exercise 2.

Run with:  python exercise3_peaks.py

WHAT YOU DO IN THIS FILE
------------------------
Three short functions, in this order:

    baseline_correct(wn, A)   flatten a sloping background
    find_bands(wn, A)         locate the peaks
    assign(peak_wn)           look each peak up in the correlation table

    python exercise3_peaks.py        <- grade yourself
    python exercise3_peaks.py run    <- run it on your data
"""

import numpy as np
import matplotlib.pyplot as plt

import irtools as ir
from exercise2_spectrum import compute_spectrum, K, N

# A short IR correlation table (approximate ranges, cm^-1).
# Use it in STEP 4 to assign your peaks. Extend it if you like.
CORRELATION_TABLE = [
    ("O-H stretch (alcohol, broad)", 3200, 3550),
    ("C-H stretch (sp3)",            2850, 2990),
    ("C=O stretch (carbonyl)",       1680, 1760),
    ("O-H bend / C-H bend",          1350, 1480),
    ("C-O stretch",                  1000, 1260),
]


def baseline_correct(wn, A):
    """Remove a slowly-varying baseline from an absorbance spectrum.

    Real spectra drift up and down due to scattering, sloping backgrounds,
    etc. A simple, transparent method (implement THIS one):

      * Pick the lowest ``m`` percent of absorbance points as "baseline"
        anchor points (they are unlikely to sit on a peak).
      * Fit a low-order polynomial (degree 2 or 3) through those anchors as a
        function of wavenumber.
      * Subtract the fitted polynomial from A.

    Parameters
    ----------
    wn : ndarray
        Wavenumber axis.
    A : ndarray
        Matching absorbance spectrum.

    Every function in this practical that takes both a wavenumber axis and a
    spectrum takes them in that order, ``(wn, A)``. Passing them the other way
    round does not raise: it silently fits a baseline through nonsense.

    Returns
    -------
    ndarray
        Baseline-corrected absorbance.

    Hints
    -----
    * ``np.percentile(A, m)`` gives the value below which m% of points lie.
    * ``np.polyfit(x, y, deg)`` and ``np.polyval`` fit/evaluate a polynomial.
    * Keep it simple; you do not need a perfect baseline, just a flatter one.
    """
    # TODO: implement the simple baseline correction described above
    raise NotImplementedError("baseline_correct: fit & subtract a low-order baseline")


def find_bands(wn, A, height=None, distance=None):
    """Return the wavenumbers and heights of the absorbance peaks.

    Use ``scipy.signal.find_peaks``. You will need to choose sensible
    ``height`` and ``distance`` (minimum spacing in samples) so that you pick
    up real bands but not every noise wiggle.

    Returns
    -------
    peak_wn : ndarray   wavenumbers of the detected peaks
    peak_A  : ndarray   absorbance at those peaks
    """
    # TODO: from scipy.signal import find_peaks
    # TODO: idx, _ = find_peaks(A, height=height, distance=distance)
    # TODO: return wn[idx], A[idx]
    raise NotImplementedError("find_bands: detect peaks with scipy.signal.find_peaks")


def assign(peak_wn):
    """Match each peak wavenumber to entries in CORRELATION_TABLE.

    Returns
    -------
    list of (wavenumber, [matching group labels])
    """
    # TODO: for each peak, collect every table row whose (low, high) range
    #       contains that wavenumber; return the pairs.
    raise NotImplementedError("assign: map peaks to functional groups")


def main():
    # -----------------------------------------------------------------
    # STEP 1  --  Recompute the ethanol absorbance spectrum.
    # -----------------------------------------------------------------
    e_rifg = None   # TODO: ir.load_dpt("ethanol_rifg.dpt", column=1)
    e_sifg = None   # TODO
    if e_rifg is None:
        raise SystemExit("Load the ethanol interferograms first.")
    wn, T = compute_spectrum(e_rifg, e_sifg, N, K)
    A = ir.absorbance(T)

    # Restrict to the chemically useful fingerprint + functional-group region.
    mask = (wn >= 500) & (wn <= 4000)
    wn, A = wn[mask], A[mask]

    # -----------------------------------------------------------------
    # STEP 2  --  Baseline correction. Plot before vs after.
    #   Q1. What artefacts in the raw absorbance did the baseline correction
    #       remove? Did it distort any real peaks?
    # -----------------------------------------------------------------
    A_bc = baseline_correct(wn, A)
    # TODO: plot A and A_bc together.

    # -----------------------------------------------------------------
    # STEP 3  --  Peak detection. Mark the peaks on the plot.
    #   Q2. How sensitive is the peak list to your `height`/`distance`
    #       choices? Give the values you settled on and why.
    # -----------------------------------------------------------------
    peak_wn, peak_A = find_bands(wn, A_bc, height=None, distance=None)
    # TODO: plot A_bc and overlay the detected peaks (e.g. plt.scatter).

    # -----------------------------------------------------------------
    # STEP 4  --  Assign the peaks.
    #   Q3. Produce a table: peak position -> assigned group. Are all of
    #       ethanol's expected bands present (O-H, C-H, C-O)? Any unexpected
    #       peaks, e.g. atmospheric CO2 near 2350 cm^-1 or water vapour?
    # -----------------------------------------------------------------
    for w, groups in assign(peak_wn):
        label = ", ".join(groups) if groups else "(unassigned)"
        print(f"{w:7.1f} cm^-1  ->  {label}")

    # -----------------------------------------------------------------
    # STEP 5 (challenge)  --  Compare two substances.
    # If you have a second sample's data (e.g. acetone: has a strong C=O near
    # 1715 cm^-1 that ethanol lacks), run it through the same pipeline and
    # plot both spectra stacked.
    #   Q4. Name one band that lets you tell the two substances apart at a
    #       glance, and say which bond it belongs to.
    # -----------------------------------------------------------------
    # TODO (optional): repeat for a second sample and overlay.

    print("\nExercise 3 complete once the assignment table prints and Q1-Q4 are answered.")


# ---------------------------------------------------------------------------
# Self-tests -- run `python exercise3_peaks.py` to grade yourself.
# Do not modify below this line.
# ---------------------------------------------------------------------------
def _report(name, ok, msg=""):
    tick = "PASS" if ok else "FAIL"
    print(f"[{tick}] {name}" + (f"  --  {msg}" if msg and not ok else ""))
    return ok


def _selftest():
    print("Running exercise3 self-tests...\n")
    results = []
    # a peak on a sloping background: the background must go
    try:
        wn = np.linspace(600, 1800, 1201)
        peak = np.exp(-((wn - 1700) / 12.0) ** 2)
        A = peak + 0.4 + 3e-4 * (wn - 600)
        out = baseline_correct(wn, A)
        edge = (wn < 1400)
        ok = abs(np.median(out[edge])) < 0.05
        results.append(_report("baseline_correct", ok, "the flat parts should come back to about zero"))
    except NotImplementedError:
        results.append(_report("baseline_correct", False, "not implemented"))
    except Exception as e:
        results.append(_report("baseline_correct", False, f"raised {e!r}"))

    # two well-separated bands must both be found
    try:
        wn = np.linspace(600, 1800, 1201)
        A = (np.exp(-((wn - 1700) / 12.0) ** 2)
             + 0.8 * np.exp(-((wn - 1100) / 12.0) ** 2))
        peak_wn, peak_A = find_bands(wn, A, height=0.3, distance=10)
        found = np.sort(np.asarray(peak_wn))
        ok = (len(found) == 2
              and abs(found[0] - 1100) < 10 and abs(found[1] - 1700) < 10)
        results.append(_report("find_bands", ok, "expected peaks near 1100 and 1700 cm^-1"))
    except NotImplementedError:
        results.append(_report("find_bands", False, "not implemented"))
    except Exception as e:
        results.append(_report("find_bands", False, f"raised {e!r}"))

    # assign returns one entry per peak, each with a list of labels
    try:
        out = assign(np.array([1700.0, 1100.0]))
        ok = (len(out) == 2
              and all(len(row) == 2 and isinstance(row[1], list) for row in out))
        results.append(_report("assign", ok, "expected one (wavenumber, [labels]) pair per input peak"))
    except NotImplementedError:
        results.append(_report("assign", False, "not implemented"))
    except Exception as e:
        results.append(_report("assign", False, f"raised {e!r}"))


    passed = sum(bool(r) for r in results)
    print(f"\n{passed}/{len(results)} checks passed.")
    if passed == len(results):
        print("All good -- now run:  python exercise3_peaks.py run")
    else:
        print("Keep going: fix the FAIL items above, then re-run.")


if __name__ == "__main__":
    import sys

    if "run" in sys.argv[1:]:
        main()
    else:
        _selftest()
        print("\nTo run the analysis on your own data:  python exercise3_peaks.py run")
