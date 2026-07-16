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


if __name__ == "__main__":
    main()
