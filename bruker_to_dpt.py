#!/usr/bin/env python3
"""
bruker_to_dpt.py  --  bulk-convert Bruker OPUS files into .dpt files
====================================================================

The spectrometer saves each measurement as one binary Bruker OPUS file, usually
with a numeric extension (``ethanol.0``, ``ethanol.1``, ...). The exercises in
this practical all read plain ``.dpt`` data point tables instead. This script
converts a whole folder in one go, so you do not have to click through
OPUS -> "Save As" -> "Data Point Table" once per measurement:

    python bruker_to_dpt.py raw_opus dpt

reads every OPUS file in ``raw_opus/`` and writes one ``.dpt`` per data block
into ``dpt/``:

    raw_opus/ethanol.0  ->  dpt/ethanol_rifg.dpt   (reference interferogram)
                            dpt/ethanol_sifg.dpt   (sample interferogram)
                            dpt/ethanol_ab.dpt     (absorbance spectrum)

Only want some of the blocks?

    python bruker_to_dpt.py raw_opus dpt --blocks ab,sifg,rifg

Anything in the folder that is not an OPUS file is ignored, so you can point it
straight at the folder the instrument wrote.

This needs the ``brukeropus`` reader (pure python):  pip install brukeropus
It only unpacks the binary container -- all the spectroscopy is still yours to
write in irtools.py.
"""

import argparse
import os
import sys

import numpy as np

try:
    from brukeropus import read_opus
except ImportError:
    sys.exit("This script needs the OPUS reader:  pip install brukeropus")


# brukeropus data key -> the suffix OPUS itself uses when it exports .dpt files.
# Anything not listed here keeps the brukeropus key as its suffix.
SUFFIXES = {
    "igrf": "rifg",   # reference interferogram  (column 2 = signal)
    "igsm": "sifg",   # sample interferogram     (column 2 = signal)
    "a": "ab",        # absorbance spectrum
    "t": "tr",        # transmittance spectrum
    "sm": "ssc",      # sample single-channel spectrum
    "rf": "rsc",      # reference single-channel spectrum
    "phsm": "phsm",   # sample phase
}


def output_stem(filename):
    """``ethanol.0`` -> ``ethanol``, ``ethanol.1`` -> ``ethanol_1``.

    Keeping the number for repeat measurements stops the second scan of a
    sample from overwriting the first.
    """
    base, ext = os.path.splitext(filename)
    digits = ext[1:]
    if digits.isdigit():
        return base if int(digits) == 0 else "{}_{}".format(base, int(digits))
    return filename.replace(".", "_")


def save_dpt(path, x, y):
    """Write a two-column comma-separated data point table, x ascending."""
    order = np.argsort(x)
    np.savetxt(path, np.column_stack([x[order], y[order]]), delimiter=",", fmt="%.8g")


def convert_file(path, out_dir, wanted=None, overwrite=False):
    """Convert one OPUS file. Returns the list of .dpt files written.

    Returns ``None`` if ``path`` is not an OPUS file at all.
    """
    opus = read_opus(path)
    if not opus.is_opus:
        return None
    stem = output_stem(os.path.basename(path))
    written, skipped = [], 0
    for key in opus.data_keys:
        suffix = SUFFIXES.get(key, key)
        if wanted and suffix not in wanted and key not in wanted:
            continue
        data = getattr(opus, key)
        out_path = os.path.join(out_dir, "{}_{}.dpt".format(stem, suffix))
        if os.path.exists(out_path) and not overwrite:
            print("  skip   {}  (exists -- use --overwrite)".format(out_path))
            skipped += 1
            continue
        save_dpt(out_path, np.asarray(data.x, float), np.asarray(data.y, float))
        print("  wrote  {}  ({} points, {})".format(out_path, len(data.y), data.label))
        written.append(out_path)
    if not written and not skipped:
        print("  note   {}: no matching blocks (this file holds: {})"
              .format(path, ", ".join(opus.data_keys) or "no data blocks"))
    return written


def list_files(folder, recursive=False):
    if recursive:
        found = [os.path.join(root, name)
                 for root, _dirs, names in os.walk(folder) for name in names]
    else:
        found = [os.path.join(folder, name) for name in os.listdir(folder)]
    return sorted(p for p in found if os.path.isfile(p))


def main():
    parser = argparse.ArgumentParser(
        description="Bulk-convert Bruker OPUS files in a folder into .dpt data point tables.")
    parser.add_argument("in_folder", help="folder holding the Bruker OPUS files")
    parser.add_argument("out_folder", nargs="?", default="dpt",
                        help="folder to write the .dpt files into (default: dpt)")
    parser.add_argument("--blocks", default="",
                        help="comma-separated list of blocks to keep, e.g. ab,sifg,rifg "
                             "(default: every block in the file)")
    parser.add_argument("--recursive", action="store_true",
                        help="also convert OPUS files in sub-folders")
    parser.add_argument("--overwrite", action="store_true",
                        help="overwrite .dpt files that already exist")
    args = parser.parse_args()

    if not os.path.isdir(args.in_folder):
        sys.exit("No such folder: {}".format(args.in_folder))
    os.makedirs(args.out_folder, exist_ok=True)

    wanted = {b.strip().lower() for b in args.blocks.split(",") if b.strip()}
    n_opus, n_written = 0, 0

    print("Converting OPUS files in {} -> {}".format(args.in_folder, args.out_folder))
    for path in list_files(args.in_folder, recursive=args.recursive):
        written = convert_file(path, args.out_folder, wanted=wanted, overwrite=args.overwrite)
        if written is None:      # not an OPUS file, quietly ignore
            continue
        n_opus += 1
        n_written += len(written)

    print("\n{} OPUS file(s) read, {} .dpt file(s) written to {}/"
          .format(n_opus, n_written, args.out_folder.rstrip("/")))
    if n_opus == 0:
        print("Found no OPUS files. Are the raw instrument files really in that folder?")


if __name__ == "__main__":
    main()
