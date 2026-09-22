"""
irtools.py  --  Your personal FT-IR toolkit
============================================

This is the ONE module you build up yourself and then re-use in every
exercise (exercise1 ... exercise5). Think of it as the set of "instruments"
in your virtual lab: once each function works, you never have to write that
piece of physics again.

HOW TO WORK ON THIS FILE
------------------------
1. Every function below has a docstring telling you *what* it must do and a
   `raise NotImplementedError(...)` that you must delete and replace with
   your own code.
2. Work top-to-bottom. Each function is small (usually 1-5 lines).
3. When you think a function is done, run this file directly:

       python irtools.py

   The self-tests at the bottom will tell you which functions pass and which
   still need work. Do NOT edit the self-tests -- they are your grader.

You are allowed to use numpy. You are NOT allowed to import a ready-made
FT-IR / spectroscopy package that does the work for you: the point of the
practical is that YOU implement the maths.

WHICH QUESTIONS THIS ANSWERS
----------------------------
Section 0, Q1 and Q2.

    the five self-tests   ->  Section 0 Q1 (paste the passing output)
    what went wrong       ->  Section 0 Q2 (which function fought you)

Nothing else works until this file does, so start here.
"""

import numpy as np


# ---------------------------------------------------------------------------
# 1. Reading the raw data
# ---------------------------------------------------------------------------
def load_dpt(path, column=1):
    """Load one column from a Bruker ``.dpt`` (data point table) file.

    A ``.dpt`` file is just comma-separated text with two columns:

        x_value , y_value
        x_value , y_value
        ...

    For the interferogram files (``*_rifg.dpt``, ``*_sifg.dpt``) the useful
    signal is in the SECOND column (index 1). For the already-processed
    absorbance files (``*_ab.dpt``) you will usually want BOTH columns, so
    make ``column`` selectable.

    This one is WRITTEN FOR YOU. Reading a comma-separated file is Python
    housekeeping, not spectroscopy, and every exercise needs it before it can
    do anything at all. Read it, then move on to find_zero_burst below, which
    is where the real work starts.

    Parameters
    ----------
    path : str
        Path to the .dpt file.
    column : int or None
        Which column to return (0 or 1). If ``None``, return the full 2-D
        array with both columns.

    Returns
    -------
    numpy.ndarray
        1-D array (single column) or 2-D array (both columns).
    """
    data = np.loadtxt(path, delimiter=",")
    if column is None:
        return data
    return data[:, column]


# ---------------------------------------------------------------------------
# 2. Finding the centre of the interferogram (the "zero burst")
# ---------------------------------------------------------------------------
def find_zero_burst(ifg):
    """Find where the interferogram's centre burst is.

    WHAT IT MUST DO
        Return the INDEX of the point with the largest magnitude in ``ifg``.

    WHY
        The zero burst is zero optical path difference: the one mirror
        position where every wavelength interferes constructively at once.
        It is the tallest feature in the interferogram, and everything else
        you do is measured relative to it.

    YOUR TASK  (two lines of code)
        1. Take the magnitude of every point       ->  np.abs(ifg)
        2. Return the index of the largest one     ->  int(np.argmax(...))

    WORKED EXAMPLE
        >>> find_zero_burst(np.array([0.1, -0.2, -9.0, 0.3]))
        2
        Index 2, not 3: -9.0 has the largest MAGNITUDE even though 0.3 is the
        largest value. Getting this wrong is the single most common mistake
        here, because the burst points downwards on about half of all
        detectors, depending on polarity and phase. Skip the np.abs and your
        code will work on friendly data and fail on real data.

    THE SELF-TEST CHECKS
        A signal whose largest-magnitude point is a negative spike at index 2
        returns 2.

    Parameters
    ----------
    ifg : numpy.ndarray
        A raw interferogram (1-D).

    Returns
    -------
    int
        Index of the maximum-magnitude sample.
    """
    # TODO: implement me
    raise NotImplementedError("find_zero_burst: return index of the largest-magnitude point")


# ---------------------------------------------------------------------------
# 3. Cutting a symmetric window around the zero burst
# ---------------------------------------------------------------------------
# --- WRITTEN FOR YOU: plumbing, not physics. Read it and move on. ---
def window_around(ifg, center, N):
    """Return ``N`` samples of ``ifg`` centred on index ``center``.

    We keep a window of length ``N`` running from ``center - N/2`` up to (but
    not including) ``center + N/2``. Using a power-of-two ``N`` makes the FFT
    fast and keeps the wavenumber axis simple.

    Parameters
    ----------
    ifg : numpy.ndarray
    center : int
        Index returned by :func:`find_zero_burst`.
    N : int
        Window length (use a power of two, e.g. 2**14).

    Returns
    -------
    numpy.ndarray
        Slice of length ``N``.

    Hints
    -----
    * Compute integer start/stop indices with ``int(center - N/2)`` etc.
    * You may assume the burst is far enough from the ends that the window
      fits. (In exercise 4 you will think about what happens if it doesn't.)
    """
    start = int(center - N / 2)
    stop = int(center + N / 2)
    if start < 0 or stop > len(ifg):
        # Slicing past the end of an array does NOT raise in Python, it just
        # returns a shorter one. That silently breaks everything downstream:
        # the spectrum and the wavenumber axis stop matching and you get a
        # shifted spectrum with no error message. So say so here instead.
        raise ValueError(
            "a window of N=%d around index %d does not fit in an "
            "interferogram of %d points. The largest N that fits is %d."
            % (N, center, len(ifg), 2 * min(center, len(ifg) - center)))
    return ifg[start:stop]


# ---------------------------------------------------------------------------
# 4. Interferogram  ->  single-beam intensity spectrum
# ---------------------------------------------------------------------------
def single_beam(ifg_window):
    """Fourier-transform a windowed interferogram into a single-beam spectrum.

    WHAT IT MUST DO
        Turn a window of length N into a magnitude spectrum of length N // 2.

    WHY
        This is the Fourier transform at the heart of FT-IR. The interferogram
        encodes every wavelength at once; the transform separates them. You
        keep the MAGNITUDE because the phase is not what you measure, and you
        keep only the FIRST HALF because the FFT of a real signal is Hermitian:
        the second half is the complex-conjugate mirror of the first and
        carries no independent information. It is not noise, and discarding it
        throws nothing away.

    YOUR TASK  (three lines of code)
        1. Fourier-transform the window      ->  np.fft.fft(ifg_window)
        2. Take the magnitude                ->  np.abs(...)
        3. Keep the first half               ->  ...[:len(ifg_window) // 2]

    WORKED EXAMPLE
        A window of 16 points transforms to 16 complex numbers, and you return
        the first 8 magnitudes:
        >>> len(single_beam(np.zeros(16)))
        8

    THE SELF-TEST CHECKS
        A 16-point window gives 8 points out, with the right values for a
        known input.

    Parameters
    ----------
    ifg_window : numpy.ndarray
        Interferogram window of length N (from :func:`window_around`).

    Returns
    -------
    numpy.ndarray
        Magnitude spectrum of length ``N // 2``.
    """
    # TODO: implement me
    raise NotImplementedError("single_beam: FFT the window, take magnitude, keep first half")


# ---------------------------------------------------------------------------
# 5. Building the wavenumber axis
# ---------------------------------------------------------------------------
# --- WRITTEN FOR YOU: plumbing, not physics. Read it and move on. ---
def wavenumber_axis(N, k):
    """Return the wavenumber (cm^-1) axis matching a spectrum of length N//2.

    The instrument samples the interferogram at a fixed rate. The constant
    ``k`` (given to you, 16716.51) is the maximum wavenumber that corresponds
    to the last point of the half-spectrum. The half-spectrum has ``N//2``
    points running linearly from 0 up to ``k``.

    Parameters
    ----------
    N : int
        FFT length used in :func:`single_beam` (the full window length).
    k : float
        Instrument constant / maximum wavenumber (cm^-1).

    Returns
    -------
    numpy.ndarray
        Wavenumber values, length ``N // 2``.

    Hints
    -----
    * ``np.linspace(start, stop, num)`` builds an evenly spaced axis.
    * The axis must have EXACTLY the same length as the output of
      :func:`single_beam`.
    """
    return np.linspace(0, k, N // 2)


# ---------------------------------------------------------------------------
# 6. Transmittance and absorbance
# ---------------------------------------------------------------------------
def transmittance(sample_sb, reference_sb):
    """Divide out the instrument, leaving only what the sample did.

    WHAT IT MUST DO
        Return ``sample_sb / reference_sb``, element by element.

    WHY
        Both single-beam spectra are dominated by the same thing: how bright
        the source is and how sensitive the detector is at each wavenumber.
        That is identical in both measurements, so it cancels in the ratio.
        What survives is the sample's own absorption. T is a fraction: 1.0 is
        "all the light got through", 0.1 is "a tenth got through".

    YOUR TASK  (one line of code)
        1. Divide the two arrays  ->  sample_sb / reference_sb
           numpy divides element by element, so no loop is needed.

    WORKED EXAMPLE
        >>> transmittance(np.array([5.0, 1.0]), np.array([10.0, 10.0]))
        array([0.5, 0.1])

    THE SELF-TEST CHECKS
        Exactly that example, together with :func:`absorbance` below.

    Returns
    -------
    numpy.ndarray
        Transmittance (dimensionless). Multiply by 100 yourself when you want %.
    """
    # TODO: implement me
    raise NotImplementedError("transmittance: divide sample by reference")


def absorbance(T):
    """Convert transmittance to absorbance.

    WHAT IT MUST DO
        Return ``-log10(T)``, element by element.

    WHY
        Transmittance is not proportional to how much of the substance is
        there: send light through twice the sample and T squares rather than
        halving. Taking the negative base-10 logarithm turns that into a
        quantity that IS proportional to concentration, which is the
        Beer-Lambert law, and it is why every spectrum in your report is
        plotted as absorbance.

    YOUR TASK  (one line of code)
        1. Negative base-10 log  ->  -np.log10(T)
           Use np.log10, not np.log, which is the natural logarithm.

    WORKED EXAMPLE
        >>> absorbance(np.array([0.5, 0.1]))
        array([0.30103, 1.     ])
        T = 0.1 gives A = 1 exactly: one absorbance unit means a tenth of the
        light gets through. T = 0.01 gives A = 2, and so on.

    THE SELF-TEST CHECKS
        absorbance([0.5, 0.1]) == [log10(2), 1.0].

    Returns
    -------
    numpy.ndarray
        Absorbance (dimensionless).
    """
    # TODO: implement me
    raise NotImplementedError("absorbance: A = -log10(T)")


# ---------------------------------------------------------------------------
# Self-tests  --  run `python irtools.py` to grade your implementations.
# Do not modify below this line.
# ---------------------------------------------------------------------------
def _report(name, ok, msg=""):
    tick = "PASS" if ok else "FAIL"
    print(f"[{tick}] {name}" + (f"  --  {msg}" if msg and not ok else ""))
    return ok


def _selftest():
    import tempfile, os
    print("Running irtools self-tests...\n")
    results = []

    # find_zero_burst
    try:
        sig = np.array([0.0, 1.0, -5.0, 2.0, 0.5])
        ok = (find_zero_burst(sig) == 2)
        results.append(_report("find_zero_burst", ok, "should pick the |max| at index 2"))
    except NotImplementedError:
        results.append(_report("find_zero_burst", False, "not implemented"))
    except Exception as e:  # noqa
        results.append(_report("find_zero_burst", False, f"raised {e!r}"))

    # single_beam  (delta function -> flat magnitude spectrum)
    try:
        x = np.zeros(16); x[0] = 1.0
        sb = single_beam(x)
        ok = (len(sb) == 8 and np.allclose(sb, 1.0))
        results.append(_report("single_beam", ok, "FFT/half/magnitude wrong"))
    except NotImplementedError:
        results.append(_report("single_beam", False, "not implemented"))
    except Exception as e:  # noqa
        results.append(_report("single_beam", False, f"raised {e!r}"))

    # transmittance / absorbance
    try:
        T = transmittance(np.array([50.0, 10.0]), np.array([100.0, 100.0]))
        A = absorbance(T)
        ok = (np.allclose(T, [0.5, 0.1]) and np.allclose(A, [np.log10(2), 1.0]))
        results.append(_report("transmittance/absorbance", ok, "ratio or -log10 wrong"))
    except NotImplementedError:
        results.append(_report("transmittance/absorbance", False, "not implemented"))
    except Exception as e:  # noqa
        results.append(_report("transmittance/absorbance", False, f"raised {e!r}"))

    passed = sum(bool(r) for r in results)
    print(f"\n{passed}/{len(results)} checks passed.")
    if passed == len(results):
        print("All good -- your toolkit is ready. Move on to exercise1_interferogram.py")
    else:
        print("Keep going: fix the FAIL items above, then re-run `python irtools.py`.")


if __name__ == "__main__":
    _selftest()
