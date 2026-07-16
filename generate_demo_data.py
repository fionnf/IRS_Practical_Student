"""
generate_demo_data.py  --  make synthetic .dpt files to practise on
===================================================================

Run this ONCE if you do not have real instrument data:

    python generate_demo_data.py

It writes six files that behave like the real ones, so every exercise
(1 through 4) runs end-to-end:

    background_rifg.dpt   background_sifg.dpt   background_ab.dpt
    ethanol_rifg.dpt      ethanol_sifg.dpt      ethanol_ab.dpt

The "ethanol" here is a caricature with a few characteristic bands -- good
enough to learn the data analysis, but do NOT quote these numbers as real
ethanol values. When you have genuine measurements, just drop the real .dpt
files in this folder and the exercises will use those instead.

This is a *tool*, not an exercise, so it is written out in full. Read it if
you are curious how a spectrometer turns a spectrum back into an
interferogram -- exercise 5 has you build that yourself.
"""

import numpy as np

K = 16716.51          # instrument constant (Nyquist wavenumber, cm^-1)
M = 2 ** 15           # number of interferogram points
HALF = M // 2 + 1     # length of a one-sided (rfft) spectrum

# One-sided wavenumber grid the spectrum lives on.
WN_FULL = np.linspace(0.0, K, HALF)

# Source/detector envelope: a smooth, positive single-beam background.
ENVELOPE = 0.2 + np.exp(-((WN_FULL - 2500.0) / 2000.0) ** 2)

# Caricature "ethanol" absorption bands: (centre cm^-1, height, FWHM cm^-1).
ETHANOL_BANDS = [
    (3350, 0.45, 250),   # broad O-H stretch
    (2975, 0.35, 45),    # C-H stretch
    (2930, 0.30, 45),    # C-H stretch
    (1450, 0.15, 80),    # C-H bend
    (1050, 0.40, 90),    # C-O stretch
    (880,  0.12, 60),
]


def _gauss(wn, centre, height, fwhm):
    sigma = fwhm / 2.3548
    return height * np.exp(-((wn - centre) ** 2) / (2 * sigma ** 2))


def absorbance(wn, bands):
    A = np.zeros_like(wn)
    for centre, height, fwhm in bands:
        A += _gauss(wn, centre, height, fwhm)
    return A


def spectrum_to_interferogram(single_beam, rng, noise=2e-3):
    """One-sided spectrum -> real, centre-bursted interferogram with noise."""
    ifg = np.fft.irfft(single_beam, n=M)
    ifg = np.fft.fftshift(ifg)                 # put the centre burst in the middle
    ifg = ifg + rng.normal(0, noise * ifg.max(), size=ifg.shape)
    return ifg


def save_dpt(path, y, x=None):
    if x is None:
        x = np.arange(len(y), dtype=float)
    np.savetxt(path, np.column_stack([x, y]), delimiter=",", fmt="%.8g")
    print(f"  wrote {path}  ({len(y)} points)")


def main():
    rng = np.random.default_rng(42)

    # ---- Background: empty beam. Reference and sample are both just the
    #      source envelope with independent noise, so their ratio is ~1. ----
    b_ref_sb = ENVELOPE.copy()
    b_smp_sb = ENVELOPE.copy()
    b_rifg = spectrum_to_interferogram(b_ref_sb, rng)
    b_sifg = spectrum_to_interferogram(b_smp_sb, rng)

    # ---- Ethanol: sample beam is attenuated by Beer-Lambert transmittance. ----
    A = absorbance(WN_FULL, ETHANOL_BANDS)
    e_ref_sb = ENVELOPE.copy()
    e_smp_sb = ENVELOPE * 10.0 ** (-A)
    e_rifg = spectrum_to_interferogram(e_ref_sb, rng)
    e_sifg = spectrum_to_interferogram(e_smp_sb, rng)

    print("Writing synthetic .dpt files...")
    save_dpt("background_rifg.dpt", b_rifg)
    save_dpt("background_sifg.dpt", b_sifg)
    save_dpt("ethanol_rifg.dpt", e_rifg)
    save_dpt("ethanol_sifg.dpt", e_sifg)

    # ---- "Instrument" absorbance files (wavenumber, absorbance), 500-4000. ----
    m = (WN_FULL >= 500) & (WN_FULL <= 4000)
    save_dpt("ethanol_ab.dpt", A[m], x=WN_FULL[m])
    save_dpt("background_ab.dpt", np.zeros(m.sum()), x=WN_FULL[m])

    print("\nDone. You can now run exercise1_interferogram.py")


if __name__ == "__main__":
    main()
