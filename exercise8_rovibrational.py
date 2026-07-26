"""
Exercise 8 -- Rovibrational analysis of HCl (and DCl / H37Cl if resolved)
============================================================================

Goal
----
Section E of the practical has you record the gas-phase rovibrational
spectrum of HCl and, on graph paper, extract the rotational constant B_e and
bond length r_e from the P- and R-branch line positions. This exercise does
the SAME physics computationally, and pushes further than the paper version:

  * a proper multiple linear regression (not just "plot and eyeball a
    slope") that also fits the CENTRIFUGAL DISTORTION constant D_e,
  * honest uncertainties on B_e, D_e and r_e (using exercise7's toolkit),
  * a from-first-principles isotope check: does H37Cl give the same bond
    length as H35Cl, as the Born-Oppenheimer approximation demands?

The rovibrational line positions of a diatomic (including centrifugal
distortion) can be written as a SINGLE formula using the running index m:

    nu(m) = nu_0 + 2*B_e*m - 4*D_e*m^3

    m = J'' + 1   for the R branch   (m = 1, 2, 3, ...)
    m = -J''      for the P branch   (m = -1, -2, -3, ...)

(You can derive this yourself from F(J) = B_e*J(J+1) - D_e*J^2(J+1)^2 and
nu = nu_0 + F(J') - F(J'') with J' = J'' +/- 1 -- try it, it is good
practice and exactly the derivation in Schwenz & Polik, J. Chem. Educ. 1999,
already in the bibliography.)

Because nu(m) is LINEAR in the two "features" m and m^3, you can recover
nu_0, B_e and D_e in one multiple linear regression -- no iterative fitting
needed.

Before you start
-----------------
* Complete exercise7_uncertainty.py first; this file imports it.
* Use your own gas-cell HCl spectrum (wavenumber, absorbance) if you have
  it. Otherwise run `generate_demo_data.py` to get `hcl_gas_ab.dpt`, a
  synthetic natural-abundance HCl spectrum built from real literature
  constants (good for practising the pipeline -- do not quote its numbers
  as "your" measured H35Cl/H37Cl constants).

Run with:  python exercise8_rovibrational.py
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

import irtools as ir
import exercise7_uncertainty as unc

# Physical constants (SI)
H = 6.62607015e-34       # J s
C_SI = 2.99792458e8      # m/s
C_CGS = 2.99792458e10    # cm/s
U = 1.66053906660e-27    # kg per amu

M_H = 1.007825 * U
M_D = 2.014102 * U        # deuterium -- for the H2SO4 vs D2SO4 -> HCl vs DCl comparison
M_CL35 = 34.968853 * U
M_CL37 = 36.965903 * U


# ---------------------------------------------------------------------------
# STEP 1 -- find the line positions in your spectrum
# ---------------------------------------------------------------------------
def find_lines(wn, A, height, distance):
    """Return the wavenumbers of resolved absorption lines.

    Same idea as exercise3's find_bands: use scipy.signal.find_peaks. Real
    gas-phase lines are much narrower than the broad liquid-phase bands you
    saw in exercises 1-3, so `distance` (minimum spacing, in SAMPLES) needs
    to be much smaller here.

    Returns
    -------
    ndarray of line-centre wavenumbers, ascending order.
    """
    # TODO: idx, _ = find_peaks(A, height=height, distance=distance)
    # TODO: return wn[idx]
    raise NotImplementedError("find_lines")


# ---------------------------------------------------------------------------
# STEP 2 -- assign each line an m-index (m = J''+1 for R, m = -J'' for P)
# ---------------------------------------------------------------------------
def predict_positions(nu0_guess, be_guess, m_values):
    """Predicted line positions (no centrifugal distortion) for a guess.

    Use nu(m) = nu0_guess + 2*be_guess*m -- the simple rigid-rotor formula
    is good enough for an initial assignment; you refine nu0/Be/De properly
    in STEP 3.

    Returns
    -------
    ndarray, same length as m_values.
    """
    # TODO: implement
    raise NotImplementedError("predict_positions")


def assign_m(line_wn, nu0_guess, be_guess, m_range=range(-9, 10)):
    """Match each observed line to its nearest predicted m-index.

    Parameters
    ----------
    line_wn : ndarray
        Observed line positions from find_lines.
    nu0_guess, be_guess : float
        A rough starting guess (read the approximate band CENTRE/gap-in-the-
        middle off your plot for nu0, and the approximate spacing between
        adjacent lines divided by 2 for be_guess).
    m_range : iterable of int
        Candidate m values to consider (m=0 is skipped -- there is no
        m=0 line, the "missing line" at the band centre).

    Returns
    -------
    m_assigned : ndarray of int
    wn_assigned : ndarray of float
        Only the lines that got a confident (closest-match, within a few
        wavenumbers) assignment; both arrays the same length, sorted by m.

    Hints
    -----
    * For each candidate m in m_range (m != 0), predict its position, find
      the closest line in `line_wn`, and keep the pair if the residual is
      small (e.g. < 3 cm^-1 -- tune this to your own data/resolution).
    * Watch out for the same observed line being claimed by two different m
      values; keep only the best match per line if that happens.
    """
    # TODO: implement the nearest-match assignment described above
    raise NotImplementedError("assign_m")


# ---------------------------------------------------------------------------
# STEP 3 -- multiple linear regression: nu(m) = nu0 + 2*Be*m - 4*De*m^3
# ---------------------------------------------------------------------------
def fit_rovibrational(m_values, nu_values):
    """Multiple linear regression for nu0, B_e, D_e (with uncertainties).

    Build the design matrix X = [1, m, m^3] (columns), solve
    nu = X @ [nu0, 2*Be, -4*De] by ordinary least squares, then get
    parameter standard errors from the residuals -- same idea as
    exercise7's linregress_with_uncertainty, generalised to 3 parameters.

    Parameters
    ----------
    m_values, nu_values : ndarray, same length n (n >= 4, more is better).

    Returns
    -------
    nu0, Be, De : float
    se_nu0, se_Be, se_De : float
        1-sigma standard errors.

    Method
    ------
    1. X = np.column_stack([np.ones_like(m), m, m**3])
    2. coeffs, residuals, rank, sv = np.linalg.lstsq(X, nu_values, rcond=None)
       coeffs = [nu0, a, b] where a = 2*Be, b = -4*De
    3. resid = nu_values - X @ coeffs
       s2 = sum(resid**2) / (n - 3)             (3 fitted parameters)
    4. cov = s2 * np.linalg.inv(X.T @ X)         (parameter covariance matrix)
       se = sqrt(diag(cov))                       -> se_nu0, se_a, se_b
    5. Be = a/2, De = -b/4; propagate: se_Be = se_a/2, se_De = se_b/4
    """
    # TODO: implement steps 1-5
    raise NotImplementedError("fit_rovibrational")


# ---------------------------------------------------------------------------
# STEP 4 -- bond length from B_e (with propagated uncertainty)
# ---------------------------------------------------------------------------
def bond_length(be, se_be, mu):
    """r_e (metres) and its 1-sigma uncertainty, from B_e = h/(8*pi^2*c*mu*r_e^2).

    Parameters
    ----------
    be, se_be : float
        Rotational constant and its standard error, in cm^-1.
    mu : float
        Reduced mass in kg.

    Returns
    -------
    r_e, se_r_e : float, in metres.

    Hints
    -----
    * Rearrange: r_e = sqrt(h / (8*pi^2*c*mu*be)), with `be` converted from
      cm^-1 to m^-1 (multiply by 100) before use, and c in m/s.
    * r_e depends on be^(-1/2), so the RELATIVE uncertainty on r_e is HALF
      the relative uncertainty on be -- use
      unc.propagate_power(se_be/be, 0.5) to get the relative uncertainty on
      r_e, then multiply by r_e to get se_r_e.
    """
    # TODO: implement
    raise NotImplementedError("bond_length")


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------
def main():
    wn, A = None, None   # TODO: wn, A = ir.load_dpt("hcl_gas_ab.dpt", column=None).T
    if wn is None:
        raise SystemExit("Load your (or the demo) HCl spectrum first.")

    # -----------------------------------------------------------------
    # STEP 1: find lines and plot them marked on the spectrum.
    #   Q1. How many lines did you find? Do you see a "missing line" gap
    #       near the band centre where m=0 would be? Why is there no m=0
    #       transition (think about the selection rule for a vibration-
    #       rotation transition)?
    # -----------------------------------------------------------------
    lines = find_lines(wn, A, height=0.05, distance=5)
    plt.figure(figsize=(9, 4))
    plt.plot(wn, A, color="black", lw=0.8)
    plt.scatter(lines, np.interp(lines, wn, A), color="red", s=15, zorder=3)
    plt.xlabel("Wavenumber / cm$^{-1}$")
    plt.ylabel("Absorbance")
    plt.title("HCl gas-phase spectrum -- detected lines")
    plt.tight_layout()
    plt.show()

    # -----------------------------------------------------------------
    # STEP 2: assign m-indices.
    # Read a rough nu0 (gap centre) and Be (half the average line spacing)
    # off the plot above and fill them in.
    #   Q2. State the nu0_guess and Be_guess you read off the plot, and how
    #       you estimated them.
    # -----------------------------------------------------------------
    nu0_guess = None   # TODO: e.g. 2886.0
    be_guess = None    # TODO: e.g. 10.5
    if nu0_guess is None:
        raise SystemExit("Set nu0_guess and be_guess from your plot first.")
    m_vals, wn_assigned = assign_m(lines, nu0_guess, be_guess)
    print(f"Assigned {len(m_vals)} of {len(lines)} detected lines.")

    # -----------------------------------------------------------------
    # STEP 3: fit nu0, Be, De by multiple linear regression.
    #   Q3. Report nu0, Be, De with their uncertainties (correct sig figs --
    #       do not report more digits than your uncertainty justifies).
    #   Q4. Plot nu(m) - 2*Be*m (the "centrifugal-distortion-only" residual)
    #       against m^3 and confirm it is a straight line through nu0 with
    #       slope -4*De. Does ignoring D_e entirely (i.e. only fitting a
    #       straight line to nu vs m) measurably bias your Be? Compare the
    #       two fits.
    # -----------------------------------------------------------------
    nu0, Be, De, se_nu0, se_Be, se_De = fit_rovibrational(m_vals, wn_assigned)
    print(f"nu0 = {nu0:.3f} +/- {se_nu0:.3f} cm^-1")
    print(f"Be  = {Be:.4f} +/- {se_Be:.4f} cm^-1")
    print(f"De  = {De:.2e} +/- {se_De:.2e} cm^-1")

    # -----------------------------------------------------------------
    # STEP 4: bond length.
    #   Q5. Report r_e with uncertainty in picometres. Compare with the
    #       literature H-Cl bond length (127.5 pm) using a t-test
    #       (unc.welch_t_test) against your value -- is the difference
    #       significant, or consistent with your measurement uncertainty?
    # -----------------------------------------------------------------
    mu_hcl = M_H * M_CL35 / (M_H + M_CL35)
    r_e, se_r_e = bond_length(Be, se_Be, mu_hcl)
    print(f"r_e = {r_e*1e12:.2f} +/- {se_r_e*1e12:.2f} pm")

    # -----------------------------------------------------------------
    # STEP 5 (advanced, resolution permitting) -- isotope check.
    #
    # Natural HCl is 75.77% H35Cl / 24.23% H37Cl. Depending on your
    # instrument resolution (Section A/exercise4!) you may or may not see
    # the H37Cl lines resolved as separate, weaker shoulders next to the
    # main H35Cl lines. If you can identify a second, weaker progression:
    #
    #   Q6. Fit it the same way (STEPs 2-4) to get Be(H37Cl) and r_e(H37Cl).
    #       Compute the PREDICTED Be(H37Cl)/Be(H35Cl) ratio from the reduced
    #       masses alone (no fitting) and compare with your two independent
    #       measurements using unc.welch_t_test. Are r_e(H35Cl) and
    #       r_e(H37Cl) the same within uncertainty? Explain why the
    #       Born-Oppenheimer approximation predicts they MUST be.
    #   Q7. If you could NOT resolve the isotope doublet, use exercise4's
    #       resolution relation (Delta-nu ~ k/N) to estimate the minimum
    #       window length N your instrument would need to resolve it, given
    #       the isotope shift you just predicted.
    # -----------------------------------------------------------------
    mu37 = M_H * M_CL37 / (M_H + M_CL37)
    predicted_be_ratio = mu_hcl / mu37
    print(f"\nPredicted Be(H37Cl)/Be(H35Cl) from reduced mass alone: {predicted_be_ratio:.5f}")
    # TODO (if you can resolve the H37Cl progression): repeat STEPs 2-4 for
    # it and compare against this prediction.

    print("\nExercise 8 complete once STEPs 1-4 run and Q1-Q5 are answered "
          "(Q6-Q7 if your data resolves the isotope doublet).")


if __name__ == "__main__":
    main()
