"""
Exercise 1 -- Loading and exploring the interferogram
=====================================================

Goal
----
Get the raw data off disk, look at it, and understand what an interferogram
is *before* you Fourier-transform anything.

Before you start
----------------
* Complete `irtools.py` first and make sure `python irtools.py` passes all
  checks. This exercise imports the functions you wrote there.
* Make sure the data files are in the same folder as this script:
      background_rifg.dpt, background_sifg.dpt, background_ab.dpt
      ethanol_rifg.dpt,    ethanol_sifg.dpt,    ethanol_ab.dpt
  (If you don't have real instrument data, run `python generate_demo_data.py`
  first to create synthetic files you can practise on.)

What RIFG / SIFG / AB mean
--------------------------
* RIFG = Reference InterFeroGram  (background / empty beam)
* SIFG = Sample   InterFeroGram   (beam through your sample)
* AB   = the ABsorbance spectrum the instrument software computed, so you can
         later check your own result against the "official" one.

Run this file with:  python exercise1_interferogram.py
"""

import numpy as np
import matplotlib.pyplot as plt

import irtools as ir


# The instrument constant (sampling / max wavenumber). Do not change.
K = 16716.51


def main():
    # -----------------------------------------------------------------
    # STEP 1  --  Load the six data files.
    #
    # Use ir.load_dpt(...). Remember: for the *_rifg and *_sifg files you
    # want column 1 (the signal). For the *_ab files load BOTH columns
    # (column=None) so you keep the wavenumber axis together with the values.
    # -----------------------------------------------------------------
    # TODO: load background interferograms
    b_rifg = None   # ir.load_dpt("background_rifg.dpt", column=1)
    b_sifg = None
    # TODO: load ethanol interferograms
    e_rifg = None
    e_sifg = None
    # TODO: load the instrument absorbance spectra (both columns)
    b_ab = None     # ir.load_dpt("background_ab.dpt", column=None)
    e_ab = None

    if b_rifg is None:
        raise SystemExit(
            "STEP 1 not done yet: load the data files above, then remove this guard."
        )

    # -----------------------------------------------------------------
    # STEP 2  --  Basic sanity checks. Fill in the prints.
    #
    # Questions to note in your report:
    #   Q1. How many points does each interferogram contain?
    #   Q2. What is the total optical-path-difference range being sampled?
    # -----------------------------------------------------------------
    # TODO: print len(...) of each interferogram
    print("TODO: print how many points each interferogram has")

    # -----------------------------------------------------------------
    # STEP 3  --  Find the zero burst of the ethanol reference interferogram.
    #
    #   Q3. At which index does the zero burst sit? Is it near the start,
    #       middle, or end of the scan? Why do you think the instrument places
    #       it there?
    # -----------------------------------------------------------------
    # TODO: i_zb = ir.find_zero_burst(e_rifg); print(i_zb)

    # -----------------------------------------------------------------
    # STEP 4  --  Plot the full interferograms.
    #
    # Plot background RIFG and SIFG on one figure. Label axes
    # ("Optical path difference / a.u." vs "Signal / a.u."), add a legend and
    # a title. Then make a SECOND plot zoomed into +/- 200 points around the
    # zero burst so you can actually see the wiggles of the centre burst.
    #
    #   Q4. Away from the centre burst the signal looks like almost-flat noise.
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
    #   Q5. The two bursts look almost identical to the eye. If they are so
    #       similar, where does the chemical information (the sample's
    #       absorption) actually hide? (Hint: think about the *small*
    #       differences and what the FFT in exercise 2 will do with them.)
    # -----------------------------------------------------------------
    # TODO: your comparison plot here

    print("\nExercise 1 complete once every TODO is filled in and every Q is answered.")


if __name__ == "__main__":
    main()
