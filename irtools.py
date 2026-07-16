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

    Hints
    -----
    * ``np.loadtxt`` can read comma-separated files with ``delimiter=","``.
    * Slicing a 2-D array: ``data[:, column]`` selects one column.
    """
    # TODO: implement me
    raise NotImplementedError("load_dpt: read the file and return the requested column(s)")


# ---------------------------------------------------------------------------
# 2. Finding the centre of the interferogram (the "zero burst")
# ---------------------------------------------------------------------------
def find_zero_burst(ifg):
    """Return the index of the zero burst (centre burst) of an interferogram.

    The zero burst is the point of MAXIMUM signal magnitude. It corresponds
    to zero optical path difference, where every wavelength interferes
    constructively at once.

    Parameters
    ----------
    ifg : numpy.ndarray
        A raw interferogram (1-D).

    Returns
    -------
    int
        Index of the maximum-magnitude sample.

    Hints
    -----
    * The burst can be a large positive OR a large negative spike, so look at
      the magnitude (``np.abs``).
    * ``np.argmax`` returns the index of the largest value.
    """
    # TODO: implement me
    raise NotImplementedError("find_zero_burst: return index of the largest-magnitude point")


# ---------------------------------------------------------------------------
# 3. Cutting a symmetric window around the zero burst
# ---------------------------------------------------------------------------
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
    # TODO: implement me
    raise NotImplementedError("window_around: slice N points centred on `center`")


# ---------------------------------------------------------------------------
# 4. Interferogram  ->  single-beam intensity spectrum
# ---------------------------------------------------------------------------
def single_beam(ifg_window):
    """Fourier-transform a windowed interferogram into a single-beam spectrum.

    An FT-IR spectrometer measures light in the *interferogram* domain. To get
    the spectrum you apply a discrete Fourier transform and keep the MAGNITUDE.
    Only the first half of the FFT output is physically meaningful for a real
    input signal (the second half is the mirror image / negative frequencies),
    so return only ``[:N//2]``.

    Parameters
    ----------
    ifg_window : numpy.ndarray
        Interferogram window of length N (from :func:`window_around`).

    Returns
    -------
    numpy.ndarray
        Magnitude spectrum of length ``N // 2``.

    Hints
    -----
    * ``np.fft.fft`` computes the DFT.
    * ``np.abs`` gives the magnitude of the (complex) FFT result.
    """
    # TODO: implement me
    raise NotImplementedError("single_beam: FFT the window, take magnitude, keep first half")


# ---------------------------------------------------------------------------
# 5. Building the wavenumber axis
# ---------------------------------------------------------------------------
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
    # TODO: implement me
    raise NotImplementedError("wavenumber_axis: linspace from 0 to k with N//2 points")


# ---------------------------------------------------------------------------
# 6. Transmittance and absorbance
# ---------------------------------------------------------------------------
def transmittance(sample_sb, reference_sb):
    """Transmittance T = I_sample / I_reference (a ratio between 0 and ~1).

    Dividing the sample single-beam spectrum by the reference (background)
    single-beam spectrum removes the instrument/source response and leaves
    only what the SAMPLE did to the light.

    Returns
    -------
    numpy.ndarray
        Transmittance (dimensionless). Multiply by 100 yourself when you want %.
    """
    # TODO: implement me
    raise NotImplementedError("transmittance: divide sample by reference")


def absorbance(T):
    """Absorbance A = -log10(T).

    Absorbance is the quantity that is (ideally) linear in concentration
    (Beer-Lambert law), which is why chemists usually report it.

    Returns
    -------
    numpy.ndarray
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

    # load_dpt
    try:
        fd, p = tempfile.mkstemp(suffix=".dpt")
        os.close(fd)
        with open(p, "w") as f:
            f.write("0.0,10.0\n1.0,20.0\n2.0,30.0\n")
        col1 = load_dpt(p, column=1)
        both = load_dpt(p, column=None)
        ok = (np.allclose(col1, [10, 20, 30]) and np.asarray(both).shape == (3, 2))
        results.append(_report("load_dpt", ok, "column selection wrong"))
        os.remove(p)
    except NotImplementedError:
        results.append(_report("load_dpt", False, "not implemented"))
    except Exception as e:  # noqa
        results.append(_report("load_dpt", False, f"raised {e!r}"))

    # find_zero_burst
    try:
        sig = np.array([0.0, 1.0, -5.0, 2.0, 0.5])
        ok = (find_zero_burst(sig) == 2)
        results.append(_report("find_zero_burst", ok, "should pick the |max| at index 2"))
    except NotImplementedError:
        results.append(_report("find_zero_burst", False, "not implemented"))
    except Exception as e:  # noqa
        results.append(_report("find_zero_burst", False, f"raised {e!r}"))

    # window_around
    try:
        arr = np.arange(100.0)
        w = window_around(arr, center=50, N=10)
        ok = (len(w) == 10 and w[0] == 45 and w[-1] == 54)
        results.append(_report("window_around", ok, "window bounds/length wrong"))
    except NotImplementedError:
        results.append(_report("window_around", False, "not implemented"))
    except Exception as e:  # noqa
        results.append(_report("window_around", False, f"raised {e!r}"))

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

    # wavenumber_axis
    try:
        wn = wavenumber_axis(N=16, k=16716.51)
        ok = (len(wn) == 8 and wn[0] == 0.0 and np.isclose(wn[-1], 16716.51))
        results.append(_report("wavenumber_axis", ok, "length or endpoints wrong"))
    except NotImplementedError:
        results.append(_report("wavenumber_axis", False, "not implemented"))
    except Exception as e:  # noqa
        results.append(_report("wavenumber_axis", False, f"raised {e!r}"))

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
