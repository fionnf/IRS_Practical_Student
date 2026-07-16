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


def baseline_correct(A, wn):
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
    A : ndarray
        Absorbance spectrum.
    wn : ndarray
        Matching wavenumber axis.

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


def find_bands(A, wn, height=None, distance=None):
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
    A_bc = baseline_correct(A, wn)
    # TODO: plot A and A_bc together.

    # -----------------------------------------------------------------
    # STEP 3  --  Peak detection. Mark the peaks on the plot.
    #   Q2. How sensitive is the peak list to your `height`/`distance`
    #       choices? Give the values you settled on and why.
    # -----------------------------------------------------------------
    peak_wn, peak_A = find_bands(A_bc, wn, height=None, distance=None)
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


if __name__ == "__main__":
    main()
