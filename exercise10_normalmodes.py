"""
Exercise 10 -- Normal-mode analysis: where vibrational frequencies come from
=============================================================================

Goal
----
Everywhere else in this practical you have treated a vibrational band as a
number to be measured. Here you compute one from first principles: given the
masses and the force constants, you PREDICT the spectrum. This is the
computational companion to Section F (CS2), and it closes the loop on a
question the manual deliberately leaves hanging.

In Section F you used two closed-form results for a linear symmetric XY2
molecule and found that a single force constant k_r, fitted to the symmetric
stretch, over-predicts the antisymmetric stretch by roughly 7-8%. The manual
tells you this is because the two bonds are not mechanically independent.
Here you fix it properly: you introduce the stretch-stretch interaction
constant k_rr, solve for BOTH constants from your two measured frequencies,
and confirm the model then reproduces the spectrum exactly.

You will also get something the closed forms cannot give you: the
EIGENVECTORS, i.e. the actual pattern of atomic motion in each normal mode.
Those are what make the IR/Raman selection rules obvious rather than
memorised.

The method (Wilson's GF matrix)
-------------------------------
For vibrations described by internal coordinates (here: the two bond lengths
r1 and r2), the classical vibrational problem reduces to an EIGENVALUE
problem:

    G F L = L  Lambda,        Lambda_ii = lambda_i = (2 pi c nu_i)^2

  * F is the force-constant matrix (the potential energy)
  * G is the inverse-kinetic-energy matrix (the masses and geometry)
  * eigenvalues of the product G F give the frequencies
  * eigenvectors give the mode shapes

For a linear symmetric XY2 (Y--X--Y, e.g. S=C=S), the stretching block is

    F = [[k_r,  k_rr],        G = [[1/m_X + 1/m_Y,  -1/m_X    ],
         [k_rr, k_r ]]             [-1/m_X,          1/m_X + 1/m_Y]]

where m_X is the CENTRAL atom (C) and m_Y a TERMINAL atom (S). The off-
diagonal -1/m_X is what couples the two bonds through the shared central
atom -- it is there even when k_rr = 0, which is why the two stretches have
different frequencies at all.

Companion tool: the interactive **Normal Mode Explorer** (linked from the lab
manual) animates these eigenvectors and shows the dipole moment and
polarizability changing in real time, which is worth five minutes of your
attention before you start.

Run with:  python exercise10_normalmodes.py
"""

import numpy as np

# Physical constants
C_CGS = 2.99792458e10        # cm/s
U = 1.66053906660e-27        # kg per amu

# Atomic masses (amu)
M_C = 12.000
M_S = 31.97207
M_O = 15.99491

# Observed CS2 fundamentals (cm^-1) -- replace with YOUR measured values.
CS2_NU1_OBS = 656.0      # symmetric stretch   (strong in Raman)
CS2_NU2_OBS = 397.0      # bend, doubly degenerate
CS2_NU3_OBS = 1535.0     # antisymmetric stretch (strong in IR)

CS2_BOND_LENGTH = 1.5529e-10   # m


# ---------------------------------------------------------------------------
# 1. Build the matrices
# ---------------------------------------------------------------------------
def f_matrix(k_r, k_rr):
    """Force-constant matrix for the stretching block of a linear XY2.

    Returns
    -------
    ndarray, shape (2, 2):   [[k_r, k_rr], [k_rr, k_r]]

    The diagonal is the force constant of each individual bond; the
    off-diagonal k_rr says how much stretching one bond stiffens (or softens)
    the other. Setting k_rr = 0 recovers the "simple valence force field"
    used in Section F.
    """
    # TODO: implement me
    raise NotImplementedError("f_matrix")


def g_matrix(m_central, m_terminal):
    """Inverse-kinetic-energy (Wilson G) matrix for the same stretching block.

    Parameters
    ----------
    m_central, m_terminal : float
        Masses in KILOGRAMS (convert from amu with the constant ``U``).

    Returns
    -------
    ndarray, shape (2, 2):
        [[1/m_c + 1/m_t,  -1/m_c],
         [-1/m_c,          1/m_c + 1/m_t]]

    (The off-diagonal is ``cos(theta)/m_central`` in general; for a LINEAR
    molecule theta = 180 degrees so cos(theta) = -1.)
    """
    # TODO: implement me
    raise NotImplementedError("g_matrix")


# ---------------------------------------------------------------------------
# 2. Solve the eigenvalue problem
# ---------------------------------------------------------------------------
def solve_modes(G, F):
    """Diagonalise G F and return wavenumbers (cm^-1) plus mode eigenvectors.

    The eigenvalues of the (generally non-symmetric) product ``G @ F`` are
    lambda_i = (2 pi c nu_i)^2, so

        nu_i [cm^-1] = sqrt(lambda_i) / (2 pi c)

    with c in cm/s.

    Returns
    -------
    wavenumbers : ndarray, shape (2,), ASCENDING order.
    vectors : ndarray, shape (2, 2)
        Column ``vectors[:, i]`` is the eigenvector for ``wavenumbers[i]``,
        expressed in the internal coordinates (r1, r2). Sort the columns to
        match the sorted wavenumbers.

    Hints
    -----
    * ``np.linalg.eig(G @ F)`` returns (eigenvalues, eigenvectors).
    * Eigenvalues may come back with tiny imaginary parts from round-off --
      take ``np.real`` (and ``np.abs`` before the square root).
    * ``np.argsort`` gives you the permutation to sort BOTH arrays consistently.
    """
    # TODO: implement me
    raise NotImplementedError("solve_modes")


def classify_mode(eigenvector, tol=1e-6):
    """Label a stretching eigenvector 'symmetric' or 'antisymmetric'.

    In internal coordinates (r1, r2):
      * both bonds lengthen together (components the SAME sign) -> symmetric
      * one lengthens while the other shortens (OPPOSITE signs) -> antisymmetric

    Returns
    -------
    str : "symmetric" or "antisymmetric"

    Hints
    -----
    * Look at the sign of the product of the two components.
    """
    # TODO: implement me
    raise NotImplementedError("classify_mode")


# ---------------------------------------------------------------------------
# 3. Invert the problem: force constants FROM measured frequencies
# ---------------------------------------------------------------------------
def fit_force_constants(nu_sym, nu_asym, m_central, m_terminal):
    """Solve for k_r AND k_rr from the two measured stretching frequencies.

    The closed-form eigenvalues of the system above are

        lambda_sym  = (k_r + k_rr) / m_terminal
        lambda_asym = (k_r - k_rr) * (1/m_terminal + 2/m_central)

    Two equations, two unknowns -- solve them. (Derive these yourself by
    applying G F to the symmetric combination (1,1)/sqrt2 and the
    antisymmetric combination (1,-1)/sqrt2; it is three lines of algebra and
    it explains where the closed forms in the Section F manual came from.)

    Parameters
    ----------
    nu_sym, nu_asym : float    measured wavenumbers in cm^-1.
    m_central, m_terminal : float   masses in KILOGRAMS.

    Returns
    -------
    k_r, k_rr : float, in N/m.

    Hints
    -----
    * lambda = (2 * pi * C_CGS * nu)^2 for nu in cm^-1.
    * Let A = k_r + k_rr and B = k_r - k_rr; get A and B from the two lambda
      equations, then k_r = (A+B)/2 and k_rr = (A-B)/2.
    """
    # TODO: implement me
    raise NotImplementedError("fit_force_constants")


# ---------------------------------------------------------------------------
# 4. The bending mode
# ---------------------------------------------------------------------------
def bend_wavenumber(k_delta, bond_length, m_central, m_terminal):
    """Wavenumber (cm^-1) of the doubly-degenerate bend of a linear XY2.

        lambda_bend = (2 * k_delta / l^2) * (1/m_terminal + 2/m_central)

    Parameters
    ----------
    k_delta : float    bending force constant, in N*m/rad^2.
    bond_length : float   equilibrium bond length l, in metres.
    m_central, m_terminal : float   masses in kg.

    Returns
    -------
    float, wavenumber in cm^-1.
    """
    # TODO: implement me
    raise NotImplementedError("bend_wavenumber")


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------
def main():
    m_c = M_C * U
    m_s = M_S * U

    # -----------------------------------------------------------------
    # STEP 1 -- Reproduce the Section F result (simple valence force field).
    #
    # Fit k_r from the symmetric stretch ALONE, with k_rr forced to 0, then
    # predict the antisymmetric stretch. This is exactly what Section F Q1/Q2
    # asked you to do by hand -- now verify it with the matrix machinery.
    #
    #   Q1. Report your k_r and your predicted nu3. Confirm the matrix result
    #       agrees with the closed form you used in Section F (they must, or
    #       one of them is wrong -- this is a genuine check on your algebra).
    #   Q2. What is the % error against the measured nu3, and in which
    #       direction? Does the sign of the error tell you anything about
    #       whether k_rr should be positive or negative?
    # -----------------------------------------------------------------
    lam1 = (2 * np.pi * C_CGS * CS2_NU1_OBS) ** 2
    k_r_simple = lam1 * m_s          # from lambda_sym = k_r/m_S with k_rr = 0
    # TODO: G = g_matrix(m_c, m_s); F = f_matrix(k_r_simple, 0.0)
    # TODO: nus, vecs = solve_modes(G, F); print them and classify each mode
    # TODO: compare nus against (CS2_NU1_OBS, CS2_NU3_OBS)

    # -----------------------------------------------------------------
    # STEP 2 -- Fix it: fit BOTH constants.
    #
    #   Q3. Report k_r and k_rr from `fit_force_constants`. Express k_rr as a
    #       percentage of k_r. Feed both back into f_matrix/solve_modes and
    #       confirm you now reproduce BOTH measured frequencies (to within
    #       round-off).
    #   Q4. Is k_rr small compared with k_r? What does its SIGN mean
    #       physically -- when one C=S bond stretches, does the other become
    #       easier or harder to stretch? Propose a bonding rationale (think
    #       about how the shared central carbon's orbitals are being used).
    # -----------------------------------------------------------------
    # TODO: k_r, k_rr = fit_force_constants(CS2_NU1_OBS, CS2_NU3_OBS, m_c, m_s)
    # TODO: verify by re-solving and comparing with the observed values

    # -----------------------------------------------------------------
    # STEP 3 -- Look at the eigenvectors.
    #
    #   Q5. Print the eigenvector for each stretching mode and classify it
    #       with `classify_mode`. For the SYMMETRIC mode, argue from the
    #       eigenvector (not from a memorised rule) that the molecular dipole
    #       moment does not change during the vibration -- and therefore that
    #       the mode is IR-INACTIVE. Then argue that the molecular
    #       polarizability DOES change, making it Raman-active.
    #   Q6. Do the same for the ANTISYMMETRIC mode and show it comes out the
    #       other way round. You have now DERIVED the mutual exclusion rule
    #       for this molecule rather than quoting it.
    # -----------------------------------------------------------------
    # TODO: print and interpret the eigenvectors

    # -----------------------------------------------------------------
    # STEP 4 -- The bend.
    #
    #   Q7. Invert `bend_wavenumber` to find the k_delta that reproduces your
    #       measured nu2. Bending constants are usually quoted in
    #       mdyn*Angstrom/rad^2 (1 mdyn*A/rad^2 = 1e-18 N*m/rad^2). Is your
    #       value in the typical 0.1-1 range? A bending force constant is much
    #       smaller than a stretching one -- explain physically why bending a
    #       bond is "cheaper" than stretching it.
    # -----------------------------------------------------------------
    # TODO: solve for k_delta from CS2_NU2_OBS and check its magnitude

    # -----------------------------------------------------------------
    # STEP 5 (challenge) -- A different molecule.
    #
    #   Q8. CO2 is also a linear symmetric XY2 (nu1 = 1333, nu3 = 2349 cm^-1
    #       -- note nu1 is Raman-only, exactly as for CS2). Repeat STEP 2 for
    #       CO2 using M_O for the terminal mass. Compare k_r(CO2) with
    #       k_r(CS2). Which molecule has the stiffer bond, and is that what
    #       you would predict from bond order and atom size? Compare k_rr/k_r
    #       for the two molecules as well.
    #   Q9. Why can neither molecule's symmetric stretch be seen in the IR,
    #       no matter how concentrated your sample is? Contrast this with a
    #       BENT XY2 such as water (nu1 = 3657 cm^-1, which IS IR-active) --
    #       what does the change in geometry do to the argument you made in
    #       Q5?
    # -----------------------------------------------------------------
    # TODO: repeat for CO2

    print("Exercise 10 complete once STEPs 1-4 run and Q1-Q7 are answered "
          "(Q8-Q9 for the challenge).")


# ---------------------------------------------------------------------------
# Self-tests -- run `python exercise10_normalmodes.py` to grade yourself.
# Do not modify below this line.
# ---------------------------------------------------------------------------
def _report(name, ok, msg=""):
    tick = "PASS" if ok else "FAIL"
    print(f"[{tick}] {name}" + (f"  --  {msg}" if msg and not ok else ""))
    return ok


def _selftest():
    print("Running exercise10 self-tests...\n")
    results = []
    m_c, m_s = M_C * U, M_S * U

    try:
        F = f_matrix(700.0, 50.0)
        ok = (np.allclose(F, [[700.0, 50.0], [50.0, 700.0]]))
        results.append(_report("f_matrix", ok, "layout wrong"))
    except NotImplementedError:
        results.append(_report("f_matrix", False, "not implemented"))
    except Exception as e:
        results.append(_report("f_matrix", False, f"raised {e!r}"))

    try:
        G = g_matrix(m_c, m_s)
        expect = np.array([[1 / m_c + 1 / m_s, -1 / m_c], [-1 / m_c, 1 / m_c + 1 / m_s]])
        ok = np.allclose(G, expect, rtol=1e-9)
        results.append(_report("g_matrix", ok, "check the -1/m_central off-diagonal"))
    except NotImplementedError:
        results.append(_report("g_matrix", False, "not implemented"))
    except Exception as e:
        results.append(_report("g_matrix", False, f"raised {e!r}"))

    # With k_rr = 0 the two stretches must come out at the Section F values.
    try:
        lam1 = (2 * np.pi * C_CGS * 656.0) ** 2
        k_r = lam1 * m_s
        nus, vecs = solve_modes(g_matrix(m_c, m_s), f_matrix(k_r, 0.0))
        ok = (len(nus) == 2 and np.isclose(nus[0], 656.0, rtol=1e-4)
              and np.isclose(nus[1], 1650.2, rtol=1e-3)
              and np.all(np.diff(nus) > 0))
        results.append(_report("solve_modes", ok,
                               "expected ~656 and ~1650 cm^-1 ascending for k_rr=0"))
    except NotImplementedError:
        results.append(_report("solve_modes", False, "not implemented"))
    except Exception as e:
        results.append(_report("solve_modes", False, f"raised {e!r}"))

    try:
        ok = (classify_mode(np.array([0.707, 0.707])) == "symmetric"
              and classify_mode(np.array([0.707, -0.707])) == "antisymmetric")
        results.append(_report("classify_mode", ok, "sign logic wrong"))
    except NotImplementedError:
        results.append(_report("classify_mode", False, "not implemented"))
    except Exception as e:
        results.append(_report("classify_mode", False, f"raised {e!r}"))

    try:
        k_r, k_rr = fit_force_constants(656.0, 1535.0, m_c, m_s)
        # round-trip: these constants must reproduce the input frequencies
        nus, _ = solve_modes(g_matrix(m_c, m_s), f_matrix(k_r, k_rr))
        ok = (np.isclose(nus[0], 656.0, rtol=1e-4) and np.isclose(nus[1], 1535.0, rtol=1e-4)
              and 0 < k_rr < k_r)
        results.append(_report("fit_force_constants", ok,
                               "must round-trip to the input frequencies"))
    except NotImplementedError:
        results.append(_report("fit_force_constants", False, "not implemented"))
    except Exception as e:
        results.append(_report("fit_force_constants", False, f"raised {e!r}"))

    try:
        nu = bend_wavenumber(5.656e-19, CS2_BOND_LENGTH, m_c, m_s)
        ok = np.isclose(nu, 397.0, rtol=2e-3)
        results.append(_report("bend_wavenumber", ok, "expected ~397 cm^-1 for CS2"))
    except NotImplementedError:
        results.append(_report("bend_wavenumber", False, "not implemented"))
    except Exception as e:
        results.append(_report("bend_wavenumber", False, f"raised {e!r}"))

    passed = sum(bool(r) for r in results)
    print(f"\n{passed}/{len(results)} checks passed.")
    if passed == len(results):
        print("All good -- now work through main() and answer Q1-Q9.")
    else:
        print("Keep going: fix the FAIL items above, then re-run.")


if __name__ == "__main__":
    _selftest()
