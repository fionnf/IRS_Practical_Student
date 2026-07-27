#!/usr/bin/env bash
#
# publish_to_gitlab.sh -- sync this practical into the ETH GitLab course repo.
#
# The student-facing copy lives in a SUBDIRECTORY of a shared repository:
#
#     https://gitlab.ethz.ch/pc-praktikum-dchab/python-scripts
#         experiments/IRS/     <-- this practical
#         experiments/.../     <-- other experiments, owned by other people
#
# So this is NOT a `git push` to a second remote. Pushing this repository's
# history onto that one would replace every other experiment in it. Instead we
# copy the current working files into experiments/IRS and commit only that
# path, leaving the rest of the course repo untouched.
#
# Usage:
#     tools/publish_to_gitlab.sh                # sync + show diff, no push
#     tools/publish_to_gitlab.sh --push         # sync, commit and push
#     COURSE_REPO=~/src/python-scripts tools/publish_to_gitlab.sh
#
# Requires: a working clone of the course repo and push rights on it. Run this
# from a machine that can reach gitlab.ethz.ch.

set -euo pipefail

GITLAB_URL="https://gitlab.ethz.ch/pc-praktikum-dchab/python-scripts.git"
SUBDIR="experiments/IRS"
COURSE_REPO="${COURSE_REPO:-$(mktemp -d)/python-scripts}"
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PUSH=0
[ "${1:-}" = "--push" ] && PUSH=1

# We publish the COMMITTED state (git archive HEAD), not the working tree, so
# a half-finished edit can never reach students. That also excludes generated
# data and caches for free, since those are gitignored and therefore untracked.
# These paths are tracked but still should not ship: IDE config, and this
# script itself (TA tooling, not student material).
EXCLUDE_PATHS=(.idea tools)

if [ ! -d "$COURSE_REPO/.git" ]; then
  echo ">> cloning course repo into $COURSE_REPO"
  git clone "$GITLAB_URL" "$COURSE_REPO"
else
  echo ">> updating existing clone at $COURSE_REPO"
  git -C "$COURSE_REPO" checkout main
  if git -C "$COURSE_REPO" remote get-url origin >/dev/null 2>&1; then
    if ! git -C "$COURSE_REPO" pull --ff-only origin main; then
      echo "!! could not fast-forward $COURSE_REPO from origin/main." >&2
      echo "   Either gitlab.ethz.ch is unreachable from here, or your local" >&2
      echo "   main has diverged. Fix that first -- publishing from a stale" >&2
      echo "   clone risks reverting someone else's experiment." >&2
      exit 1
    fi
  else
    echo "!! $COURSE_REPO has no 'origin' remote; cannot verify it is current." >&2
    echo "   Point COURSE_REPO at a real clone of $GITLAB_URL." >&2
    [ "$PUSH" -eq 1 ] && exit 1
    echo "   Continuing anyway because this is a dry run." >&2
  fi
fi

# Refuse to run against a dirty course repo -- we must not sweep up someone
# else's half-finished work into our commit.
if [ -n "$(git -C "$COURSE_REPO" status --porcelain)" ]; then
  echo "!! $COURSE_REPO has uncommitted changes. Resolve them first." >&2
  exit 1
fi

if [ -n "$(git -C "$SRC" status --porcelain)" ]; then
  echo "!! $SRC has uncommitted changes. Commit them first -- this script" >&2
  echo "   publishes the committed state, so anything uncommitted would be" >&2
  echo "   silently left behind." >&2
  exit 1
fi

STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT
echo ">> exporting $(git -C "$SRC" rev-parse --short HEAD) -> $COURSE_REPO/$SUBDIR"
git -C "$SRC" archive HEAD | tar -x -C "$STAGE"
for p in "${EXCLUDE_PATHS[@]}"; do rm -rf "${STAGE:?}/$p"; done

# Belt and braces. Model answers live in the separate PRIVATE course repo and
# have no route into this one, but this publishes to a student-facing location,
# so check anyway rather than trust that. Refuse outright on anything that looks
# like solutions, and on any exercise file with its NotImplementedError markers
# already filled in.
LEAKS=$(cd "$STAGE" && find . \( -iname '*solution*' -o -iname '*worked*' \
        -o -iname '*answer*' -o -iname '*musterloesung*' \) -print | sed 's|^\./||')
if [ -n "$LEAKS" ]; then
  echo "!! refusing to publish -- these look like answer material:" >&2
  echo "$LEAKS" | sed 's/^/     /' >&2
  exit 1
fi
for f in "$STAGE"/exercise*.py "$STAGE"/irtools.py; do
  [ -f "$f" ] || continue
  if ! grep -q "NotImplementedError" "$f"; then
    echo "!! refusing to publish -- $(basename "$f") has no NotImplementedError" >&2
    echo "   left in it. That is what a completed solution looks like; students" >&2
    echo "   are supposed to receive skeletons." >&2
    exit 1
  fi
done

# The course repo's experiments/IRS also holds material this script does NOT
# own -- notably Rohdaten/, the real measured spectra from previous years, and
# any scripts the course kept alongside them. We must never delete those.
#
# So we track exactly what WE published, in a manifest committed next to the
# files. On each run we copy our files in, then remove only those listed in the
# previous manifest that we no longer publish. Anything absent from the
# manifest was not put there by this script and is left strictly alone -- and
# on a first run, with no manifest present, nothing is deleted at all.
MANIFEST="$SUBDIR/.published-by-irs-practical"
mkdir -p "$COURSE_REPO/$SUBDIR"

NEW_LIST="$STAGE/.manifest.tmp"
(cd "$STAGE" && find . -type f ! -name '.manifest.tmp' | sed 's|^\./||' | LC_ALL=C sort) > "$NEW_LIST"

# Snapshot the PREVIOUS manifest before overwriting it. The safety net below
# must ask "did we publish this file last time?", and the new manifest can no
# longer answer that for a file we have just stopped publishing.
OLD_LIST="$STAGE/.manifest.old"
: > "$OLD_LIST"

PRESERVED=0
if [ -f "$COURSE_REPO/$MANIFEST" ]; then
  cp "$COURSE_REPO/$MANIFEST" "$OLD_LIST"
  while IFS= read -r rel; do
    [ -z "$rel" ] && continue
    if ! grep -qxF -- "$rel" "$NEW_LIST"; then
      rm -f "$COURSE_REPO/$SUBDIR/$rel"
    fi
  done < "$OLD_LIST"
else
  PRESERVED=$(find "$COURSE_REPO/$SUBDIR" -type f 2>/dev/null | wc -l | tr -d ' ')
  if [ "$PRESERVED" -gt 0 ]; then
    echo ">> first run: $PRESERVED existing file(s) already in $SUBDIR will be"
    echo "   left untouched (Rohdaten/, previous scripts, ...). This script only"
    echo "   ever removes files it published itself."
  fi
fi

tar -c -C "$STAGE" --exclude='.manifest.tmp' . | tar -x -C "$COURSE_REPO/$SUBDIR"
cp "$NEW_LIST" "$COURSE_REPO/$MANIFEST"

cd "$COURSE_REPO"
if [ -z "$(git status --porcelain -- "$SUBDIR")" ]; then
  echo ">> no changes; course repo is already up to date."
  exit 0
fi

git add -- "$SUBDIR"

# Safety net 1: nothing outside the subdirectory may be staged.
OUTSIDE=$(git diff --cached --name-only | grep -v "^$SUBDIR/" || true)
if [ -n "$OUTSIDE" ]; then
  echo "!! refusing to continue -- staged files outside $SUBDIR:" >&2
  echo "$OUTSIDE" >&2
  git reset -q
  exit 1
fi

# Safety net 2: never delete anything we did not publish ourselves.
BAD_DEL=$(git diff --cached --name-only --diff-filter=D \
          | sed "s|^$SUBDIR/||" \
          | { grep -vxF -f "$OLD_LIST" || true; } \
          | grep -v '^\.published-by-irs-practical$' || true)
if [ -n "$BAD_DEL" ]; then
  echo "!! refusing to continue -- this would delete files the script does not own:" >&2
  echo "$BAD_DEL" | sed 's/^/     /' >&2
  git reset -q
  exit 1
fi

echo
echo "===== files this will change (scoped to $SUBDIR) ====="
git status --short -- "$SUBDIR"
echo "======================================================"
echo "  additions/updates: $(git diff --cached --name-only --diff-filter=AM | wc -l | tr -d ' ')"
echo "  removals:          $(git diff --cached --name-only --diff-filter=D | wc -l | tr -d ' ')"

if [ "$PUSH" -ne 1 ]; then
  # Leave the index exactly as we found it, or the next run trips the
  # "uncommitted changes" guard and you can never get past the dry run.
  git reset -q
  git checkout -q -- "$SUBDIR" 2>/dev/null || true
  git clean -qfd -- "$SUBDIR" 2>/dev/null || true
  echo
  echo ">> dry run complete. Nothing committed, working tree restored."
  echo "   Review the list above, then re-run with --push to commit and push."
  exit 0
fi

git commit -m "IRS practical: sync experiments/IRS from upstream

Synced from the standalone IRS_Practical repository. Student-facing
skeletons, demo-data generator and README only; worked solutions and
generated data are deliberately not included."
git push origin main
echo ">> pushed to $GITLAB_URL ($SUBDIR)"
