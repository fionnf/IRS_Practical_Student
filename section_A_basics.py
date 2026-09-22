"""
Section A -- FT-IR measurement basics
=====================================

Everything Section A needs, in four parts that run in order. Each part uses
what the one before it produced, so work through them top to bottom.

WHICH QUESTIONS THIS ANSWERS
----------------------------
Section A, Q1 to Q8  (and Section 0, Q3 on the practice data)

    PART 1, explore the interferograms  ->  Section A Q1; Section 0 Q3
    PART 2, interferogram to spectrum   ->  Section A Q2
    PART 3, baseline, peaks, assignment ->  Section A Q3 and Q8
    PART 4, resolution experiments      ->  Section A Q4, Q5 and Q6

Section A Q7 is a derivation, and Q9 to Q13 use uncertainty.py. The manual's
question numbers are the only ones that count.

YOU WRITE FOUR FUNCTIONS
------------------------
    compute_spectrum   two interferograms -> a transmittance spectrum
    find_bands         locate the peaks
    apodize            taper the window edges
    zero_fill          pad the window with zeros

Everything else in this file is written for you and marked as such.

    python section_A_basics.py        grade yourself
    python section_A_basics.py run    run all four parts on your data
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks


K = 16716.51        # instrument constant (Nyquist wavenumber, cm^-1)
N = 2 ** 14         # FFT window length. PART 4 varies this.


# -------------------------------------------------------------------------
# The FT-IR pipeline -- ALL WRITTEN FOR YOU
#
# This is the route from what the spectrometer records to a spectrum you
# can read. Nothing here is yours to write, but read it once: the manual
# asks you about it, and PART 2 below chains these together.
# -------------------------------------------------------------------------

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
    data = np.loadtxt(path, delimiter=",")
    if column is None:
        return data
    return data[:, column]

def find_zero_burst(ifg):
    """Find where the interferogram's centre burst is.

    WHAT IT MUST DO
        Return the INDEX of the point with the largest magnitude in ``ifg``.

    WHY
        The zero burst is zero optical path difference: the one mirror
        position where every wavelength interferes constructively at once.
        It is the tallest feature in the interferogram, and everything else
        you do is measured relative to it.

    HOW IT WORKS
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


    Parameters
    ----------
    ifg : numpy.ndarray
        A raw interferogram (1-D).

    Returns
    -------
    int
        Index of the maximum-magnitude sample.
    """
    return int(np.argmax(np.abs(ifg)))

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

    HOW IT WORKS
        1. Fourier-transform the window      ->  np.fft.fft(ifg_window)
        2. Take the magnitude                ->  np.abs(...)
        3. Keep the first half               ->  ...[:len(ifg_window) // 2]

    WORKED EXAMPLE
        A window of 16 points transforms to 16 complex numbers, and you return
        the first 8 magnitudes:
        >>> len(single_beam(np.zeros(16)))
        8


    Parameters
    ----------
    ifg_window : numpy.ndarray
        Interferogram window of length N (from :func:`window_around`).

    Returns
    -------
    numpy.ndarray
        Magnitude spectrum of length ``N // 2``.
    """
    N = len(ifg_window)
    spectrum = np.fft.fft(ifg_window)
    return np.abs(spectrum)[:N // 2]

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

    HOW IT WORKS
        1. Divide the two arrays  ->  sample_sb / reference_sb
           numpy divides element by element, so no loop is needed.

    WORKED EXAMPLE
        >>> transmittance(np.array([5.0, 1.0]), np.array([10.0, 10.0]))
        array([0.5, 0.1])


    Returns
    -------
    numpy.ndarray
        Transmittance (dimensionless). Multiply by 100 yourself when you want %.
    """
    return sample_sb / reference_sb

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

    HOW IT WORKS
        1. Negative base-10 log  ->  -np.log10(T)
           Use np.log10, not np.log, which is the natural logarithm.

    WORKED EXAMPLE
        >>> absorbance(np.array([0.5, 0.1]))
        array([0.30103, 1.     ])
        T = 0.1 gives A = 1 exactly: one absorbance unit means a tenth of the
        light gets through. T = 0.01 gives A = 2, and so on.


    Returns
    -------
    numpy.ndarray
        Absorbance (dimensionless).
    """
    return -np.log10(T)

CORRELATION_TABLE = [
    ("O-H stretch (alcohol, broad)", 3200, 3550),
    ("C-H stretch (sp3)",            2850, 2990),
    ("C=O stretch (carbonyl)",       1680, 1760),
    ("O-H bend / C-H bend",          1350, 1480),
    ("C-O stretch",                  1000, 1260),
]


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
    # TODO: 1. centre = find_zero_burst(rifg)
    # TODO: 2. r_win = window_around(rifg, centre, N)   (and s_win likewise)
    # TODO: 3. I0 = single_beam(r_win);  I = single_beam(s_win)
    # TODO: 4. wn = wavenumber_axis(N, k)
    # TODO: 5. T = transmittance(I, I0)
    # TODO: return wn, T
    raise NotImplementedError("compute_spectrum: chain the given pipeline functions together")


# --- WRITTEN FOR YOU: plumbing, not physics. Read it and move on. ---
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
    threshold = np.percentile(A, 10)
    anchors = A <= threshold
    coeffs = np.polyfit(wn[anchors], A[anchors], deg=2)
    baseline = np.polyval(coeffs, wn)
    return A - baseline


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


# --- WRITTEN FOR YOU: plumbing, not physics. Read it and move on. ---
def assign(peak_wn):
    """Match each peak wavenumber to entries in CORRELATION_TABLE.

    Returns
    -------
    list of (wavenumber, [matching group labels])
    """
    results = []
    for w in peak_wn:
        groups = [name for name, lo, hi in CORRELATION_TABLE if lo <= w <= hi]
        results.append((w, groups))
    return results


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


# --- WRITTEN FOR YOU: plumbing, not physics. Read it and move on. ---
def spectrum_from_window(window, k):
    """Single-beam magnitude spectrum + matching wavenumber axis for a window.

    Convenience wrapper so the experiments below stay short. Reuse your
    given pipeline functions: length here is len(window) (which may be zero-filled).
    """
    N = len(window)
    I = single_beam(window)
    wn = wavenumber_axis(N, k)
    return wn, I


# -------------------------------------------------------------------------
# PART 1 -- explore the raw interferograms  (Section A Q1)
# -------------------------------------------------------------------------
def part1_explore():
    # -----------------------------------------------------------------
    # STEP 1  --  Load the six data files.
    #
    # Use load_dpt(...). Remember: for the *_rifg and *_sifg files you
    # want column 1 (the signal). For the *_ab files load BOTH columns
    # (column=None) so you keep the wavenumber axis together with the values.
    # -----------------------------------------------------------------
    # TODO: load background interferograms
    b_rifg = None   # load_dpt("background_rifg.dpt", column=1)
    b_sifg = None
    # TODO: load ethanol interferograms
    e_rifg = None
    e_sifg = None
    # TODO: load the instrument absorbance spectra (both columns)
    b_ab = None     # load_dpt("background_ab.dpt", column=None)
    e_ab = None

    if b_rifg is None:
        raise SystemExit(
            "STEP 1 not done yet: load the data files above, then remove this guard."
        )

    # -----------------------------------------------------------------
    # STEP 2  --  Basic sanity checks. Fill in the prints.
    #
    # Questions to note in your report:
    #   - How many points does each interferogram contain?
    #   - What is the total optical-path-difference range being sampled?
    # -----------------------------------------------------------------
    # TODO: print len(...) of each interferogram
    print("TODO: print how many points each interferogram has")

    # -----------------------------------------------------------------
    # STEP 3  --  Find the zero burst of the ethanol reference interferogram.
    #
    #   - At which index does the zero burst sit? Is it near the start,
    #       middle, or end of the scan? Why do you think the instrument places
    #       it there?
    # -----------------------------------------------------------------
    # TODO: i_zb = find_zero_burst(e_rifg); print(i_zb)

    # -----------------------------------------------------------------
    # STEP 4  --  Plot the full interferograms.
    #
    # Plot background RIFG and SIFG on one figure. Label axes
    # ("Optical path difference / a.u." vs "Signal / a.u."), add a legend and
    # a title. Then make a SECOND plot zoomed into +/- 200 points around the
    # zero burst so you can actually see the wiggles of the centre burst.
    #
    #   - Away from the centre burst the signal looks like almost-flat noise.
    #       Why does nearly all the spectral information live in that narrow
    #       burst region?
    # -----------------------------------------------------------------
    # TODO: your plotting code here
    plt.figure(figsize=(8, 4))
    # plt.plot(b_rifg, label="Background RIFG")
    # plt.plot(b_sifg, label="Background SIFG")
    plt.title("Exercise 1 -- replace me with your interferogram plot")
    plt.xlabel("Optical path difference / a.u.")
    plt.ylabel("Signal / a.u.")
    plt.legend()
    plt.tight_layout()
    plt.show()

    # -----------------------------------------------------------------
    # STEP 5  --  Compare reference vs sample.
    #
    # Overlay the ethanol RIFG and SIFG (zoomed around the burst).
    #   - The two bursts look almost identical to the eye. If they are so
    #       similar, where does the chemical information (the sample's
    #       absorption) actually hide? (Hint: think about the *small*
    #       differences and what the FFT in exercise 2 will do with them.)
    # -----------------------------------------------------------------
    # TODO: your comparison plot here

    print("\nDone once this runs and you have answered Section A Q1\n"
          "in the manual.")


# -------------------------------------------------------------------------
# PART 2 -- interferogram to spectrum  (Section A Q2)
# -------------------------------------------------------------------------
def part2_spectrum():
    # -----------------------------------------------------------------
    # STEP 1  --  Load the interferograms (as in exercise 1).
    # -----------------------------------------------------------------
    # TODO: load ethanol_rifg / ethanol_sifg with load_dpt(..., column=1)
    e_rifg = None
    e_sifg = None
    if e_rifg is None:
        raise SystemExit("Load the ethanol interferograms first.")

    # -----------------------------------------------------------------
    # STEP 2  --  Run your pipeline.
    # -----------------------------------------------------------------
    wn, T = compute_spectrum(e_rifg, e_sifg, N, K)
    A = absorbance(T)

    # -----------------------------------------------------------------
    # STEP 3  --  Plot the transmittance spectrum.
    #
    # Convention: IR spectra run with wavenumber DECREASING left-to-right,
    # so set plt.xlim(4000, 500). Plot T in percent.
    #
    #   - Identify the strong dip near ~3300 cm^-1 and the group of dips
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
    #   - Absorbance and transmittance carry the same information. Why do
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
    #   - Do the peak POSITIONS match? Do the peak HEIGHTS match?
    #   - List two reasons your curve might differ from the instrument's
    #       (hint: apodization and phase correction -- more in exercise 4).
    # -----------------------------------------------------------------
    # TODO: e_ab = load_dpt("ethanol_ab.dpt", column=None)
    # TODO: overlay plot of your A vs e_ab

    print("\nDone once this runs and you have answered Section A Q2\n"
          "(and the band names for Q3) in the manual.")


# -------------------------------------------------------------------------
# PART 3 -- baseline, peaks, assignment  (Section A Q3, Q8)
# -------------------------------------------------------------------------
def part3_peaks():
    # -----------------------------------------------------------------
    # STEP 1  --  Recompute the ethanol absorbance spectrum.
    # -----------------------------------------------------------------
    e_rifg = None   # TODO: load_dpt("ethanol_rifg.dpt", column=1)
    e_sifg = None   # TODO
    if e_rifg is None:
        raise SystemExit("Load the ethanol interferograms first.")
    wn, T = compute_spectrum(e_rifg, e_sifg, N, K)
    A = absorbance(T)

    # Restrict to the chemically useful fingerprint + functional-group region.
    mask = (wn >= 500) & (wn <= 4000)
    wn, A = wn[mask], A[mask]

    # -----------------------------------------------------------------
    # STEP 2  --  Baseline correction. Plot before vs after.
    #   - What artefacts in the raw absorbance did the baseline correction
    #       remove? Did it distort any real peaks?
    # -----------------------------------------------------------------
    A_bc = baseline_correct(wn, A)
    # TODO: plot A and A_bc together.

    # -----------------------------------------------------------------
    # STEP 3  --  Peak detection. Mark the peaks on the plot.
    #   - How sensitive is the peak list to your `height`/`distance`
    #       choices? Give the values you settled on and why.
    # -----------------------------------------------------------------
    peak_wn, peak_A = find_bands(wn, A_bc, height=None, distance=None)
    # TODO: plot A_bc and overlay the detected peaks (e.g. plt.scatter).

    # -----------------------------------------------------------------
    # STEP 4  --  Assign the peaks.
    #   - Produce a table: peak position -> assigned group. Are all of
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
    #   - Name one band that lets you tell the two substances apart at a
    #       glance, and say which bond it belongs to.
    # -----------------------------------------------------------------
    # TODO (optional): repeat for a second sample and overlay.

    print("\nDone once this runs and you have answered Section A Q3 and Q8\n"
          "in the manual.")


# -------------------------------------------------------------------------
# PART 4 -- resolution experiments  (Section A Q4, Q5, Q6)
# -------------------------------------------------------------------------
def part4_resolution():
    rifg = None   # TODO: load_dpt("ethanol_rifg.dpt", column=1)
    sifg = None   # TODO
    if rifg is None:
        raise SystemExit("Load the ethanol interferograms first (see exercise 1).")

    centre = find_zero_burst(rifg)

    # -----------------------------------------------------------------
    # EXPERIMENT A  --  Resolution vs window length N.
    #
    # Loop over several window lengths, e.g. [2**10, 2**12, 2**14], compute the
    # transmittance each time and overlay the spectra (zoom into a region with
    # close peaks, e.g. 2800-3050 cm^-1).
    #
    #   - As N increases, what happens to the linewidths and to your ability
    #       to separate neighbouring bands?
    #   - FT-IR resolution (cm^-1) is roughly 1 / (max optical path
    #       difference). Explain qualitatively why a longer window = better
    #       resolution, in terms of how far the mirror travels.
    # -----------------------------------------------------------------
    plt.figure(figsize=(8, 4))
    for N in [2 ** 10, 2 ** 12, 2 ** 14]:
        r = window_around(rifg, centre, N)
        s = window_around(sifg, centre, N)
        # TODO: single-beam of each, transmittance, wavenumber axis, then plot
        # wn, I0 = spectrum_from_window(r, K); _, I = spectrum_from_window(s, K)
        # T = transmittance(I, I0)
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
    #   - Which apodization gives the sharpest peaks? Which gives the least
    #       ringing (fewest negative side-lobes around strong bands)? Describe
    #       the trade-off in one sentence.
    # -----------------------------------------------------------------
    N = 2 ** 12
    r = window_around(rifg, centre, N)
    s = window_around(sifg, centre, N)
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
    #   - Zero-filling makes the curve look smoother. Did it actually improve
    #       the true RESOLUTION (your ability to separate two real peaks), or
    #       only the sampling of the curve? Justify using what you saw in
    #       Experiment A.
    # -----------------------------------------------------------------
    # TODO: implement the zero-fill comparison

    print("\nDone once experiments A-C run and you have answered\n"
          "Section A Q4, Q5 and Q6 in the manual.")


def main():
    """Run all four parts in order."""
    part1_explore()
    part2_spectrum()
    part3_peaks()
    part4_resolution()
    print("\nDone once all four parts run and you have answered\n"
          "Section A Q1 to Q8 in the manual.")


# ---------------------------------------------------------------------------
# Self-tests -- run `python section_A_basics.py` to grade yourself.
# Do not modify below this line.
# ---------------------------------------------------------------------------
def _report(name, ok, msg=""):
    tick = "PASS" if ok else "FAIL"
    print(f"[{tick}] {name}" + (f"  --  {msg}" if msg and not ok else ""))
    return ok


def _selftest():
    print("Running Section A self-tests...\n")
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
    passed = sum(bool(r) for r in results)
    print(f"\n{passed}/{len(results)} checks passed.")
    if passed == len(results):
        print("All good -- now run:  python section_A_basics.py run")
    else:
        print("Keep going: fix the FAIL items above, then re-run.")


if __name__ == "__main__":
    import sys

    if "run" in sys.argv[1:]:
        main()
    else:
        _selftest()
        print("\nTo run the analysis on your own data:  "
              "python section_A_basics.py run")
