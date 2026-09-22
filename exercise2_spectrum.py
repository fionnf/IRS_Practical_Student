"""
Exercise 2 -- From interferogram to IR spectrum
================================================

Goal
----
Turn the raw interferograms into a real, interpretable IR spectrum:
single-beam spectra -> transmittance -> absorbance, and check your result
against the instrument's own absorbance file.

This is the heart of FT-IR. You already wrote every tool you need in
`irtools.py`; here you wire them together into the full pipeline.

Run with:  python exercise2_spectrum.py

WHAT YOU DO IN THIS FILE
------------------------
One function: compute_spectrum. It chains together the irtools pieces you
already wrote into the full route from two interferograms to a transmittance
spectrum. If irtools passes its self-test, this is mostly plumbing.

    python exercise2_spectrum.py        <- grade yourself
    python exercise2_spectrum.py run    <- run it on your data
"""

import numpy as np
import matplotlib.pyplot as plt

import irtools as ir

K = 16716.51        # instrument constant (cm^-1 at the end of the half-spectrum)
N = 2 ** 14         # FFT window length. You will vary this in exercise 4.


def compute_spectrum(rifg, sifg, N, k):
    """Full pipeline: two raw interferograms -> (wavenumber, transmittance).

    Steps you must implement:
      1. Find the zero burst of the REFERENCE interferogram (rifg).
      2. Cut a window of length N centred on that burst from BOTH rifg and
         sifg. (Use the SAME centre for both so they stay aligned!)
      3. Fourier-transform each window into a single-beam spectrum.
      4. Build the matching wavenumber axis.
      5. Compute transmittance = sample / reference.

    Returns
    -------
    wn : ndarray
        Wavenumber axis (cm^-1).
    T : ndarray
        Transmittance (dimensionless).
    """
    # TODO: 1. centre = ir.find_zero_burst(rifg)
    # TODO: 2. r_win = ir.window_around(rifg, centre, N)   (and s_win likewise)
    # TODO: 3. I0 = ir.single_beam(r_win);  I = ir.single_beam(s_win)
    # TODO: 4. wn = ir.wavenumber_axis(N, k)
    # TODO: 5. T = ir.transmittance(I, I0)
    # TODO: return wn, T
    raise NotImplementedError("compute_spectrum: wire the irtools functions together")


def main():
    # -----------------------------------------------------------------
    # STEP 1  --  Load the interferograms (as in exercise 1).
    # -----------------------------------------------------------------
    # TODO: load ethanol_rifg / ethanol_sifg with ir.load_dpt(..., column=1)
    e_rifg = None
    e_sifg = None
    if e_rifg is None:
        raise SystemExit("Load the ethanol interferograms first.")

    # -----------------------------------------------------------------
    # STEP 2  --  Run your pipeline.
    # -----------------------------------------------------------------
    wn, T = compute_spectrum(e_rifg, e_sifg, N, K)
    A = ir.absorbance(T)

    # -----------------------------------------------------------------
    # STEP 3  --  Plot the transmittance spectrum.
    #
    # Convention: IR spectra run with wavenumber DECREASING left-to-right,
    # so set plt.xlim(4000, 500). Plot T in percent.
    #
    #   Q1. Identify the strong dip near ~3300 cm^-1 and the group of dips
    #       near 2900 cm^-1. Which bonds in ethanol do they correspond to?
    # -----------------------------------------------------------------
    plt.figure(figsize=(8, 4))
    plt.plot(wn, T * 100, label="Transmittance")
    plt.xlim(4000, 500)
    plt.ylim(0, 105)
    plt.xlabel("Wavenumber / cm$^{-1}$")
    plt.ylabel("Transmittance / %")
    plt.title("Ethanol transmittance -- your result")
    plt.legend()
    plt.tight_layout()
    plt.show()

    # -----------------------------------------------------------------
    # STEP 4  --  Plot the absorbance spectrum.
    #
    #   Q2. Absorbance and transmittance carry the same information. Why do
    #       chemists usually prefer absorbance for quantitative work?
    #       (Think back to the Beer-Lambert law.)
    # -----------------------------------------------------------------
    # TODO: plot A vs wn with the same x-limits.

    # -----------------------------------------------------------------
    # STEP 5  --  Validate against the instrument.
    #
    # Load ethanol_ab.dpt (both columns): column 0 is wavenumber, column 1 is
    # the absorbance the Bruker software computed. Overlay it on YOUR
    # absorbance curve.
    #
    #   Q3. Do the peak POSITIONS match? Do the peak HEIGHTS match?
    #   Q4. List two reasons your curve might differ from the instrument's
    #       (hint: apodization and phase correction -- more in exercise 4).
    # -----------------------------------------------------------------
    # TODO: e_ab = ir.load_dpt("ethanol_ab.dpt", column=None)
    # TODO: overlay plot of your A vs e_ab

    print("Exercise 2 complete once the pipeline runs and Q1-Q4 are answered.")


# ---------------------------------------------------------------------------
# Self-tests -- run `python exercise2_spectrum.py` to grade yourself.
# Do not modify below this line.
# ---------------------------------------------------------------------------
def _report(name, ok, msg=""):
    tick = "PASS" if ok else "FAIL"
    print(f"[{tick}] {name}" + (f"  --  {msg}" if msg and not ok else ""))
    return ok


def _selftest():
    print("Running exercise2 self-tests...\n")
    results = []
    # identical reference and sample must give T = 1 everywhere
    try:
        rng = np.random.default_rng(0)
        N = 1024
        ifg = np.zeros(4096)
        ifg[2048] = 50.0
        ifg += rng.normal(0, 1e-3, ifg.shape)
        wn, T = compute_spectrum(ifg, ifg.copy(), N, 16716.51)
        ok = np.allclose(T, 1.0, atol=1e-9)
        results.append(_report("compute_spectrum (T = 1 for an empty sample)", ok, "dividing a beam by itself must give transmittance 1"))
    except NotImplementedError:
        results.append(_report("compute_spectrum (T = 1 for an empty sample)", False, "not implemented"))
    except Exception as e:
        results.append(_report("compute_spectrum (T = 1 for an empty sample)", False, f"raised {e!r}"))

    # the axis must be half the window length
    try:
        N = 1024
        ifg = np.zeros(4096)
        ifg[2048] = 50.0
        wn, T = compute_spectrum(ifg, ifg.copy(), N, 16716.51)
        ok = (len(wn) == N // 2 and len(T) == N // 2)
        results.append(_report("compute_spectrum (array lengths)", ok, "wn and T should both have N//2 points"))
    except NotImplementedError:
        results.append(_report("compute_spectrum (array lengths)", False, "not implemented"))
    except Exception as e:
        results.append(_report("compute_spectrum (array lengths)", False, f"raised {e!r}"))


    passed = sum(bool(r) for r in results)
    print(f"\n{passed}/{len(results)} checks passed.")
    if passed == len(results):
        print("All good -- now run:  python exercise2_spectrum.py run")
    else:
        print("Keep going: fix the FAIL items above, then re-run.")


if __name__ == "__main__":
    import sys

    if "run" in sys.argv[1:]:
        main()
    else:
        _selftest()
        print("\nTo run the analysis on your own data:  python exercise2_spectrum.py run")
