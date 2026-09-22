"""
Exercise 6 (experimental) -- Quantitative spectral unmixing of a real mixture
==============================================================================

This exercise uses the DATA YOU MEASURE in Section D of the practical (the
xylene-isomer mixture case): two pure-isomer ATR spectra and a series of
binary mixtures at known mole fractions. Section D asks you to compute the
"excess spectrum" (measured minus an assumed ideal linear combination) by
hand for one mixture at a time. Here you do something more powerful: treat
EVERY mixture spectrum as an unknown, and let least-squares regression tell
you the composition -- exactly the technique used in real quantitative IR
analysis of multi-component mixtures.

The physics: if absorbance is additive (Beer-Lambert, no chemical
interaction), a mixture spectrum is a LINEAR COMBINATION of the pure-
component spectra:

    A_mixture(wn)  ~=  x1 * A_pure1(wn)  +  x2 * A_pure2(wn)

At every wavenumber this is one linear equation in the unknowns (x1, x2).
Stack the equation over all wavenumbers and you get an over-determined linear
system -- solve it by least squares to get the best-fit (x1, x2) directly
from the spectrum, with NO peak-picking required.

You need real data for this: your own two pure-isomer ATR absorbance spectra
and your five (or more) mixture spectra from Section D, as ``.dpt`` files
(wavenumber, absorbance).

Run with:  python exercise6_mixture_unmixing.py

WHAT YOU DO IN THIS FILE
------------------------
Three functions:

    common_grid(...)           put two spectra on the same wavenumber axis
    unmix(...)                 least squares for the mixing fractions
    reconstruction_error(...)  how well the fit reproduces the mixture

    python exercise6_mixture_unmixing.py        <- grade yourself
    python exercise6_mixture_unmixing.py run    <- run it on your data

WHICH QUESTIONS THIS ANSWERS
----------------------------
Section D, Q1 to Q7

    STEP 2, the parity plot            ->  Section D Q1 and Q2
    STEP 3, the residual               ->  Section D Q3
    STEP 4, RMS error and the verdict  ->  Section D Q4 and Q7
    STEP 5, ATR-corrected spectra      ->  Section D Q5
    the covariance from unmix          ->  Section D Q6

The manual's question numbers are the only ones that count. This file used to
carry its own Q1, Q2, Q3 that meant something different from the manual's, so
those are now plain bullets under each step.
"""

import numpy as np
import matplotlib.pyplot as plt

import irtools as ir


def common_grid(wn_a, a, wn_b, b, wn_lo=650, wn_hi=1500, n=2000):
    """Resample two spectra (a on wn_a, b on wn_b) onto the SAME wavenumber grid.

    Real spectra from different scans rarely share an identical wavenumber
    axis. Before you can add/combine spectra point-by-point you must put them
    on a common grid by interpolation.

    Parameters
    ----------
    wn_a, a : ndarray   first spectrum's wavenumber axis and absorbance.
    wn_b, b : ndarray   second spectrum's wavenumber axis and absorbance.
    wn_lo, wn_hi : float   range to keep (choose a region with informative,
        non-saturated bands -- e.g. the aromatic/substitution region for
        xylenes, roughly 650-900 cm^-1, or widen if you want more bands).
    n : int   number of points in the common grid.

    Returns
    -------
    wn : ndarray, length n       the common grid.
    a_i, b_i : ndarray, length n  both spectra resampled onto it.

    Hints
    -----
    * ``np.linspace(wn_lo, wn_hi, n)`` builds the common grid.
    * ``np.interp(x_new, x_old, y_old)`` requires ``x_old`` sorted ascending;
      flip your arrays first if your wavenumber axis runs high to low.
    """
    # TODO: build wn, then np.interp both spectra onto it (mind sort order!)
    raise NotImplementedError("common_grid")


def unmix(A_mixture, A_pure1, A_pure2):
    """Least-squares mole fractions of a two-component mixture spectrum.

    Solve   A_mixture ~= x1 * A_pure1 + x2 * A_pure2   for (x1, x2) in the
    least-squares sense. All three spectra must already be on the SAME
    wavenumber grid (use common_grid first).

    Parameters
    ----------
    A_mixture, A_pure1, A_pure2 : ndarray, all the same length.

    Returns
    -------
    x1, x2 : float
        Best-fit coefficients. Note nothing forces them to sum to 1 or to be
        non-negative -- that is itself something to check (see Q2 below).

    Hints
    -----
    * Build the design matrix ``M = np.column_stack([A_pure1, A_pure2])``
      (shape (n_points, 2)).
    * ``np.linalg.lstsq(M, A_mixture, rcond=None)`` returns ``(coeffs,
      residuals, rank, singular_values)``; ``coeffs`` is ``[x1, x2]``.
    """
    # TODO: build M and solve with np.linalg.lstsq
    raise NotImplementedError("unmix")


def reconstruction_error(A_mixture, A_pure1, A_pure2, x1, x2):
    """Root-mean-square residual between the measured and reconstructed spectrum.

    A small residual supports the "ideal, additive mixture" hypothesis; a
    large, structured residual (e.g. a residual peak at a specific
    wavenumber) suggests a real interaction, an impurity, or a bad pure-
    component reference.

    Returns
    -------
    float   RMS of (A_mixture - (x1*A_pure1 + x2*A_pure2)).
    """
    # TODO: compute and return the RMS residual
    raise NotImplementedError("reconstruction_error")


def main():
    # -----------------------------------------------------------------
    # STEP 1  --  Load your pure-component references.
    #
    # Replace the filenames with your own Section-D absorbance files
    # (wavenumber, absorbance -- two columns, so column=None).
    # -----------------------------------------------------------------
    wn1 = A1 = None   # TODO: wn1, A1 = ir.load_dpt("pure_isomer1_ab.dpt", column=None).T
    wn2 = A2 = None   # TODO: same for pure_isomer2_ab.dpt
    if wn1 is None:
        raise SystemExit("Load your two pure-component reference spectra first.")

    # -----------------------------------------------------------------
    # STEP 2  --  Load your mixture spectra + their KNOWN mole fractions.
    #
    # Fill in the paths and the true mole fraction of isomer 1 you prepared
    # for each (Section D asked for 5 mixtures spanning 0-1).
    # -----------------------------------------------------------------
    mixture_files = [
        # ("mixture_x0.2_ab.dpt", 0.2),
        # ("mixture_x0.4_ab.dpt", 0.4),
        # ("mixture_x0.6_ab.dpt", 0.6),
        # ("mixture_x0.8_ab.dpt", 0.8),
    ]
    if not mixture_files:
        raise SystemExit("List your 5 mixture files and their true mole fractions above.")

    # -----------------------------------------------------------------
    # STEP 3  --  Unmix every mixture and compare to the truth.
    #
    #   - Tabulate: true x1, fitted x1, fitted x2, and (fitted x1 + fitted
    #       x2). If the mixture were perfectly ideal and your references
    #       perfectly clean, what would you expect x1+x2 to equal?
    #   - Plot fitted x1 (y-axis) against true x1 (x-axis) for all your
    #       mixtures, with a y=x reference line. How linear is it? Fit a line
    #       and report the slope and intercept.
    # -----------------------------------------------------------------
    true_x1, fitted_x1, fitted_x2, rms_err = [], [], [], []
    for path, x1_true in mixture_files:
        # TODO: wn_m, A_m = ir.load_dpt(path, column=None).T
        # TODO: wn_g, a1_g, a2_g = common_grid(wn1, A1, wn2, A2)  # then also
        #       resample A_m onto wn_g (reuse np.interp directly, or extend
        #       common_grid to take a third spectrum -- your choice)
        # TODO: x1, x2 = unmix(A_m_grid, a1_g, a2_g)
        # TODO: err = reconstruction_error(A_m_grid, a1_g, a2_g, x1, x2)
        # TODO: append to the lists above
        pass

    # TODO: print/plot the comparison table and parity plot described in Q1/Q2.

    # -----------------------------------------------------------------
    # STEP 4  --  Look at the residuals.
    #
    # For your mixture closest to x1 = 0.5, plot: the measured spectrum, the
    # reconstructed spectrum (x1*A_pure1 + x2*A_pure2), and the residual
    # (measured - reconstructed) on its own axis below.
    #
    #   - Is the residual flat noise, or does it have real structure (a
    #       peak or dip at a specific wavenumber)? If it has structure,
    #       suggest a physical cause (e.g. a band-position shift between the
    #       pure and mixed states, a third component, baseline drift between
    #       scans).
    # -----------------------------------------------------------------
    # TODO: your residual plot here.

    # -----------------------------------------------------------------
    # STEP 5  --  Connect back to Section D's original question.
    #
    #   - Section D asked you to compute a single excess spectrum by hand
    #       and judge "ideal or not" qualitatively. Using the RMS reconstruction
    #       error across ALL your mixtures from STEP 3, give a QUANTITATIVE
    #       answer: is this pair of xylene isomers well described by an ideal,
    #       purely additive mixture model? At what mole fraction (if any) is
    #       the model worst, and can you suggest why?
    #   - (challenge) Repeat STEP 3 using the ATR-CORRECTED spectra instead
    #       of the raw ones (from Section D part iv). Does ATR correction
    #       improve or worsen the linearity of your parity plot (Q2) and the
    #       reconstruction error (Q4)? What does this tell you about trusting
    #       instrument-applied corrections for quantitative work?
    # -----------------------------------------------------------------

    print("\nDone once STEPs 1-5 run and you have answered\n"
          "Section D Q1 to Q7 in the manual.")


# ---------------------------------------------------------------------------
# Self-tests -- run `python exercise6_mixture_unmixing.py` to grade yourself.
# Do not modify below this line.
# ---------------------------------------------------------------------------
def _report(name, ok, msg=""):
    tick = "PASS" if ok else "FAIL"
    print(f"[{tick}] {name}" + (f"  --  {msg}" if msg and not ok else ""))
    return ok


def _selftest():
    print("Running exercise6 self-tests...\n")
    results = []
    # both spectra must land on one shared axis
    try:
        wn_a = np.linspace(600, 1600, 900)
        wn_b = np.linspace(650, 1550, 700)
        a = np.exp(-((wn_a - 1000) / 40.0) ** 2)
        b = np.exp(-((wn_b - 1300) / 40.0) ** 2)
        wn, ai, bi = common_grid(wn_a, a, wn_b, b, wn_lo=700, wn_hi=1500, n=500)
        ok = (len(wn) == len(ai) == len(bi) == 500
              and np.all(np.diff(wn) > 0) and wn[0] >= 700 and wn[-1] <= 1500)
        results.append(_report("common_grid", ok, "expected three arrays of length n, on an ascending axis"))
    except NotImplementedError:
        results.append(_report("common_grid", False, "not implemented"))
    except Exception as e:
        results.append(_report("common_grid", False, f"raised {e!r}"))

    # an exact mixture of two knowns must give its own coefficients back
    try:
        wn = np.linspace(600, 1600, 1000)
        p1 = np.exp(-((wn - 900) / 30.0) ** 2)
        p2 = np.exp(-((wn - 1300) / 30.0) ** 2)
        x1, x2 = unmix(0.3 * p1 + 0.7 * p2, p1, p2)
        ok = (abs(x1 - 0.3) < 1e-6 and abs(x2 - 0.7) < 1e-6)
        results.append(_report("unmix", ok, "expected x1 = 0.3 and x2 = 0.7 for a mixture built that way"))
    except NotImplementedError:
        results.append(_report("unmix", False, "not implemented"))
    except Exception as e:
        results.append(_report("unmix", False, f"raised {e!r}"))

    # a perfect reconstruction has no error left over
    try:
        wn = np.linspace(600, 1600, 1000)
        p1 = np.exp(-((wn - 900) / 30.0) ** 2)
        p2 = np.exp(-((wn - 1300) / 30.0) ** 2)
        mix = 0.3 * p1 + 0.7 * p2
        exact = reconstruction_error(mix, p1, p2, 0.3, 0.7)
        wrong = reconstruction_error(mix, p1, p2, 0.6, 0.4)
        ok = (exact < 1e-9 and wrong > exact)
        results.append(_report("reconstruction_error", ok, "should be ~0 for an exact fit, and grow when the fit is wrong"))
    except NotImplementedError:
        results.append(_report("reconstruction_error", False, "not implemented"))
    except Exception as e:
        results.append(_report("reconstruction_error", False, f"raised {e!r}"))


    passed = sum(bool(r) for r in results)
    print(f"\n{passed}/{len(results)} checks passed.")
    if passed == len(results):
        print("All good -- now run:  python exercise6_mixture_unmixing.py run")
    else:
        print("Keep going: fix the FAIL items above, then re-run.")


if __name__ == "__main__":
    import sys

    if "run" in sys.argv[1:]:
        main()
    else:
        _selftest()
        print("\nTo run the analysis on your own data:  python exercise6_mixture_unmixing.py run")
