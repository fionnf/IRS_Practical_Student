"""
team_setup.py  --  per-team task assignments for the IRS practical
====================================================================

Every team gets a different combination of samples, bands, analysis windows
and molecules, generated deterministically from the team number. Nothing is
random at run time: the same team number always produces the same sheet, on
any machine, so an assistant can regenerate a team's assignment months later
to mark their report against it.

USAGE
-----
    python team_setup.py 16                 # student sheet for team 16
    python team_setup.py 16 --key           # the same, plus the marking key
    python team_setup.py --all 1 24         # sheets for teams 1..24
    python team_setup.py 16 --latex         # LaTeX block to paste in the manual
    python team_setup.py --check 1 40       # audit the spread of assignments

The team number also seeds that team's practice data:

    python generate_demo_data.py --team 16

so two teams do not even share the synthetic interferogram they rehearse on.

NOTE FOR ASSISTANTS
-------------------
* Assignments are drawn from pools defined below. Edit the pools to match
  what is actually on the shelf -- but if you edit them AFTER handing sheets
  out, bump ASSIGNMENT_VERSION so it is obvious that older sheets came from a
  different pool.
* The generator does not know your stock. Skim the sheets before the session
  and override anything unavailable; record the override.
* Difficulty is meant to be equivalent across teams. If one option turns out
  to be much harder in practice, remove it from the pool rather than leaving
  some teams disadvantaged.
"""

import argparse
import hashlib
import random

# Bump this if you change any pool below. It is printed on every sheet so a
# sheet can always be traced back to the pool that produced it.
ASSIGNMENT_VERSION = "2025.1"


# --------------------------------------------------------------------------
# Pools. Options within a pool should be of comparable difficulty.
# --------------------------------------------------------------------------
LIQUIDS = ["ethanol", "propan-2-ol", "acetone", "ethyl acetate", "cyclohexane", "toluene"]
SOLIDS = ["paracetamol", "caffeine", "vanillin", "benzoic acid", "sucrose", "urea"]

# (label, nominal wavenumber, the atom pair to use for the reduced mass)
FORCE_BANDS = [
    ("C-H stretch", 2900, "C-H"),
    ("C=O stretch", 1700, "C=O"),
    ("O-H stretch", 3300, "O-H"),
    ("C-O stretch", 1050, "C-O"),
]

# Signal-free windows for the RMS noise-floor measurement (cm^-1).
NOISE_WINDOWS = [(1850, 2050), (2550, 2750), (3750, 3950), (1950, 2150)]

# Window-length triples for the exercise-4 resolution study.
N_TRIPLES = [
    (2 ** 9, 2 ** 11, 2 ** 13),
    (2 ** 10, 2 ** 12, 2 ** 14),
    (2 ** 11, 2 ** 13, 2 ** 15),
]

APODIZATION_PAIRS = [
    ("boxcar", "Blackman"), ("boxcar", "Hann"),
    ("triangular", "Blackman"), ("Hann", "Blackman"),
]

XYLENE_PAIRS = [("ortho", "meta"), ("ortho", "para"), ("meta", "para")]

FILM_LABELS = ["A", "B", "C", "D"]

# Bench-4 molecules a team must analyse. First list = must include one that
# actually appears in this practical; second = free choice for contrast.
PRACTICAL_MOLECULES = ["CS2", "CO2", "HCl", "CO", "H2O", "CH3Cl"]
CONTRAST_MOLECULES = ["SF6", "XeF4", "C6H6", "NH3", "BF3", "CH4", "C2H4",
                      "N2", "H2O2", "trans-C2H2Cl2", "BrF5", "SiF4", "C2H6", "O3"]

MIXTURE_FRACTIONS = [0.2, 0.4, 0.6, 0.8]


def _seed_for(team):
    """A well-spread, stable seed for a team number.

    Seeding Mersenne Twister directly with a small integer leaves the first
    few draws correlated between nearby seeds -- teams 7 and 16 came out with
    identical samples, band and isomer pair. Hashing first decorrelates them,
    and hashlib (unlike the built-in hash()) is stable across processes and
    Python versions, so a sheet regenerated next year is still the same sheet.
    """
    digest = hashlib.sha256(f"IRS-{ASSIGNMENT_VERSION}-team-{int(team)}".encode()).digest()
    return int.from_bytes(digest[:8], "big")


def assignment(team):
    """Deterministic assignment dictionary for a team number."""
    rng = random.Random(_seed_for(team))

    liquid = rng.choice(LIQUIDS)
    solid = rng.choice(SOLIDS)
    band = rng.choice(FORCE_BANDS)
    noise = rng.choice(NOISE_WINDOWS)
    n_triple = rng.choice(N_TRIPLES)
    apod = rng.choice(APODIZATION_PAIRS)
    xylene = rng.choice(XYLENE_PAIRS)

    films = FILM_LABELS[:]
    rng.shuffle(films)
    crystallinity_film = films[0]
    residual_film = films[1]

    mols = [rng.choice(PRACTICAL_MOLECULES)]
    pool = [m for m in CONTRAST_MOLECULES]
    rng.shuffle(pool)
    mols += pool[:2]

    return {
        "team": int(team),
        "version": ASSIGNMENT_VERSION,
        "liquid": liquid,
        "solid": solid,
        "band": band,
        "noise_window": noise,
        "n_triple": n_triple,
        "apodization_pair": apod,
        "xylene_pair": xylene,
        "crystallinity_film": crystallinity_film,
        "residual_film": residual_film,
        "molecules": mols,
        "mixture_fraction": rng.choice(MIXTURE_FRACTIONS),
        "j_max": rng.choice([6, 7, 8, 9]),
    }


def student_sheet(a):
    b_label, b_wn, b_pair = a["band"]
    lo, hi = a["noise_window"]
    n1, n2, n3 = a["n_triple"]
    ap1, ap2 = a["apodization_pair"]
    x1, x2 = a["xylene_pair"]
    lines = [
        f"IRS PRACTICAL -- TASK ASSIGNMENT FOR TEAM {a['team']}",
        f"(assignment set {a['version']}; quote this on the first page of your report)",
        "",
        "Your team's assignment differs from every other team's. Use exactly these",
        "and state them in your report; if something is unavailable on the day, ask",
        "your assistant for a substitution and record what you were given instead.",
        "",
        "SECTION 0 -- practice data",
        f"  Generate your practice data with:  python generate_demo_data.py --team {a['team']}",
        "  (Your synthetic files differ from other teams', so your Section 0",
        "   answers will not match theirs.)",
        f"  Bench 4 molecules to analyse (Q6):  {', '.join(a['molecules'])}",
        "",
        "SECTION A -- FT-IR basics",
        f"  Liquid sample:                     {a['liquid']}",
        f"  Solid sample:                      {a['solid']}",
        f"  Band for the force constant (iv):  {b_label} (~{b_wn} cm^-1), reduced mass for {b_pair}",
        f"  Noise-floor window:                {lo}-{hi} cm^-1",
        f"  Window lengths to compare (ii):    N = {n1}, {n2}, {n3}",
        f"  Apodizations to rank in detail:    {ap1} vs {ap2}",
        "",
        "SECTION C -- polymer films",
        f"  Crystallinity index on film:       {a['crystallinity_film']}",
        f"  Residual/laminate test on film:    {a['residual_film']}",
        "",
        "SECTION D -- xylene mixtures",
        f"  Isomer pair:                       {x1}- and {x2}-xylene",
        f"  Detailed residual analysis at:     x1 = {a['mixture_fraction']}",
        "",
        "SECTION E -- HCl / DCl",
        f"  Fit lines out to at least:         J'' = {a['j_max']}",
        "",
    ]
    return "\n".join(lines)


def marking_key(a):
    lo, hi = a["noise_window"]
    b_label, b_wn, b_pair = a["band"]
    lines = [
        f"--- MARKING KEY, TEAM {a['team']} (assignment set {a['version']}) ---",
        "Regenerate at any time with:  python team_setup.py "
        f"{a['team']} --key",
        "",
        "Cross-checks:",
        f"  * Their practice data must match:  python generate_demo_data.py --team {a['team']}",
        "    Re-run it and compare the zero-burst index they quote in Section 0 Q3.",
        f"    A team quoting a different burst index used another team's seed (or the default).",
        f"  * Their noise floor must be measured in {lo}-{hi} cm^-1, and the SAME value",
        "    must reappear in the Section B detection limit and the Section D",
        "    significance test.",
        f"  * Force constant must use the {b_label} (~{b_wn} cm^-1) with mu for {b_pair}.",
        f"    A k computed from a different band is either a misread assignment or",
        "    a borrowed answer -- check which.",
        f"  * Section D parity plot must be for {a['xylene_pair'][0]}/{a['xylene_pair'][1]}-xylene.",
        f"  * Section C crystallinity on film {a['crystallinity_film']}, residual test on"
        f" {a['residual_film']}.",
        f"  * Bench 4 molecules: {', '.join(a['molecules'])}.",
        "",
        "Two reports sharing numbers that should differ under these assignments is",
        "the clearest signal available short of the viva.",
        "",
    ]
    return "\n".join(lines)


def latex_block(a):
    b_label, b_wn, b_pair = a["band"]
    lo, hi = a["noise_window"]
    n1, n2, n3 = a["n_triple"]
    ap1, ap2 = a["apodization_pair"]
    x1, x2 = a["xylene_pair"]
    esc = lambda s: str(s).replace("_", r"\_")
    return "\n".join([
        r"\begin{center}",
        r"\begin{tabular}{ll}",
        r"\hline",
        r"\multicolumn{2}{l}{\textbf{Task assignment --- Team " + str(a["team"]) +
        r"} \quad \small(set " + esc(a["version"]) + r")} \\",
        r"\hline",
        r"Practice data seed & \texttt{--team " + str(a["team"]) + r"} \\",
        r"Liquid sample & " + esc(a["liquid"]) + r" \\",
        r"Solid sample & " + esc(a["solid"]) + r" \\",
        r"Force-constant band & " + esc(b_label) + r" ($\sim$" + str(b_wn) +
        r"~cm$^{-1}$), $\mu$ for " + esc(b_pair) + r" \\",
        r"Noise-floor window & " + f"{lo}--{hi}" + r"~cm$^{-1}$ \\",
        r"Window lengths & $N = " + f"{n1}, {n2}, {n3}" + r"$ \\",
        r"Apodizations to rank & " + esc(ap1) + r" vs " + esc(ap2) + r" \\",
        r"Xylene isomer pair & " + esc(x1) + r"/" + esc(x2) + r" \\",
        r"Crystallinity film & " + esc(a["crystallinity_film"]) + r" \\",
        r"Residual-test film & " + esc(a["residual_film"]) + r" \\",
        r"Bench 4 molecules & " + esc(", ".join(a["molecules"])) + r" \\",
        r"Fit HCl lines to & $J'' = " + str(a["j_max"]) + r"$ \\",
        r"\hline",
        r"\end{tabular}",
        r"\end{center}",
    ])


def audit(lo, hi):
    """Report how evenly the pools are used across a range of teams."""
    from collections import Counter
    fields = ["liquid", "solid", "crystallinity_film"]
    counters = {f: Counter() for f in fields}
    counters["band"] = Counter()
    counters["xylene_pair"] = Counter()
    combos = set()
    for t in range(lo, hi + 1):
        a = assignment(t)
        for f in fields:
            counters[f][a[f]] += 1
        counters["band"][a["band"][0]] += 1
        counters["xylene_pair"][a["xylene_pair"]] += 1
        combos.add((a["liquid"], a["solid"], a["band"][0], a["xylene_pair"],
                    a["crystallinity_film"]))
    n = hi - lo + 1
    print(f"Audit over teams {lo}-{hi} ({n} teams), assignment set {ASSIGNMENT_VERSION}\n")
    for f, c in counters.items():
        spread = ", ".join(f"{k}:{v}" for k, v in sorted(c.items(), key=lambda kv: str(kv[0])))
        print(f"  {f:20s} {spread}")
    print(f"\n  distinct assignment combinations: {len(combos)} / {n}")
    if len(combos) < n:
        print("  (some teams share a full combination -- fine for large cohorts,")
        print("   but check that those teams are not sitting next to each other)")


def main():
    ap = argparse.ArgumentParser(description="Per-team assignments for the IRS practical.")
    ap.add_argument("team", nargs="?", type=int, help="team number")
    ap.add_argument("--key", action="store_true", help="also print the marking key")
    ap.add_argument("--latex", action="store_true", help="print a LaTeX table instead")
    ap.add_argument("--all", nargs=2, type=int, metavar=("FIRST", "LAST"),
                    help="print sheets for a range of teams")
    ap.add_argument("--check", nargs=2, type=int, metavar=("FIRST", "LAST"),
                    help="audit pool usage over a range of teams")
    args = ap.parse_args()

    if args.check:
        audit(args.check[0], args.check[1]); return
    if args.all:
        for t in range(args.all[0], args.all[1] + 1):
            print(student_sheet(assignment(t)))
            if args.key:
                print(marking_key(assignment(t)))
            print("=" * 72)
        return
    if args.team is None:
        ap.error("give a team number, or use --all / --check")

    a = assignment(args.team)
    if args.latex:
        print(latex_block(a)); return
    print(student_sheet(a))
    if args.key:
        print(marking_key(a))


if __name__ == "__main__":
    main()
