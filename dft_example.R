# ==========================================
# IR Spectroscopy Data Analysis in R
# ==========================================
# Note: This worksheet is provided as-is. Teaching Assistants can only support Python.
# Use R at your own risk.

rm(list=ls())

k <- 16716.51 # Sampling rate

setwd("C:/Users/kerim/Desktop/IRS/A")

# Load data
b.RIFG <- read.table("background_rifg.dpt", sep=",")[,2]
b.SIFG <- read.table("background_sifg.dpt", sep=",")[,2]
b.AB <- read.table("background_ab.dpt", sep=",")
EtOH.RIFG <- read.table("ethanol_rifg.dpt", sep=",")[,2]
EtOH.SIFG <- read.table("ethanol_sifg.dpt", sep=",")[,2]
EtOH.AB <- read.table("ethanol_ab.dpt", sep=",")

# Plot interferograms
plot(b.RIFG, type="l", col='black')
lines(b.SIFG, type="l", col="black")
lines(EtOH.SIFG, type="l", col="red")
# Add legend

# Data selection
s.RIFG <- EtOH.RIFG
s.SIFG <- EtOH.SIFG
s.AB <- EtOH.AB

N <- 2^14
i.zb <- which.max(abs(s.RIFG))
RIFG <- s.RIFG[(i.zb-N/2):(i.zb+N/2-1)]
SIFG <- s.SIFG[(i.zb-N/2):(i.zb+N/2-1)]

plot(RIFG, type="l", col="black")
lines(SIFG, type="l", col="red")
# Add axis and legend

# FFT and spectra
# Calculate FFT for RIFG and SIFG
# Plot the spectra

# Transmission
# Calculate transmission spectrum

# Absorption
# Calculate absorption spectrum

# Compare calculated and measured absorption
# Plot both spectra for comparison