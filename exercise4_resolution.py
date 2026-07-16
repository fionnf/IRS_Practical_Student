"""
Exercise 4 -- Resolution, apodization and zero-filling
======================================================

Goal
----
So far you took the FFT of a plain rectangular window and hoped for the best.
In this exercise you EXPERIMENT with the three knobs that every FT-IR
spectroscopist has to understand:

  * window length N       -> spectral resolution  (how far the mirror travels)
  * apodization function  -> peak shape vs side-lobes ("ringing")
  * zero-filling          -> interpolation of the spectrum

These are genuine numerical experiments: change one thing, look at the
spectrum, and explain what you see.

Run with:  python exercise4_resolution.py
"""

import numpy as np
import matplotlib.pyplot as plt

import irtools as ir

K = 16716.51


# ---------------------------------------------------------------------------
# Tools to implement
# ---------------------------------------------------------------------------
def apodize(window, kind="boxcar"):
    """Multiply an interferogram window by an apodization (taper) function.

    Cutting a finite window out of the interferogram is itself a
    multiplication by a rectangular ("boxcar") function, which causes ringing
    (side-lobes / negative wiggles) around sharp peaks. Tapering the window
    edges smoothly to zero suppresses that ringing at the cost of slightly
    broader peaks.

    Implement at least these ``kind`` options:
      * "boxcar"        -> no change (multiply by ones)
      * "triangular"    -> a linear ramp up then down (np.bartlett)
      * "hann"          -> raised cosine (np.hanning)
      * "blackman"      -> stronger taper (np.blackman)

    Parameters
    ----------
    window : ndarray   interferogram window of length N.
    kind : str

    Returns
    -------
    ndarray   window * taper, same length.

    Hints
    -----
    * numpy already provides np.bartlett(N), np.hanning(N), np.blackman(N),
      each returning a taper of length N. "boxcar" is just np.ones(N).
    """
    # TODO: build the taper for the requested `kind` and return window * taper
    raise NotImplementedError("apodize: taper the window before the FFT")


def zero_fill(window, factor=2):
    """Pad the interferogram window with zeros to `factor` x its length.

    Zero-filling does NOT add information, but it interpolates the FFT onto a
    finer wavenumber grid, making peak positions easier to read.

    Parameters
    ----------
    window : ndarray
    factor : int   e.g. 2 doubles the length.

    Returns
    -------
    ndarray   length = factor * len(window).

    Hints
    -----
    * np.pad(window, (0, extra)) appends `extra` zeros.
    """
    # TODO: append zeros so the result has length factor*len(window)
    raise NotImplementedError("zero_fill: pad the window with zeros")


def spectrum_from_window(window, k):
    """Single-beam magnitude spectrum + matching wavenumber axis for a window.

    Convenience wrapper so the experiments below stay short. Reuse your
    irtools functions: length here is len(window) (which may be zero-filled).
    """
    N = len(window)
    I = ir.single_beam(window)
    wn = ir.wavenumber_axis(N, k)
    return wn, I


# ---------------------------------------------------------------------------
# Experiments
# ---------------------------------------------------------------------------
def main():
    rifg = None   # TODO: ir.load_dpt("ethanol_rifg.dpt", column=1)
    sifg = None   # TODO
    if rifg is None:
        raise SystemExit("Load the ethanol interferograms first (see exercise 1).")

    centre = ir.find_zero_burst(rifg)

    # -----------------------------------------------------------------
    # EXPERIMENT A  --  Resolution vs window length N.
    #
    # Loop over several window lengths, e.g. [2**10, 2**12, 2**14], compute the
    # transmittance each time and overlay the spectra (zoom into a region with
    # close peaks, e.g. 2800-3050 cm^-1).
    #
    #   Q1. As N increases, what happens to the linewidths and to your ability
    #       to separate neighbouring bands?
    #   Q2. FT-IR resolution (cm^-1) is roughly 1 / (max optical path
    #       difference). Explain qualitatively why a longer window = better
    #       resolution, in terms of how far the mirror travels.
    # -----------------------------------------------------------------
    plt.figure(figsize=(8, 4))
    for N in [2 ** 10, 2 ** 12, 2 ** 14]:
        r = ir.window_around(rifg, centre, N)
        s = ir.window_around(sifg, centre, N)
        # TODO: single-beam of each, transmittance, wavenumber axis, then plot
        # wn, I0 = spectrum_from_window(r, K); _, I = spectrum_from_window(s, K)
        # T = ir.transmittance(I, I0)
        # plt.plot(wn, T*100, label=f"N = {N}")
        pass
    plt.xlim(3050, 2800)
    plt.xlabel("Wavenumber / cm$^{-1}$")
    plt.ylabel("Transmittance / %")
    plt.title("Experiment A: resolution vs window length")
    plt.legend()
    plt.tight_layout()
    plt.show()

    # -----------------------------------------------------------------
    # EXPERIMENT B  --  Apodization.
    #
    # Fix N (say 2**12). For each kind in ["boxcar","triangular","hann",
    # "blackman"]: apodize BOTH windows, compute transmittance, overlay.
    #
    #   Q3. Which apodization gives the sharpest peaks? Which gives the least
    #       ringing (fewest negative side-lobes around strong bands)? Describe
    #       the trade-off in one sentence.
    # -----------------------------------------------------------------
    N = 2 ** 12
    r = ir.window_around(rifg, centre, N)
    s = ir.window_around(sifg, centre, N)
    plt.figure(figsize=(8, 4))
    for kind in ["boxcar", "triangular", "hann", "blackman"]:
        # TODO: ra = apodize(r, kind); sa = apodize(s, kind)
        # TODO: compute T and plot vs wavenumber
        pass
    plt.xlim(4000, 500)
    plt.xlabel("Wavenumber / cm$^{-1}$")
    plt.ylabel("Transmittance / %")
    plt.title("Experiment B: effect of apodization")
    plt.legend()
    plt.tight_layout()
    plt.show()

    # -----------------------------------------------------------------
    # EXPERIMENT C  --  Zero-filling.
    #
    # Take a SHORT window (e.g. N = 2**10) so points are coarse. Compute the
    # spectrum with no zero-fill and with factor=4, and overlay them on a
    # narrow zoom. Use markers ('o-') so you can see individual points.
    #
    #   Q4. Zero-filling makes the curve look smoother. Did it actually improve
    #       the true RESOLUTION (your ability to separate two real peaks), or
    #       only the sampling of the curve? Justify using what you saw in
    #       Experiment A.
    # -----------------------------------------------------------------
    # TODO: implement the zero-fill comparison

    print("Exercise 4 complete once experiments A-C run and Q1-Q4 are answered.")


if __name__ == "__main__":
    main()
