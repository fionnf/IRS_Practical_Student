# FT-IR Spectroscopy Practical — student code

> **This repository is the student half of the practical.** It contains the
> Python you will write and the data you can practise on. The lab manual (the
> PDF your assistant gives you) tells you what to measure; this repository is
> where you turn those measurements into numbers.
>
> Model answers are **not** here, and neither are the assistant's notes. If you
> are a teaching assistant, you want the private course repository instead.

You take **raw data from an FT-IR spectrometer** and turn it, step by step and
with code you write yourself, into an interpretable infrared spectrum. Then you
push further: identify functional groups, measure how the instrument's own
settings shape the spectrum, extract bond lengths and force constants, and
follow a reaction in real time.

This is a **practical, not a tutorial with the answers filled in.** Almost every
file is a skeleton: docstrings and hints tell you *what* each piece must do, and
`# TODO` / `raise NotImplementedError` mark where **you** write the physics.

---

## Quick start

Four commands. If you are in a hurry, this is the whole setup.

```bash
git clone https://github.com/fionnf/IRS_Practical.git
cd IRS_Practical
pip install -r requirements.txt
python generate_demo_data.py
```

Then, whenever you want to know where you stand:

```bash
python check.py
```

`check.py` verifies your Python and packages, confirms the practice data is
present, and shows how many self-tests each exercise passes. **Run it first, run
it when you are stuck, and run it before you hand in.** It is a diagnostic tool —
nothing it prints is graded.

```
3. Your progress
----------------------------------------------------------
  [6/6] irtools.py                       ######  Your FT-IR toolkit
  [0/5] exercise7_uncertainty.py         .....   Uncertainty toolkit
  ...
  Self-tests passed: 6/28
```

---

## Setting up properly

### 1. Install Python

You need **Python 3.9 or newer**. Check with `python --version` (on some systems
the command is `python3`).

If you do not have it: [python.org/downloads](https://www.python.org/downloads/).
On Windows, tick **"Add Python to PATH"** in the installer — skipping that box is
the single most common cause of `python: command not found` later.

### 2. Get an editor

Either works, both are free for students:

- [PyCharm](https://www.jetbrains.com/pycharm/download/) — Community Edition is
  enough. Clone directly with `File ▸ New Project ▸ Get from VCS`.
- [VS Code](https://code.visualstudio.com/) — install the Python extension.
  Clone with `Ctrl/Cmd+Shift+P ▸ Git: Clone`.

### 3. Get the files

If your course points you at the **ETH GitLab** copy, the practical lives in
`experiments/IRS` of
[`pc-praktikum-dchab/python-scripts`](https://gitlab.ethz.ch/pc-praktikum-dchab/python-scripts) —
clone that and work inside `experiments/IRS`.

Otherwise clone this repository directly. Either way you get the same files.

### 4. Install the packages

```bash
pip install -r requirements.txt
```

Just `numpy`, `scipy` and `matplotlib`.

> **If this succeeds but `python check.py` still says a package is missing,**
> your editor is running a different Python than your terminal. This is *the*
> classic setup problem and it is not your fault. `check.py` prints the exact
> interpreter path it used — point your editor at that one. PyCharm:
> `Settings ▸ Project ▸ Python Interpreter`. VS Code: the interpreter picker in
> the status bar.

### 5. Get data

```bash
python generate_demo_data.py
```

This writes practice data for **every** exercise, so you can work through the
whole practical before your lab slot. When you have your own measurements, drop
the real `.dpt` files into the folder and use those — the practice data is for
learning the analysis, not for your report.

---

## The data files

| File | What it is |
|---|---|
| `*_rifg.dpt` | **R**eference **I**nter**F**ero**G**ram (empty beam) — use column 2 |
| `*_sifg.dpt` | **S**ample **I**nter**F**ero**G**ram — use column 2 |
| `*_ab.dpt` | **AB**sorbance spectrum the instrument computed — both columns |
| `polymer_ref_*.dpt` | Reference library for identification (exercise 9) |
| `polymer_unknown_*.dpt` | Two unknowns. One is not what it first appears to be. |
| `hcl_gas_ab.dpt` | HCl gas-phase rovibrational spectrum (exercise 8) |
| `hcl_gas_highres_ab.dpt` | Same, sharp enough to resolve the Cl-35/Cl-37 doublet — for the advanced isotope question only |
| `kinetics_298K/`, `kinetics_308K/` | A spectrum per time point plus `times.csv` (exercise 11) |

A `.dpt` file is just comma-separated `wavenumber, value`.

> The synthetic "ethanol" is a caricature with a few characteristic bands. It is
> good for learning the analysis; do **not** quote its band positions as real
> ethanol values.

---

## How to work through it

Do the files **in order** — later ones import earlier ones.

### `irtools.py` — build your toolkit *(start here)*
The core FT-IR maths as seven small functions you implement yourself:
`load_dpt`, `find_zero_burst`, `window_around`, `single_beam`,
`wavenumber_axis`, `transmittance`, `absorbance`. Nothing downstream works until
these pass, so get all six self-tests green before moving on.

### 1. `exercise1_interferogram.py` — load and explore
Read the files, find the zero burst, plot the interferograms, and reason about
*where the chemical information hides* before transforming anything.

### 2. `exercise2_spectrum.py` — interferogram → spectrum
Assemble the full pipeline: single-beam spectra → transmittance → absorbance,
then **validate against the instrument's own `*_ab.dpt`**. On the practice data a
correct pipeline reproduces the known band absorbances to a couple of percent —
so a large disagreement means a real bug, not bad luck.

### 3. `exercise3_peaks.py` — read it like a chemist
Baseline-correct, detect peaks with `scipy.signal.find_peaks`, and **assign** them
to functional groups using the correlation table provided.

### 4. `exercise4_resolution.py` — the instrument's knobs
Numerical experiments on the three things that shape every FT-IR spectrum:
**window length** (resolution ≈ 1 / maximum optical path difference),
**apodization** (peak shape versus ringing) and **zero-filling** (interpolation
versus true resolving power).

### 5. `exercise5_simulation.py` — build a spectrometer
Run the physics **backwards**: turn a known spectrum into an interferogram, then
recover it. Six parts — forward model, round trip, why noise falls as √n,
Beer–Lambert calibration, deconvolving overlapping bands with `curve_fit`, and a
Monte Carlo uncertainty. Needs no instrument data.

### 6. `exercise6_mixture_unmixing.py` — quantify a real mixture
**Classical least-squares unmixing** on your xylene-isomer data: solve
`A_mixture ≈ x₁·A_pure1 + x₂·A_pure2` directly from the spectrum, no peak-picking,
and use the reconstruction residual to answer *quantitatively* whether the
mixture is ideal.

### 7. `exercise7_uncertainty.py` — error propagation and statistics
A toolkit you will use for the **rest** of the practical: small-sample confidence
intervals (Student's *t*, not a bare standard deviation), propagation through
products and powers, regression with standard errors, and a two-sample *t*-test.
Every number you quote in your report should come with an uncertainty from here.

### 8. `exercise8_rovibrational.py` — bond lengths from a gas spectrum
Assign P and R branch lines with a running index `m`, then fit
`ν(m) = ν₀ + 2Bₑm − 4Dₑm³` by multiple regression — including **centrifugal
distortion**, not just the rigid rotor — to get `ν₀`, `Bₑ`, `Dₑ` and a bond length
with a real error bar. On the practice data you should land within about 0.1 pm
of the literature 127.5 pm.

### 9. `exercise9_polymer_id.py` — how library matching really works
Implement the **hit quality index** that commercial identification software
computes internally (cosine similarity of baseline-removed, normalised spectra),
then learn why a confident top hit can still be an incomplete answer: one of the
two practice unknowns is a laminate, and only a **residual re-search** reveals its
second layer. Also covers ATR penetration depth and the PE crystallinity index.

### 10. `exercise10_normalmodes.py` — where frequencies come from
Build the Wilson **GF matrices** for a linear XY₂ molecule, diagonalise for
frequencies *and* eigenvectors, then invert the problem to extract both force
constants from your measured spectrum — resolving the ~7% discrepancy the manual
deliberately leaves hanging as a real stretch–stretch interaction constant rather
than experimental error.

### 11. `exercise11_kinetics.py` — following a reaction in real time
Load a whole time series, integrate a band with a **local baseline** at each time
point (area, not height — it survives a band that shifts or broadens), fit a
first-order rate law with a real uncertainty on *k*, and then **test** the rate
law rather than assuming it. Includes a trap worth understanding: log-linearising
re-weights your noisiest late-time points.

> `dft_example.R` is an optional R version of the core workflow, provided as-is.
> Teaching assistants support **Python** only.

---

## Which file goes with which part of the lab manual

| Manual section | Python file(s) | Practice data |
|---|---|---|
| 0 — Pre-lab tools & orientation | `irtools.py` | — |
| A — FT-IR measurement basics | `exercise1`…`exercise4`, `exercise7` | `background_*`, `ethanol_*` |
| B — The Case of Deniz O'Sullivan | `exercise3`, `exercise7` | your own |
| C — The Afterparty (polymers) | `exercise9_polymer_id.py` | `polymer_ref_*`, `polymer_unknown_*` |
| D — Excess spectra of ideal mixtures | `exercise6_mixture_unmixing.py` | your own |
| E — Rovibrational spectra of gases | `exercise8_rovibrational.py` | `hcl_gas_ab.dpt` |
| F — Raman and IR of CS₂ | `exercise10_normalmodes.py` | your own |
| G — The O–H band as a probe | `exercise3`, `exercise7` | your own |
| H — H/D exchange | `exercise3`, `exercise7` | your own |
| I — Time-resolved ATR-FTIR | `exercise11_kinetics.py` | `kinetics_298K/`, `kinetics_308K/` |
| J — Computational bonus | `exercise5_simulation.py` | none needed |

---

## Background

**IR spectroscopy** probes molecular vibrations: each bond or functional group
absorbs at characteristic wavenumbers, so an IR spectrum is a fingerprint of
structure.

**How an FT-IR works.** A **Michelson interferometer** splits the infrared beam,
reflects one half off a *moving* mirror, and recombines them. The changing
optical path difference makes each wavelength interfere constructively or
destructively, and the detector records the combined signal — the
**interferogram** — which encodes every IR wavelength at once. A **Fourier
transform** converts it from path difference into wavenumber.

**The zero burst.** At zero optical path difference every wavelength interferes
constructively, giving the interferogram's maximum. Most spectral information
lives in a narrow window around it: cut a window there, Fourier-transform it, and
keep the positive-wavenumber half.

**Reference versus sample.** You measure a **background** (empty beam, `RIFG`) and
a **sample** (`SIFG`). Each transforms into a *single-beam* spectrum dominated by
source and detector response. Dividing sample by reference cancels that
instrument response, leaving **transmittance** `T`, and hence **absorbance**
`A = −log₁₀(T)` — the quantity linear in concentration (Beer–Lambert).

---

## What to hand in

Answer the **Q**uestions embedded in each file and in the lab manual, and include
the key figures. A good report:

- overlays your ethanol absorbance spectrum on the instrument's and discusses the
  agreement (2);
- gives a peak-assignment table with functional groups (3);
- shows the resolution / apodization / zero-filling comparisons and explains the
  trade-offs in your own words (4);
- shows the √n signal-averaging plot and calibration curve, states your measured
  unknown concentration, shows the two-band deconvolution with parameter
  uncertainties, and reports a proper confidence interval from the Monte Carlo
  run (5);
- shows the parity plot and residual spectrum for the mixture unmixing, and gives
  a verdict *with numbers* on whether the xylene mixture is ideal (6);
- reports **every** physical constant anywhere in your write-up — force
  constants, concentrations, mole fractions, bond lengths — as a value with a
  propagated uncertainty (7);
- shows the P/R branch assignment, the 2- versus 3-parameter regression
  comparison, and the HCl-versus-DCl bond length consistency check (8);
- gives the **full ranked hit list** for each polymer unknown, not just the
  winner, plus the residual re-search that reveals the laminate, and says what
  that means for trusting a single top-hit percentage (9);
- reports both CS₂ force constants from the GF-matrix inversion and states
  whether `k_rr` accounts for the discrepancy the manual leaves open (10);
- shows the time series with the isosbestic point marked, the first-order fit
  with `k ± σ_k` and a half-life, the residual plot and the `order_test`
  comparison, plus an honest note on how much `k` moves when the noise-dominated
  late points are dropped (11).

---

## Troubleshooting

**Start with `python check.py`.** It diagnoses most of what goes wrong below.

| Symptom | Cause and fix |
|---|---|
| `ModuleNotFoundError` | Packages not installed, or your editor uses a different interpreter than your terminal. Compare against the path `check.py` prints. |
| `FileNotFoundError` for a `.dpt` | Run `python generate_demo_data.py`, or put your real files in the project folder. |
| `NotImplementedError` | Expected — that function is still yours to write. |
| Spectrum looks like noise | Check you windowed around the zero burst of the *reference* and used the **same** centre for sample and reference. |
| Spectrum shifted along x | Your wavenumber axis should have exactly `N//2` points. |
| Peaks at the wrong wavenumbers | You are probably plotting against array index rather than the wavenumber axis. |
| Exercise 8 gives a nonsense bond length (~2× too long) | You used `hcl_gas_highres_ab.dpt`. Its resolved Cl-35/Cl-37 doublet interleaves two line progressions; use `hcl_gas_ab.dpt` unless you are doing the advanced isotope question. |
| Kinetics fit returns `NaN` | Some band areas have gone negative in the noise. Drop the late points that have decayed into the noise floor, and say that you did. |

Remember the IR convention: plot wavenumber **decreasing** left to right
(`plt.xlim(4000, 500)`).
