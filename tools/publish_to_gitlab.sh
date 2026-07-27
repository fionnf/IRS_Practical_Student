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

# Replace the subdirectory wholesale so files deleted upstream also disappear
# here. Scoped to $SUBDIR, so nothing outside experiments/IRS is ever touched.
rm -rf "${COURSE_REPO:?}/$SUBDIR"
mkdir -p "$COURSE_REPO/$SUBDIR"
tar -c -C "$STAGE" . | tar -x -C "$COURSE_REPO/$SUBDIR"

cd "$COURSE_REPO"
if git diff --quiet -- "$SUBDIR" && [ -z "$(git status --porcelain -- "$SUBDIR")" ]; then
  echo ">> no changes; course repo is already up to date."
  exit 0
fi

git add -- "$SUBDIR"
echo
echo "===== files this will change (scoped to $SUBDIR) ====="
git status --short -- "$SUBDIR"
echo "======================================================"

# Safety net: prove nothing outside the subdirectory got staged.
OUTSIDE=$(git diff --cached --name-only | grep -v "^$SUBDIR/" || true)
if [ -n "$OUTSIDE" ]; then
  echo "!! refusing to continue -- staged files outside $SUBDIR:" >&2
  echo "$OUTSIDE" >&2
  exit 1
fi

if [ "$PUSH" -ne 1 ]; then
  echo
  echo ">> dry run complete. Nothing committed."
  echo "   Review the list above, then re-run with --push to commit and push."
  exit 0
fi

git commit -m "IRS practical: sync experiments/IRS from upstream

Synced from the standalone IRS_Practical repository. Student-facing
skeletons, demo-data generator and README only; worked solutions and
generated data are deliberately not included."
git push origin main
echo ">> pushed to $GITLAB_URL ($SUBDIR)"
