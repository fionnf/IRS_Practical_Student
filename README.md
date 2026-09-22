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
settings shape the spectrum, and extract bond lengths and force constants.

This is a **practical, not a tutorial with the answers filled in.** Almost every
file is a skeleton: docstrings and hints tell you *what* each piece must do, and
`# TODO` / `raise NotImplementedError` mark where **you** write the physics.

---

## Quick start

Four commands, and the last one sets itself up. If you are in a hurry, this is everything.

```bash
git clone https://github.com/fionnf/IRS_Practical.git
cd IRS_Practical
pip install -r requirements.txt
python check.py
```

That is the whole setup. `check.py` verifies your Python and packages,
**generates the practice data for you if it is missing**, and shows how many
self-tests each exercise passes. You do not need to run
`generate_demo_data.py` yourself.

**Run `check.py` first, run it when you are stuck, and run it before you hand
in.** It is a diagnostic tool — nothing it prints is graded.

Every exercise then works the same way:

```bash
python section_A_basics.py        # grade yourself against its self-tests
python section_A_basics.py run    # run the analysis on your data
```

> **The interactive bench page** — four in-browser instruments (interferometer
> console, rovibrational simulator, normal-mode explorer, and a symmetry explorer
> covering 34 molecules across 15 point groups) — lives at
> **<https://irs-practical.vercel.app/>**. No account or install needed;
> Section 0 of the manual walks you through it.

```
3. Your progress
----------------------------------------------------------
  [6/6] section_A_basics.py                       ######  Your FT-IR toolkit
  [0/5] uncertainty.py         .....   Uncertainty toolkit
  ...
  Self-tests passed: 0/15
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

Nothing to do. `python check.py` writes practice data for **every** exercise
the first time it finds it missing, so you can work through the whole practical
before your lab slot. (`python generate_demo_data.py` regenerates it, if you
ever want that.)

When you have your own measurements, drop the real `.dpt` files into the folder
and use those — the practice data is for learning the analysis, not for your
report.

---

## The data files

| File | What it is |
|---|---|
| `*_rifg.dpt` | **R**eference **I**nter**F**ero**G**ram (empty beam) — use column 2 |
| `*_sifg.dpt` | **S**ample **I**nter**F**ero**G**ram — use column 2 |
| `*_ab.dpt` | **AB**sorbance spectrum the instrument computed — both columns |
| `polymer_ref_*.dpt` | Reference library for identification (exercise 9) |
| `polymer_unknown_*.dpt` | Two unknowns. One is not what it first appears to be. |
| `kinetics_298K/` | A whole time-resolved run: one spectrum per time point, plus `times.csv` (exercise 11) |
| `kinetics_308K/` | The same reaction run warmer — for the activation energy |

A `.dpt` file is just comma-separated `wavenumber, value`.

> The synthetic "ethanol" is a caricature with a few characteristic bands. It is
> good for learning the analysis; do **not** quote its band positions as real
> ethanol values.

---

## How to work through it

**One script per experiment.** Each is self-contained: open it, run it, and it
does that section from beginning to end. There is no toolkit to build first and
no order you have to follow — start with whichever section you measured first.

| File | Answers | You write |
|---|---|---|
| `section_A_basics.py` | Section A Q1–Q8 (and 0 Q3) | 4 functions |
| `section_C_polymers.py` | Section C Q1–Q6 | 2 functions |
| `section_D_mixtures.py` | Section D Q1–Q7 | 1 function |
| `section_E_kinetics.py` | Section E Q1–Q5 | 3 functions |
| `section_F_normalmodes.py` | Section F Q1–Q4 | 2 functions |
| `uncertainty.py` | used by all of them | nothing, it is given |

**Twelve short functions in total.** Each is marked with a `# TODO`, says how
many lines it wants, and comes with a worked example. Everything else —
including the whole Fourier-transform pipeline and all of `uncertainty.py` — is
written for you and marked **WRITTEN FOR YOU**. Read it; don't rewrite it.

Every script works the same way:

```bash
python section_A_basics.py        # grade yourself against its self-tests
python section_A_basics.py run    # run the analysis on your data
```

## Which file goes with which part of the lab manual

| Manual section | Python file(s) | Practice data |
|---|---|---|
| 0 — Pre-lab tools & orientation | `section_A_basics.py` | — |
| A — FT-IR measurement basics | `section_A_basics.py` | `background_*`, `ethanol_*` |
| B — The Case of Deniz O'Sullivan | `section_A_basics.py`, `uncertainty.py` | your own |
| C — The Afterparty (polymers) | `section_C_polymers.py` | `polymer_ref_*`, `polymer_unknown_*` |
| D — Excess spectra of ideal mixtures | `section_D_mixtures.py` | your own |
| E — Hydrolysis of acetic anhydride | `section_E_kinetics.py` | `kinetics_298K/`, `kinetics_308K/` |
| F — Raman and IR of CS₂ | `section_F_normalmodes.py` | your own |
| G — The O–H band as a probe | `section_A_basics.py`, `uncertainty.py` | your own |
| H — H/D exchange | `section_A_basics.py`, `uncertainty.py` | your own |

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
- gives the **full ranked hit list** for each polymer unknown, not just the
  winner, plus the residual re-search that reveals the laminate, and says what
  that means for trusting a single top-hit percentage (9);
- reports both CS₂ force constants from the GF-matrix inversion and states
  whether `k_rr` accounts for the discrepancy the manual leaves open (10);
- shows the time series with the isosbestic point marked, the first-order fit
  with `k ± σ_k` and a half-life, the residual plot, plus an honest note on
  how much `k` moves when the noise-dominated late points are dropped (11).

---

## Troubleshooting

**Start with `python check.py`.** It diagnoses most of what goes wrong below.

| Symptom | Cause and fix |
|---|---|
| `ModuleNotFoundError` | Packages not installed, or your editor uses a different interpreter than your terminal. Compare against the path `check.py` prints. |
| `FileNotFoundError` for a `.dpt` | Run `python check.py`, which regenerates the practice data, or put your real files in the project folder. |
| `NotImplementedError` | Expected — that function is still yours to write. |
| Spectrum looks like noise | Check you windowed around the zero burst of the *reference* and used the **same** centre for sample and reference. |
| Spectrum shifted along x | Your wavenumber axis should have exactly `N//2` points. |
| Peaks at the wrong wavenumbers | You are probably plotting against array index rather than the wavenumber axis. |
| Exercise 11 finds an "isosbestic point" out in the flat baseline | You searched the whole spectrum. Every spectrum agrees where nothing is happening; restrict the search to between the falling band and the rising one. |

Remember the IR convention: plot wavenumber **decreasing** left to right
(`plt.xlim(4000, 500)`).
