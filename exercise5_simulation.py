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

This exercise needs NO instrument data -- you generate everything. That is the
point: a simulator lets you separate the physics from the messy real data.

You will implement the modelling functions; the driver at the bottom runs the
experiments and asks the questions.

Run with:  python exercise5_simulation.py
"""

import numpy as np
import matplotlib.pyplot as plt


# A small synthetic "molecule": a list of absorption bands (centre cm^-1,
# peak absorbance per unit concentration, width cm^-1). Feel free to edit.
BANDS = [
    (3300, 0.8, 120),   # broad O-H-like band
    (2950, 0.5, 40),    # C-H stretch
    (1710, 1.0, 25),    # sharp C=O-like band
    (1050, 0.7, 60),    # C-O-like band
]

WN = np.linspace(400, 4000, 4000)   # wavenumber grid for the "true" spectrum


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

    print("Exercise 5 complete once Parts A-D run and Q1-Q4 are answered.")


if __name__ == "__main__":
    main()
