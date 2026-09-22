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

WHAT YOU DO IN THIS FILE
------------------------
Three short functions, then three numerical experiments that use them:

    apodize(window, kind)      taper the window edges
    zero_fill(window, factor)  pad with zeros
    spectrum_from_window(...)  window -> spectrum, a thin wrapper

    python exercise4_resolution.py        <- grade yourself
    python exercise4_resolution.py run    <- run the experiments
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


# ---------------------------------------------------------------------------
# Self-tests -- run `python exercise4_resolution.py` to grade yourself.
# Do not modify below this line.
# ---------------------------------------------------------------------------
def _report(name, ok, msg=""):
    tick = "PASS" if ok else "FAIL"
    print(f"[{tick}] {name}" + (f"  --  {msg}" if msg and not ok else ""))
    return ok


def _selftest():
    print("Running exercise4 self-tests...\n")
    results = []
    # boxcar changes nothing; a taper removes energy from the edges
    try:
        w = np.ones(256)
        box = apodize(w, "boxcar")
        bla = apodize(w, "blackman")
        ok = (np.allclose(box, w) and len(bla) == len(w)
              and abs(bla[0]) < 1e-6 and bla.sum() < box.sum())
        results.append(_report("apodize", ok, "boxcar must be a no-op, and blackman must taper the edges to ~0"))
    except NotImplementedError:
        results.append(_report("apodize", False, "not implemented"))
    except Exception as e:
        results.append(_report("apodize", False, f"raised {e!r}"))

    # zero-filling lengthens the window without touching the data
    try:
        w = np.arange(1.0, 65.0)
        out = zero_fill(w, factor=4)
        ok = (len(out) == 4 * len(w) and np.allclose(out[:len(w)], w)
              and np.allclose(out[len(w):], 0.0))
        results.append(_report("zero_fill", ok, "expected factor*N points, original data first, zeros after"))
    except NotImplementedError:
        results.append(_report("zero_fill", False, "not implemented"))
    except Exception as e:
        results.append(_report("zero_fill", False, f"raised {e!r}"))

    # the spectrum and its axis must be the same length
    try:
        w = np.zeros(512)
        w[256] = 10.0
        wn, spec = spectrum_from_window(w, 16716.51)
        ok = (len(wn) == len(spec) == len(w) // 2)
        results.append(_report("spectrum_from_window", ok, "wn and the spectrum should both be len(window)//2"))
    except NotImplementedError:
        results.append(_report("spectrum_from_window", False, "not implemented"))
    except Exception as e:
        results.append(_report("spectrum_from_window", False, f"raised {e!r}"))


    passed = sum(bool(r) for r in results)
    print(f"\n{passed}/{len(results)} checks passed.")
    if passed == len(results):
        print("All good -- now run:  python exercise4_resolution.py run")
    else:
        print("Keep going: fix the FAIL items above, then re-run.")


if __name__ == "__main__":
    import sys

    if "run" in sys.argv[1:]:
        main()
    else:
        _selftest()
        print("\nTo run the analysis on your own data:  python exercise4_resolution.py run")
