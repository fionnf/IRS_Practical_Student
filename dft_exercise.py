# ==========================================
# IR Spectroscopy Data Analysis in Python
# Guided Exercise Sheet
# ==========================================

import numpy as np
import matplotlib.pyplot as plt

# 1. Sampling rate given by the IR spectrometer
k = 16716.51  # Hz (just given, don’t change)

# 2. Load interferogram data
# In R, this was done with `read.table("file.dpt", sep=",")`
# In Python, use `np.loadtxt("file.dpt", delimiter=",")`

# TODO: Load the following files (second column only for *_RIFG and *_SIFG):
# - background_rifg.dpt
# - background_sifg.dpt
# - background_ab.dpt
# - ethanol_rifg.dpt
# - ethanol_sifg.dpt
# - ethanol_ab.dpt
#
# Hint: Use slicing [:, 1] after loading to select column 2.

# Example (complete for background_rifg only, do the rest yourself):
b_RIFG = np.loadtxt("background_rifg.dpt", delimiter=",")[:, 1]

# Students: Now load the rest here
# b_SIFG = ...
# b_AB   = ...
# EtOH_RIFG = ...
# EtOH_SIFG = ...
# EtOH_AB   = ...

# 3. Plot interferograms
# First: plot background reference interferogram (RIFG)
plt.plot(b_RIFG, color="black", label="Background RIFG")

# TODO: Plot the other background interferograms (SIFG, AB)
# plt.plot(...)

plt.xlabel("x / a.u.")
plt.ylabel("signal / a.u.")
plt.legend()
plt.title("Background Interferograms")
plt.show()

# 4. Fourier Transform
# Use numpy.fft.fft to calculate spectra from interferograms.
# Hint: np.fft.fft(signal) gives the frequency spectrum.
# Hint2: Use np.fft.fftfreq for frequency axis.

# Example for one interferogram:
fft_b_RIFG = np.fft.fft(b_RIFG)
freqs = np.fft.fftfreq(len(b_RIFG), d=1/k)

# TODO: Plot the magnitude of the FFT vs. frequency
# plt.plot(freqs, np.abs(fft_b_RIFG))

# 5. Compare Background vs. Ethanol
# TODO: Overlay spectra (background vs. ethanol) to see absorption features.

# ==========================================
# ✨ Extension (Optional):
# - Normalize the spectra
# - Zoom into a specific wavenumber range
# - Compute transmission = Sample / Reference
# ==========================================
