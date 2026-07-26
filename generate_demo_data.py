"""
generate_demo_data.py  --  make synthetic .dpt files to practise on
===================================================================

Run this ONCE if you do not have real instrument data:

    python generate_demo_data.py

It writes files that behave like the real ones, so every exercise runs
end-to-end:

    background_rifg.dpt   background_sifg.dpt   background_ab.dpt
    ethanol_rifg.dpt      ethanol_sifg.dpt      ethanol_ab.dpt
    hcl_gas_ab.dpt         (for exercise8_rovibrational.py)

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


# ---------------------------------------------------------------------------
# Synthetic HCl gas-phase rovibrational spectrum, for exercise8_rovibrational.py
# Built from real literature constants for H35Cl / H37Cl (not a caricature --
# these are the accepted textbook values), so this is a reasonable stand-in
# for your gas-cell data while you're waiting for lab time.
# ---------------------------------------------------------------------------
_C_CGS = 2.99792458e10       # cm/s
_H = 6.62607015e-34          # J s
_KB = 1.380649e-23           # J/K
_U = 1.66053906660e-27       # kg per amu

_M_H = 1.007825 * _U
_M_CL35 = 34.968853 * _U
_M_CL37 = 36.965903 * _U

# Literature H35Cl constants (band origin, rotational constant, centrifugal
# distortion). H37Cl constants below are then PREDICTED from these via the
# isotope reduced-mass scaling -- exactly the calculation exercise8 asks you
# to do yourself, so do not peek until you've derived it.
_NU0_35 = 2885.9    # cm^-1
_BE_35 = 10.5934    # cm^-1
_DE_35 = 5.315e-4   # cm^-1
_ABUNDANCE_35 = 0.7577
_ABUNDANCE_37 = 0.2423


def _isotope_scale(nu0, be, mu_ref, mu_new):
    ratio = mu_ref / mu_new
    return nu0 * np.sqrt(ratio), be * ratio


def hcl_line_positions(nu0, be, de, j_max=9):
    """Return (m, nu) for the P and R branch lines of a rovibrational band."""
    m_vals, nus = [], []
    for J in range(0, j_max):          # R branch, m = J+1
        m = J + 1
        m_vals.append(m)
        nus.append(nu0 + 2 * be * m - 4 * de * m ** 3)
    for J in range(1, j_max):          # P branch, m = -J
        m = -J
        m_vals.append(m)
        nus.append(nu0 + 2 * be * m - 4 * de * m ** 3)
    return np.array(m_vals), np.array(nus)


def hcl_gas_spectrum(wn, T=298.0, linewidth=1.6):
    """Synthetic natural-abundance HCl absorbance spectrum on grid `wn`."""
    mu35 = _M_H * _M_CL35 / (_M_H + _M_CL35)
    mu37 = _M_H * _M_CL37 / (_M_H + _M_CL37)
    nu0_37, be_37 = _isotope_scale(_NU0_35, _BE_35, mu35, mu37)
    de_37 = _DE_35 * (be_37 / _BE_35) ** 3   # De ~ Be^3 (Kratzer relation)

    A = np.zeros_like(wn)
    for nu0, be, de, abundance in [
        (_NU0_35, _BE_35, _DE_35, _ABUNDANCE_35),
        (nu0_37, be_37, de_37, _ABUNDANCE_37),
    ]:
        m_vals, nus = hcl_line_positions(nu0, be, de)
        for m, nu in zip(m_vals, nus):
            J = m - 1 if m > 0 else -m
            pop = (2 * J + 1) * np.exp(-_H * _C_CGS * be * J * (J + 1) / (_KB * T))
            A += abundance * pop * _gauss(wn, nu, 1.0, linewidth)

    A = A / A.max() * 0.75   # rescale to a plausible peak absorbance
    return A


# ---------------------------------------------------------------------------
# Synthetic polymer reference spectra, for exercise9_polymer_id.py
#
# Band positions are approximately correct for each polymer (they are the
# genuinely diagnostic ones a chemist would use), but the relative intensities
# are simplified. Treat these as a TEACHING library for learning how library
# matching works -- not as a substitute for a real commercial reference
# library when identifying an actual unknown.
# ---------------------------------------------------------------------------
POLYMER_BANDS = {
    # (centre cm^-1, height, FWHM cm^-1)
    "PE": [
        (2915, 0.90, 30), (2848, 0.75, 28),      # CH2 asym / sym stretch
        (1463, 0.30, 22),                          # CH2 bend
        (730, 0.22, 10), (720, 0.26, 10),         # CH2 rock doublet -> crystallinity
    ],
    "PS": [
        (3082, 0.16, 14), (3060, 0.22, 14), (3025, 0.26, 14),  # aromatic C-H
        (2920, 0.40, 26), (2850, 0.22, 26),                     # aliphatic C-H
        (1601, 0.35, 14), (1583, 0.16, 12),
        (1493, 0.42, 14), (1452, 0.45, 16),                     # ring modes
        (756, 0.70, 12), (698, 0.85, 12),                       # monosubst. benzene
    ],
    "PET": [
        (2960, 0.20, 26),
        (1712, 1.00, 24),                          # ester C=O -- very strong
        (1410, 0.25, 16), (1340, 0.28, 18),
        (1240, 0.85, 24), (1090, 0.60, 22),        # C-O
        (720, 0.45, 14),                            # aromatic
    ],
    "PVC": [
        (2910, 0.40, 30), (2850, 0.22, 28),
        (1425, 0.35, 18), (1330, 0.22, 16), (1250, 0.30, 18),
        (690, 0.55, 20), (615, 0.60, 22),          # C-Cl stretch -- halogen tell
    ],
}


def polymer_spectrum(wn, name):
    """Absorbance spectrum of one reference polymer on grid `wn`."""
    return absorbance(wn, POLYMER_BANDS[name])


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

    # ---- Synthetic HCl gas-phase rovibrational spectrum (exercise 8). ----
    wn_hcl = np.linspace(2600, 3150, 6000)
    A_hcl = hcl_gas_spectrum(wn_hcl)
    save_dpt("hcl_gas_ab.dpt", A_hcl, x=wn_hcl)

    # ---- Polymer reference library + two unknowns (exercise 9). ----
    wn_poly = np.linspace(600, 3200, 5200)
    for name in POLYMER_BANDS:
        A_poly = polymer_spectrum(wn_poly, name)
        A_poly = A_poly + rng.normal(0, 2e-3, size=A_poly.shape)
        save_dpt(f"polymer_ref_{name}.dpt", A_poly, x=wn_poly)

    # Unknown 1: a single pure polymer, with a sloping baseline and extra noise
    # (i.e. realistically messy, but genuinely one material).
    unknown1 = polymer_spectrum(wn_poly, "PS")
    unknown1 = unknown1 + 0.08 * (wn_poly - wn_poly.min()) / np.ptp(wn_poly)
    unknown1 = unknown1 + rng.normal(0, 6e-3, size=unknown1.shape)
    save_dpt("polymer_unknown_1.dpt", unknown1, x=wn_poly)

    # Unknown 2: a LAMINATE -- two polymers superimposed. Deliberately included
    # so that blind top-hit library matching gives a confident but INCOMPLETE
    # answer (see exercise9, STEP 4).
    unknown2 = 0.62 * polymer_spectrum(wn_poly, "PET") + 0.38 * polymer_spectrum(wn_poly, "PE")
    unknown2 = unknown2 + rng.normal(0, 5e-3, size=unknown2.shape)
    save_dpt("polymer_unknown_2.dpt", unknown2, x=wn_poly)

    print("\nDone. You can now run exercise1_interferogram.py")


if __name__ == "__main__":
    main()
