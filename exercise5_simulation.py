"""
Exercise 5 (experimental) -- Build your own FT-IR spectrometer in silico
========================================================================

Everything so far went in ONE direction: interferogram -> spectrum. In a real
instrument the physics runs the OTHER way too: a known spectrum of light
produces an interferogram at the detector. In this exercise you build the
whole loop yourself and use it to run experiments you could never do by just
staring at fixed data files:

  Part A  Forward model : known spectrum  -> interferogram   (inverse FFT)
  Part B  Round trip    : interferogram   -> recovered spectrum, and check it
  Part C  Noise & signal averaging : why co-adding scans improves SNR ~ sqrt(n)
  Part D  Beer-Lambert quantitation : build a calibration curve and measure an
          "unknown" concentration.
  Part E  Band deconvolution : recover two overlapping bands from one blended
          peak by fitting a sum-of-Gaussians model (non-linear least squares).
  Part F  Monte Carlo uncertainty : repeat the Part D measurement many times
          under noise to turn a single concentration estimate into an actual
          confidence interval.

This exercise needs NO instrument data -- you generate everything. That is the
point: a simulator lets you separate the physics from the messy real data, and
run experiments (many repeats, deliberately overlapping bands, arbitrary
scan counts) that would be impractical on the real instrument.

You will implement the modelling functions; the driver at the bottom runs the
experiments and asks the questions.

Run with:  python exercise5_simulation.py
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit


# A small synthetic "molecule": a list of absorption bands (centre cm^-1,
# peak absorbance per unit concentration, width cm^-1). Feel free to edit.
BANDS = [
    (3300, 0.8, 120),   # broad O-H-like band
    (2950, 0.5, 40),    # C-H stretch
    (1710, 1.0, 25),    # sharp C=O-like band
    (1050, 0.7, 60),    # C-O-like band
]

WN = np.linspace(400, 4000, 4000)   # wavenumber grid for the "true" spectrum

# Two closely-spaced, partially-overlapping bands for Part E (deconvolution).
# Close enough together that the sum looks like ONE broad, slightly
# asymmetric peak rather than two resolved bands -- the situation you often
# meet in a crowded fingerprint region.
OVERLAP_TRUE = [
    (1690.0, 0.55, 30.0),
    (1728.0, 0.45, 30.0),
]


# ---------------------------------------------------------------------------
# Part A -- the forward model
# ---------------------------------------------------------------------------
def gaussian_band(wn, centre, height, width):
    """A single Gaussian absorption band evaluated on the array ``wn``.

    Use the standard Gaussian shape

        height * exp( -(wn - centre)^2 / (2 * sigma^2) )

    where ``sigma = width / 2.355`` converts a full-width-at-half-maximum
    (FWHM = ``width``) into the Gaussian sigma.

    Returns
    -------
    ndarray  same shape as ``wn``.
    """
    # TODO: implement the Gaussian
    raise NotImplementedError("gaussian_band")


def absorbance_spectrum(wn, concentration=1.0):
    """Total absorbance = sum of all BANDS, scaled by concentration.

    Beer-Lambert: absorbance is proportional to concentration, so multiply the
    summed band absorbances (defined at unit concentration) by
    ``concentration``.
    """
    # TODO: sum gaussian_band(...) over BANDS, then multiply by concentration
    raise NotImplementedError("absorbance_spectrum")


def spectrum_to_transmittance(A):
    """Beer-Lambert inverse: T = 10**(-A)."""
    # TODO
    raise NotImplementedError("spectrum_to_transmittance")


def make_interferogram(single_beam_spectrum):
    """Turn a (real, one-sided) intensity spectrum into an interferogram.

    A real spectrum corresponds to a real, symmetric interferogram. The clean
    way to get it is the inverse real FFT:

        ifg = np.fft.irfft(single_beam_spectrum)

    Then roll the array so the centre burst sits in the MIDDLE (nicer to look
    at and matches real instruments): ``np.fft.fftshift(ifg)``.

    Returns
    -------
    ndarray  the interferogram.
    """
    # TODO: irfft then fftshift
    raise NotImplementedError("make_interferogram")


# ---------------------------------------------------------------------------
# Part B/C helpers -- recovering the spectrum and adding noise
# ---------------------------------------------------------------------------
def recover_spectrum(ifg):
    """Inverse of make_interferogram: interferogram -> single-beam spectrum.

    Undo the fftshift (``np.fft.ifftshift``) and take the real FFT magnitude
    (``np.abs(np.fft.rfft(...))``). Return the recovered single-beam spectrum.
    """
    # TODO
    raise NotImplementedError("recover_spectrum")


def add_detector_noise(ifg, noise_level, rng):
    """Add Gaussian white noise to an interferogram (models detector noise).

    Parameters
    ----------
    ifg : ndarray
    noise_level : float   standard deviation of the noise.
    rng : np.random.Generator   pass in np.random.default_rng(seed) so results
        are reproducible.

    Returns
    -------
    ndarray   noisy interferogram.
    """
    # TODO: return ifg + rng.normal(0, noise_level, size=ifg.shape)
    raise NotImplementedError("add_detector_noise")


def coadd_scans(clean_ifg, n_scans, noise_level, rng):
    """Average ``n_scans`` independently-noisy copies of ``clean_ifg``.

    Real FT-IR co-adds many mirror sweeps and averages them. Each sweep sees
    fresh, independent noise but the SAME underlying signal, so averaging
    beats the noise down.

    Returns
    -------
    ndarray   the averaged interferogram.
    """
    # TODO: build n_scans noisy copies (add_detector_noise) and return their mean
    raise NotImplementedError("coadd_scans")


# ---------------------------------------------------------------------------
# Part D -- quantitation
# ---------------------------------------------------------------------------
def peak_absorbance(wn, A, centre, halfwidth=40):
    """Return the maximum absorbance within +/- halfwidth of ``centre``.

    A simple band-height measurement for the calibration curve.
    """
    # TODO: mask wn to [centre-halfwidth, centre+halfwidth] and return A[mask].max()
    raise NotImplementedError("peak_absorbance")


# ---------------------------------------------------------------------------
# Part E -- deconvolving two overlapping bands
# ---------------------------------------------------------------------------
def two_gaussian_model(wn, c1, h1, w1, c2, h2, w2):
    """Sum of two Gaussian bands, as a single callable for curve fitting.

    This is exactly ``gaussian_band(wn, c1, h1, w1) + gaussian_band(wn, c2,
    h2, w2)`` -- the function signature (all parameters flattened, no tuples)
    is what ``scipy.optimize.curve_fit`` expects.

    Returns
    -------
    ndarray  same shape as ``wn``.
    """
    # TODO: return the sum of the two gaussian_band(...) calls
    raise NotImplementedError("two_gaussian_model")


def fit_overlapping_bands(wn, A, p0):
    """Fit ``two_gaussian_model`` to data ``(wn, A)`` starting from guess ``p0``.

    Parameters
    ----------
    wn, A : ndarray   the blended spectrum region to fit.
    p0 : sequence of 6 floats
        Initial guess ``(c1, h1, w1, c2, h2, w2)``. A poor guess can make the
        fit converge on the wrong (or an unphysical) answer -- that is the
        point of Q6 below.

    Returns
    -------
    popt : ndarray, length 6   best-fit parameters, same order as p0.
    pcov : ndarray, 6x6        covariance matrix of the fit (its diagonal
        gives the variance -- i.e. uncertainty squared -- of each parameter).

    Hints
    -----
    * ``from scipy.optimize import curve_fit`` (already imported at the top).
    * ``popt, pcov = curve_fit(two_gaussian_model, wn, A, p0=p0)``.
    """
    # TODO: call curve_fit and return (popt, pcov)
    raise NotImplementedError("fit_overlapping_bands")


# ---------------------------------------------------------------------------
# Part F -- Monte Carlo uncertainty on a concentration measurement
# ---------------------------------------------------------------------------
def monte_carlo_concentration(wn, true_concentration, band_centre,
                               noise_std, slope, intercept, n_trials, rng):
    """Repeat a noisy concentration measurement many times.

    A single "unknown" measurement gives you ONE number. To know how much to
    trust that number, simulate the measurement many times with independent
    noise realisations and look at the SPREAD of the results.

    For each of ``n_trials`` repeats:
      1. Generate a noisy absorbance spectrum at ``true_concentration``
         (``absorbance_spectrum`` + ``rng.normal(0, noise_std, size=wn.shape)``).
      2. Measure the band height at ``band_centre`` with ``peak_absorbance``.
      3. Invert the calibration line (``height = slope*conc + intercept``) to
         get an estimated concentration for that trial.

    Returns
    -------
    ndarray, length n_trials
        The Monte Carlo sample of estimated concentrations.
    """
    # TODO: loop n_trials times, build each estimate as described, collect
    #       them in a list/array and return it.
    raise NotImplementedError("monte_carlo_concentration")


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------
def main():
    rng = np.random.default_rng(0)

    # ---------------- Part A: forward model ----------------
    A_true = absorbance_spectrum(WN, concentration=1.0)
    T = spectrum_to_transmittance(A_true)
    ifg = make_interferogram(T)

    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    ax[0].plot(WN, A_true)
    ax[0].set(title="Part A: true absorbance", xlabel="cm$^{-1}$", ylabel="A")
    ax[0].set_xlim(4000, 400)
    ax[1].plot(ifg)
    ax[1].set(title="...its interferogram", xlabel="sample", ylabel="signal")
    plt.tight_layout(); plt.show()
    # Q1. Which feature of the interferogram (its centre burst) came from which
    #     feature of the spectrum? What does the SHARP 1710 band contribute to
    #     the interferogram compared with the BROAD 3300 band?

    # ---------------- Part B: round trip ----------------
    recovered = recover_spectrum(ifg)
    # Compare `recovered` (single-beam) with T. They should match up to scaling.
    # TODO: plot recovered vs T (normalise if needed) and confirm agreement.
    # Q2. Does your recovered spectrum reproduce the input? What sets the
    #     wavenumber spacing of the recovered spectrum?

    # ---------------- Part C: noise & signal averaging ----------------
    # For a range of scan counts, co-add noisy interferograms, recover the
    # spectrum, and measure the noise (e.g. std of a signal-free baseline
    # region). Plot measured noise vs n_scans on log-log axes.
    #
    # Theory: noise should fall as 1/sqrt(n_scans), i.e. slope -0.5 on log-log.
    noise_level = 0.05
    scan_counts = [1, 4, 16, 64, 256]
    measured_noise = []
    for n in scan_counts:
        avg = coadd_scans(ifg, n, noise_level, rng)
        rec = recover_spectrum(avg)
        # TODO: estimate the residual noise in `rec` (e.g. std of a flat region,
        #       or std of rec - recover_spectrum(ifg)) and append it.
        # measured_noise.append(...)
        pass
    # TODO: plt.loglog(scan_counts, measured_noise, 'o-'); overlay a 1/sqrt(n) guide.
    # Q3. Does your measured noise follow the 1/sqrt(n) law? To halve the noise,
    #     by what factor must you multiply the number of scans (and therefore
    #     the measurement time)? Is signal averaging an efficient way to buy
    #     signal-to-noise?

    # ---------------- Part D: Beer-Lambert calibration ----------------
    # Build a calibration curve from KNOWN concentrations, then measure an
    # unknown. Use the sharp 1710 cm^-1 band.
    concentrations = np.array([0.2, 0.4, 0.6, 0.8, 1.0])
    heights = []
    for c in concentrations:
        A_c = absorbance_spectrum(WN, concentration=c)
        # add a little measurement noise so it is not a perfect line
        A_c = A_c + rng.normal(0, 0.01, size=A_c.shape)
        # TODO: h = peak_absorbance(WN, A_c, centre=1710); heights.append(h)
        pass
    # TODO: fit a straight line height = m*concentration (+ b) with np.polyfit.
    # TODO: plot calibration points + fitted line.

    # An unknown sample (pretend you don't know its concentration):
    c_unknown_true = 0.73
    A_unknown = absorbance_spectrum(WN, concentration=c_unknown_true) \
        + rng.normal(0, 0.01, size=WN.shape)
    # TODO: measure its 1710 band height, invert your calibration line to get
    #       the estimated concentration, and compare with c_unknown_true.
    # Q4. How close is your estimate? Which band would give the most reliable
    #     calibration and why (think about the linewidth, height, and whether
    #     it overlaps its neighbours)?

    # -----------------------------------------------------------------
    # Part E  --  Deconvolve two overlapping bands.
    #
    # Build ONE blended spectrum from OVERLAP_TRUE (two Gaussians 38 cm^-1
    # apart) and add a little noise. Plot it -- to the eye it looks like a
    # single, slightly lopsided peak. Then fit `two_gaussian_model` to it
    # with `fit_overlapping_bands`, starting from a REASONABLE initial guess
    # (e.g. read the visual peak position off the plot for both starting
    # centres). Overlay: the blended data, your fitted sum, and the two
    # individual fitted Gaussian components.
    # -----------------------------------------------------------------
    region = (WN >= 1550) & (WN <= 1850)
    wn_e = WN[region]
    A_blend = sum(gaussian_band(wn_e, c, h, w) for c, h, w in OVERLAP_TRUE)
    A_blend_noisy = A_blend + rng.normal(0, 0.01, size=wn_e.shape)
    # TODO: p0 = (1690, 0.5, 30, 1725, 0.5, 30)   # or your own visual estimate
    # TODO: popt, pcov = fit_overlapping_bands(wn_e, A_blend_noisy, p0)
    # TODO: plot data, popt-sum, and the two individual components (using
    #       gaussian_band with popt[:3] and popt[3:] separately).
    # Q5. Compare your fitted (centre, height, width) for each component with
    #     OVERLAP_TRUE. How close did the fit get? Report the parameter
    #     uncertainties from sqrt(np.diag(pcov)) alongside your fitted values.
    # Q6. Deliberately fit again from a BAD initial guess (e.g. both centres
    #     at 1600, or centres swapped). Does the fit still converge to the
    #     right answer? What does this tell you about deconvolving real,
    #     unlabelled overlapping bands where you don't already know the truth?

    # -----------------------------------------------------------------
    # Part F  --  Monte Carlo uncertainty on your Part D measurement.
    #
    # Using the calibration slope/intercept you fit in Part D, run
    # `monte_carlo_concentration` for a few hundred trials at the SAME
    # c_unknown_true and noise_std used above. Plot a histogram of the
    # resulting concentration estimates.
    # -----------------------------------------------------------------
    # TODO: samples = monte_carlo_concentration(WN, c_unknown_true, 1710,
    #                                            0.01, m, b, n_trials=300, rng=rng)
    # TODO: plt.hist(samples, bins=30); report samples.mean(), samples.std()
    # Q7. Does the mean of your Monte Carlo distribution recover c_unknown_true?
    #     Report the standard deviation of the distribution as your measurement
    #     uncertainty (a proper "+/-" on your Part D answer).
    # Q8. Repeat Part F using a WEAKER band (e.g. the 1050 cm^-1 band with a
    #     smaller height) instead of the sharp 1710 band. Does the uncertainty
    #     grow or shrink? Connect this to what you found in Part D, Q4, about
    #     what makes a good quantitation band.

    print("Exercise 5 complete once Parts A-F run and Q1-Q8 are answered.")


if __name__ == "__main__":
    main()
