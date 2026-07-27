"""
check.py -- is my setup working, and how far through the practical am I?
========================================================================

Run this whenever you are stuck, and at the start of every session:

    python check.py

It answers three questions in order, and stops at the first one that fails,
because there is no point grading your exercises if numpy is not installed:

    1. Is Python set up correctly, with the packages this practical needs?
    2. Is the practice data present?
    3. Which exercises have you finished, and which still have work left?

Nothing here is graded and nothing here is part of your report -- it is a
diagnostic tool, so run it as often as you like.

This file deliberately imports NOTHING beyond the Python standard library at
the top level, so that it still runs (and can tell you what is wrong) on a
machine where numpy and scipy have not been installed yet.
"""

import os
import subprocess
import sys

# Exercises in the order you should work through them. The second entry says
# how the file reports progress: "selftest" files grade themselves, "report"
# files are judged from the figures and answers in your write-up instead.
EXERCISES = [
    ("irtools.py", "selftest", "Your FT-IR toolkit -- everything else imports it"),
    ("exercise1_interferogram.py", "report", "Load and explore the interferograms"),
    ("exercise2_spectrum.py", "report", "Interferogram to spectrum, validated"),
    ("exercise3_peaks.py", "report", "Baseline, peak finding, assignment"),
    ("exercise4_resolution.py", "report", "Resolution, apodization, zero-filling"),
    ("exercise5_simulation.py", "report", "Simulate a spectrometer end to end"),
    ("exercise6_mixture_unmixing.py", "report", "Least-squares mixture unmixing"),
    ("exercise7_uncertainty.py", "selftest", "Uncertainty toolkit -- used everywhere"),
    ("exercise8_rovibrational.py", "report", "HCl rovibrational constants"),
    ("exercise9_polymer_id.py", "selftest", "Library matching and ATR depth"),
    ("exercise10_normalmodes.py", "selftest", "GF-matrix normal modes"),
    ("exercise11_kinetics.py", "selftest", "Time-resolved kinetics"),
]

REQUIRED_PACKAGES = ["numpy", "scipy", "matplotlib"]

# A representative file per data group, with the reason you need it.
DATA_GROUPS = [
    ("background_rifg.dpt", "interferograms (exercises 1-4)"),
    ("ethanol_ab.dpt", "reference absorbance to validate against (exercise 2)"),
    ("hcl_gas_ab.dpt", "HCl gas-phase spectrum (exercise 8)"),
    ("polymer_ref_PE.dpt", "polymer library (exercise 9)"),
    ("kinetics_298K/times.csv", "kinetics time series (exercise 11)"),
]

GREEN, YELLOW, RED, DIM, BOLD, OFF = (
    ("\033[32m", "\033[33m", "\033[31m", "\033[2m", "\033[1m", "\033[0m")
    if sys.stdout.isatty() and os.name != "nt" else ("", "", "", "", "", "")
)
TICK, CROSS, DOT = "PASS", "FAIL", "--"


def rule(title):
    print(f"\n{BOLD}{title}{OFF}\n" + "-" * max(len(title), 58))


def check_python():
    rule("1. Python")
    major, minor = sys.version_info[:2]
    ok = (major, minor) >= (3, 9)
    mark = f"{GREEN}{TICK}{OFF}" if ok else f"{RED}{CROSS}{OFF}"
    print(f"  [{mark}] Python {major}.{minor} at {sys.executable}")
    if not ok:
        print(f"\n  {RED}Python 3.9 or newer is required.{OFF}")
        return False

    missing = []
    for pkg in REQUIRED_PACKAGES:
        try:
            mod = __import__(pkg)
            version = getattr(mod, "__version__", "?")
            print(f"  [{GREEN}{TICK}{OFF}] {pkg} {version}")
        except ImportError:
            missing.append(pkg)
            print(f"  [{RED}{CROSS}{OFF}] {pkg} is NOT installed")

    if missing:
        print(
            f"\n  {RED}Missing: {', '.join(missing)}{OFF}\n"
            f"  Fix it with:\n\n      {BOLD}{sys.executable} -m pip install -r "
            f"requirements.txt{OFF}\n\n"
            "  If that succeeds but this check still fails, your editor is\n"
            "  probably running a different Python than your terminal. In\n"
            "  PyCharm look at Settings > Project > Python Interpreter; in\n"
            "  VS Code use the interpreter picker in the status bar, and make\n"
            "  sure it matches the path printed above."
        )
        return False
    return True


def check_data():
    rule("2. Practice data")
    missing = [(f, why) for f, why in DATA_GROUPS if not os.path.exists(f)]
    for fname, why in DATA_GROUPS:
        mark = f"{GREEN}{TICK}{OFF}" if os.path.exists(fname) else f"{YELLOW}{DOT}{OFF}"
        print(f"  [{mark}] {fname:<28} {DIM}{why}{OFF}")

    if missing:
        print(
            f"\n  {YELLOW}Some practice data is missing.{OFF} Generate all of it with:\n"
            f"\n      {BOLD}python generate_demo_data.py{OFF}\n\n"
            "  You only need this until you have your own measurements --\n"
            "  once you do, drop your .dpt files in this folder and use those."
        )
    return not missing


def run_selftest(filename):
    """Run one exercise's self-test in a subprocess; return (passed, total)."""
    try:
        proc = subprocess.run(
            [sys.executable, filename],
            capture_output=True, text=True, timeout=300,
            env={**os.environ, "MPLBACKEND": "Agg"},
        )
    except subprocess.TimeoutExpired:
        return None
    for line in proc.stdout.splitlines():
        line = line.strip()
        if "checks passed" in line and "/" in line:
            try:
                got, rest = line.split("/", 1)
                return int(got), int(rest.split()[0])
            except (ValueError, IndexError):
                return None
    return None


def check_progress():
    rule("3. Your progress")
    done = total = 0
    for filename, kind, blurb in EXERCISES:
        if not os.path.exists(filename):
            print(f"  [{RED}{CROSS}{OFF}] {filename:<32} file is missing!")
            continue

        if kind == "report":
            print(f"  [{DIM} ~ {OFF}] {filename:<32} {DIM}{blurb}{OFF}")
            continue

        result = run_selftest(filename)
        if result is None:
            print(f"  [{RED}{CROSS}{OFF}] {filename:<32} could not run -- "
                  f"try {BOLD}python {filename}{OFF} to see the error")
            continue

        passed, n = result
        total += n
        done += passed
        bar = "#" * passed + "." * (n - passed)
        colour = GREEN if passed == n else (YELLOW if passed else RED)
        print(f"  [{colour}{passed}/{n}{OFF}] {filename:<32} {colour}{bar}{OFF}  {DIM}{blurb}{OFF}")

    print(f"\n  Self-tests passed: {BOLD}{done}/{total}{OFF}")
    print(f"  {DIM}Files marked ~ have no self-tests: they are judged from the\n"
          f"  figures and answers in your report, not by this script.{OFF}")
    return done, total


def main():
    print(f"{BOLD}FT-IR practical -- setup and progress check{OFF}")
    if not check_python():
        return 1
    check_data()
    done, total = check_progress()

    rule("What to do next")
    if total and done == total:
        print(f"  {GREEN}Every self-test passes.{OFF} Work through the main() section of\n"
              "  each exercise, answer the embedded questions, and write them up.")
    else:
        print("  Open the first file above that is not yet complete and implement\n"
              "  the functions marked with TODO. Re-run this check as you go.\n"
              "  Work in order: later exercises import the earlier ones.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
