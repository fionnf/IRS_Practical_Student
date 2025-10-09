# IR Spectroscopy Data Analysis

This project guides you through the process of analyzing infrared (IR) spectroscopy data using Python. You will learn how to load interferogram data, visualize signals, perform Fourier transforms, and interpret sample spectra.

---

## 🧑‍🔬 Background

**IR Spectroscopy** is a powerful technique for identifying molecular structures.  
The raw data from an IR spectrometer is an *interferogram*, a signal that must be transformed to reveal the spectrum.

## How Does an FT-IR Spectrometer Work?
An IR spectrometer uses a Michelson interferometer to split and recombine infrared light.
A moving mirror creates varying optical path differences, causing constructive and destructive interference for different wavelengths.
As the mirror moves, the detector records the resulting signal, called the interferogram, which contains information from all IR wavelengths at once.
To extract the spectrum, a Fourier Transform is applied to the interferogram, converting it from the time (or path difference) domain to the frequency (wavenumber) domain.

### What is the "Zero Burst"?

The **zero burst** is the point of maximum signal in the interferogram, corresponding to zero optical path difference in the interferometer.  
This region contains the most useful spectral information.  
By extracting a window around the zero burst before the Fourier Transform, you improve spectral resolution and reduce noise.  
After the FFT, only the positive half of the spectrum (wavenumbers) is physically meaningful for IR, so we plot just that half to obtain a clean, interpretable IR spectrum.

---

## What You Need

- A computer with macOS, Windows, or Linux
- [Python 3](https://www.python.org/downloads/) installed
- [PyCharm](https://www.jetbrains.com/pycharm/download/) or [VS Code](https://code.visualstudio.com/) installed
- Git installed (see [Git downloads](https://git-scm.com/downloads))
- The `.dpt` data files (provided with the project)

## How to Get Started

### 1. Clone the Project

#### Using PyCharm

1. Open PyCharm.
2. Go to `File` \> `New Project` \> `Get from VCS`.
3. Paste this URL: `https://github.com/fionnf/IRS_Practical.git`
4. Choose a folder and click `Clone`.

#### Using VS Code

1. Open VS Code.
2. Press `Cmd+Shift+P` (macOS) or `Ctrl+Shift+P` (Windows/Linux).
3. Type `Git: Clone` and select it.
4. Paste the URL: `https://github.com/fionnf/IRS_Practical.git`
5. Choose a folder and click `Open`.

### 2. Install Python

If you do not have Python, download and install it from [python.org](https://www.python.org/downloads/).

### 3. Install Project Dependencies

Open the terminal in your IDE (PyCharm or VS Code) and run:

```bash
pip install -r requirements.txt
```

This installs the required Python packages.


4. Run the Analysis
In the terminal, run:
```bash
python main.py
```

