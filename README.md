# FT-IR Spectroscopy: A Data-Analysis Practical

In this practical you will take **raw data from an FT-IR spectrometer** and turn
it, step by step and mostly with code you write yourself, into an interpretable
infrared spectrum. You will then push further: identify functional groups,
study how the instrument settings shape the spectrum, and finally *simulate a
spectrometer from scratch* to understand noise, signal averaging and
quantitative analysis.

This is a **practical, not a tutorial with the answers filled in.** Almost every
Python file is a skeleton: docstrings and hints tell you *what* each piece must
do, and `# TODO` / `raise NotImplementedError` mark where **you** write the
physics. If you just want to watch code run, this is not that. If you want to
actually understand FT-IR, read on.

---

## 🧑‍🔬 Background

**IR spectroscopy** probes molecular vibrations: each bond/functional group
absorbs light at characteristic wavenumbers, so an IR spectrum is a fingerprint
of chemical structure.

### How does an FT-IR spectrometer work?
An FT-IR spectrometer uses a **Michelson interferometer**. Infrared light is
split, one beam reflects off a *moving* mirror, and the two beams recombine.
The changing optical path difference makes each wavelength interfere
constructively or destructively. The detector records the combined signal — the
**interferogram** — which encodes *all* IR wavelengths at once. A **Fourier
transform** converts the interferogram from the path-difference domain into the
wavenumber (spectrum) domain.

### The "zero burst" (centre burst)
The **zero burst** is the point of maximum signal in the interferogram, at zero
optical path difference, where every wavelength interferes constructively. Most
of the spectral information lives in a narrow window around it. We cut a window
around the burst, Fourier-transform it, and keep the positive-wavenumber half
(the physically meaningful part) to get a clean spectrum.

### Reference vs sample: how chemistry appears
You measure two interferograms: a **reference/background** (empty beam, `RIFG`)
and a **sample** (`SIFG`). Each transforms into a *single-beam* spectrum that is
dominated by the source and detector response. Dividing sample by reference
removes that instrument response and leaves the **transmittance** `T`, from which
the **absorbance** `A = -log₁₀(T)` follows — the quantity that is linear in
concentration (Beer–Lambert law).

---

## What you need

- Python 3 ([python.org](https://www.python.org/downloads/))
- An IDE: [PyCharm](https://www.jetbrains.com/pycharm/download/) or
  [VS Code](https://code.visualstudio.com/)
- Git ([git-scm.com](https://git-scm.com/downloads))
- The `.dpt` data files — either the real instrument files (provided in the lab)
  **or** synthetic practice files you generate yourself (see below).

## Getting started

1. **Clone** the repository (PyCharm: `File ▸ New Project ▸ Get from VCS`; VS
   Code: `Ctrl/Cmd+Shift+P ▸ Git: Clone`) using
   `https://github.com/fionnf/IRS_Practical.git`.
2. **Install dependencies** in the IDE terminal:
   ```bash
   pip install -r requirements.txt
   ```
3. **Get data.** If you have the real `.dpt` files, drop them in the project
   folder. Otherwise generate realistic practice data:
   ```bash
   python generate_demo_data.py
   ```
   This writes `background_*.dpt` and `ethanol_*.dpt`. (The synthetic "ethanol"
   is a caricature — good for learning the analysis, not for quoting real band
   values.)

---

## The data files

| File | Meaning |
|------|---------|
| `*_rifg.dpt` | **R**eference **I**nter**F**ero**G**ram (empty beam) — use column 2 |
| `*_sifg.dpt` | **S**ample **I**nter**F**ero**G**ram — use column 2 |
| `*_ab.dpt`   | **AB**sorbance spectrum the instrument computed (wavenumber, A) — both columns |

---

## How to work through it

Do the files **in order**. Each builds on the previous one.

### 0. `irtools.py` — build your toolkit *(do this first)*
The core FT-IR maths, implemented by you as a handful of small functions
(`load_dpt`, `find_zero_burst`, `window_around`, `single_beam`,
`wavenumber_axis`, `transmittance`, `absorbance`). Run it to grade yourself:
```bash
python irtools.py
```
Keep going until all self-tests pass — later exercises import these functions.

### 1. `exercise1_interferogram.py` — load & explore
Read the six files, find the zero burst, plot the interferograms, and reason
about *where the chemical information hides* before you transform anything.

### 2. `exercise2_spectrum.py` — interferogram → spectrum
Assemble the full pipeline: single-beam spectra → transmittance → absorbance,
and **validate against the instrument's own `*_ab.dpt` file**.

### 3. `exercise3_peaks.py` — read it like a chemist
Baseline-correct the spectrum, detect peaks automatically
(`scipy.signal.find_peaks`), and **assign** them to functional groups using the
correlation table provided. Optionally compare two substances.

### 4. `exercise4_resolution.py` — the instrument's knobs
Numerical experiments on the three things that shape every FT-IR spectrum:
**window length** (resolution ≈ 1 / max path difference), **apodization**
(peak shape vs ringing), and **zero-filling** (interpolation vs true
resolution).

### 5. `exercise5_simulation.py` — build a spectrometer *(experimental)*
Run the physics **backwards**: turn a known spectrum into an interferogram, then
recover it. Use your simulator to see **why co-adding scans improves signal-to-
noise as √n**, and build a **Beer–Lambert calibration curve** to measure an
"unknown" concentration. Needs **no** instrument data — you generate everything.

> `dft_example.R` is an optional R version of the core workflow. It is provided
> as-is; teaching assistants support **Python** only.

---

## What to hand in (report)

For each exercise, answer the **Q**uestions embedded in the file and include the
key figures. A good report:

- shows your ethanol absorbance spectrum overlaid on the instrument's, and
  discusses the agreement (Exercise 2);
- gives a peak-assignment table with functional groups (Exercise 3);
- shows the resolution / apodization / zero-filling comparisons and explains the
  trade-offs in your own words (Exercise 4);
- shows the √n signal-averaging plot and the calibration curve, and states your
  measured "unknown" concentration with a comment on its reliability
  (Exercise 5).

## Tips & troubleshooting

- **Run `python irtools.py` early and often.** Nothing downstream works until
  the toolkit passes.
- **`ModuleNotFoundError`** → you didn't `pip install -r requirements.txt`, or
  you're using a different interpreter than your IDE's terminal.
- **`FileNotFoundError` for a `.dpt`** → run `python generate_demo_data.py`, or
  put the real files in the project folder.
- **Weird spectrum / peaks everywhere** → check you windowed around the zero
  burst of the *reference* and used the *same* centre for sample and reference;
  check your wavenumber axis has exactly `N//2` points.
- Remember the IR convention: plot wavenumber **decreasing** left→right
  (`plt.xlim(4000, 500)`).
