\# ==========================================
# IR Spectroscopy Data Analysis in Python
# Guided Exercise Sheet
# ==========================================
# This sheet will guide you through loading, visualizing, and analyzing IR interferogram data.
# Follow each step and fill in the TODOs.

import numpy as np
import matplotlib.pyplot as plt

# 1. Sampling rate given by the IR spectrometer (do not change)
k = 16716.51  # Hz

# 2. Load interferogram data
# Each .dpt file contains two columns. For *_RIFG and *_SIFG, use only the second column.
# Use np.loadtxt("filename", delimiter=",")[:, 1] to select column 2.

# Example (background_rifg only):
b_RIFG = np.loadtxt("background_rifg.dpt", delimiter=",")[:, 1]

#Load the other files (fill in the lines below)
b_SIFG = np.loadtxt("background_sifg.dpt", delimiter=",")[:, 1]
b_AB   = np.loadtxt("background_ab.dpt", delimiter=",")
EtOH_RIFG = np.loadtxt("ethanol_rifg.dpt", delimiter=",")[:, 1]
EtOH_SIFG = np.loadtxt("ethanol_sifg.dpt", delimiter=",")[:, 1]
EtOH_AB   = np.loadtxt("ethanol_ab.dpt", delimiter=",")

# 3. Slice around the zero burst (maximum) for better spectral resolution

# The "zero burst" is the point of maximum signal in the interferogram,
# corresponding to zero optical path difference in the interferometer.
# This region contains the most useful spectral information.
# By extracting a window around the zero burst before the Fourier Transform,
# you improve spectral resolution and reduce noise.
# After the FFT, only the positive half of the spectrum (wavenumbers) is physically meaningful for IR,
# so we plot just that half to obtain a clean, interpretable IR spectrum.

# This step is crucial for IR analysis. Find the maximum and extract a window around it.

N = 2**14  # Window size (adjust if needed)
i_zb = np.argmax(np.abs(EtOH_RIFG))  # Find zero burst in sample
RIFG = EtOH_RIFG[int(i_zb-N/2):int(i_zb+N/2)]
SIFG = EtOH_SIFG[int(i_zb-N/2):int(i_zb+N/2)]

# 4. Plot interferograms
plt.figure(figsize=(8, 4))
plt.plot(b_RIFG, color="black", label="Background RIFG")
plt.plot(b_SIFG, color="blue", label="Background SIFG")
plt.xlabel("Optical Path Difference / a.u.")
plt.ylabel("Signal / a.u.")
plt.legend()
plt.title("Background Interferograms")
plt.show()

# 5. Fourier Transform and wavenumber axis
# Compute FFT and plot only the positive half (IR convention)
FT_RIFG = np.fft.fft(RIFG)
FT_SIFG = np.fft.fft(SIFG)
I0 = np.abs(FT_RIFG)[:N//2]
I  = np.abs(FT_SIFG)[:N//2]
wn = np.linspace(0, k, N//2)  # Wavenumber axis (cm⁻¹)

# 6. Plot transmission spectrum (sample/reference)
T = I / I0
plt.figure(figsize=(8, 4))
plt.plot(wn, T*100, color='red', label="Transmittance (%)")
plt.xlim(4000, 500)
plt.ylim(0, 100)
plt.xlabel('Wavenumber (cm⁻¹)')
plt.ylabel('Transmittance (%)')
plt.title('Transmission Spectrum')
plt.legend()
plt.show()

# 7. Plot absorption spectrum
A = -np.log10(T)
plt.figure(figsize=(8, 4))
plt.plot(wn, A, color='red', label="Absorbance")
plt.xlim(4000, 500)
plt.ylim(-0.01, 0.6)
plt.xlabel('Wavenumber (cm⁻¹)')
plt.ylabel('Absorbance')
plt.title('Absorption Spectrum')
plt.legend()
plt.show()

# ==========================================
#  Extension (Optional):
# - Normalize the spectra (divide by max value)
# - Zoom into a specific wavenumber range (e.g., plt.xlim(1800, 800))
# - Try with other sample files (e.g., AB)
# ==========================================