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
# main is a PROTECTED branch there, so this commits onto a side branch and asks
# GitLab to open a merge request as part of the push.
#
# Usage:
#     tools/publish_to_gitlab.sh                     # dry run: show the diff only
#     tools/publish_to_gitlab.sh --push              # commit, push branch, open MR
#     tools/publish_to_gitlab.sh --branch my-name    # use a different branch
#     tools/publish_to_gitlab.sh --push --branch main  # direct push, if allowed
#
#     COURSE_REPO=~/src/python-scripts tools/publish_to_gitlab.sh --push
#
# COURSE_REPO points at your clone of the course repo; without it a fresh clone
# is made in a temporary directory. Run from a machine that can reach
# gitlab.ethz.ch, with push rights on the project.
#
# What it will and will not touch: everything it writes lives under
# experiments/IRS, and it removes only files listed in the manifest it wrote on
# a previous run. Rohdaten/ and anything else already in that directory are left
# alone, and the commit is refused outright if a deletion falls outside that set.

set -euo pipefail

GITLAB_URL="https://gitlab.ethz.ch/pc-praktikum-dchab/python-scripts.git"
SUBDIR="experiments/IRS"
COURSE_REPO="${COURSE_REPO:-$(mktemp -d)/python-scripts}"
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# main is a PROTECTED branch on the ETH GitLab project, so nobody can push to
# it directly -- changes go through a merge request. We therefore commit onto a
# side branch by default and ask GitLab to open the MR as part of the push.
# Pass --branch main if you are publishing somewhere without that protection.
PUSH=0
BRANCH="${BRANCH:-irs-practical-sync}"
while [ $# -gt 0 ]; do
  case "$1" in
    --push)   PUSH=1; shift ;;
    --branch) BRANCH="${2:?--branch needs a name}"; shift 2 ;;
    -h|--help)
      sed -n '2,23p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
      exit 0 ;;
    *) echo "unknown option: $1 (try --help)" >&2; exit 2 ;;
  esac
done

# We publish the COMMITTED state (git archive HEAD), not the working tree, so
# a half-finished edit can never reach students. That also excludes generated
# data and caches for free, since those are gitignored and therefore untracked.
# These paths are tracked but still should not ship: IDE config, and this
# script itself (TA tooling, not student material).
EXCLUDE_PATHS=(.idea tools vercel.json)

# Check the SOURCE first: no point cloning or switching branches in the
# course repo only to bail out because this repository is dirty.
if [ -n "$(git -C "$SRC" status --porcelain)" ]; then
  echo "!! $SRC has uncommitted changes. Commit them first -- this script" >&2
  echo "   publishes the committed state, so anything uncommitted would be" >&2
  echo "   silently left behind." >&2
  exit 1
fi

if [ ! -d "$COURSE_REPO/.git" ]; then
  echo ">> cloning course repo into $COURSE_REPO"
  git clone "$GITLAB_URL" "$COURSE_REPO"
else
  echo ">> updating existing clone at $COURSE_REPO"
  git -C "$COURSE_REPO" checkout main
  if git -C "$COURSE_REPO" remote get-url origin >/dev/null 2>&1; then
    if ! git -C "$COURSE_REPO" pull --ff-only origin main; then
      echo "!! could not fast-forward $COURSE_REPO from origin/main." >&2
      if [ -n "$(git -C "$COURSE_REPO" log origin/main..main --oneline 2>/dev/null)" ]; then
        echo "   Your local main carries commits that are not on origin/main:" >&2
        git -C "$COURSE_REPO" log origin/main..main --oneline 2>/dev/null | sed 's/^/     /' >&2
        echo "   main is protected on this project, so those can never be pushed." >&2
        echo "   Move them onto a branch, or discard them and let this script" >&2
        echo "   recreate the commit:" >&2
        echo "       git -C $COURSE_REPO reset --hard origin/main" >&2
      else
        echo "   gitlab.ethz.ch may be unreachable from here. Publishing from a" >&2
        echo "   stale clone risks reverting someone else's experiment." >&2
      fi
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

# Work on the side branch, rebuilt from the current main each time so it never
# carries stale content from a previous sync.
if [ "$BRANCH" != "main" ]; then
  BASE=origin/main
  git -C "$COURSE_REPO" rev-parse --verify -q "$BASE" >/dev/null || BASE=main
  git -C "$COURSE_REPO" checkout -q -B "$BRANCH" "$BASE"
  echo ">> working on branch '$BRANCH' (based on $BASE)"
fi


STAGE="$(mktemp -d)"
WORK="$(mktemp -d)"
trap 'rm -rf "$STAGE" "$WORK"' EXIT
echo ">> exporting $(git -C "$SRC" rev-parse --short HEAD) -> $COURSE_REPO/$SUBDIR"
git -C "$SRC" archive HEAD | tar -x -C "$STAGE"
for p in "${EXCLUDE_PATHS[@]}"; do rm -rf "${STAGE:?}/$p"; done

# Belt and braces. Model answers live in the separate PRIVATE course repo and
# have no route into this one, but this publishes to a student-facing location,
# so check anyway rather than trust that. Refuse outright on anything that looks
# like solutions, and on any exercise file with its NotImplementedError markers
# already filled in.
# Note the patterns are deliberately anchored: a bare '*solution*' also matches
# exercise4_reSOLUTION.py, which would block every legitimate publish.
LEAKS=$(cd "$STAGE" && find . \( \
          -iname 'solution' -o -iname 'solutions' \
          -o -iname 'solution_*' -o -iname 'solutions_*' \
          -o -iname '*_solution.*' -o -iname '*_solutions.*' \
          -o -iname 'worked' -o -iname 'worked_*' -o -iname '*_worked.*' \
          -o -iname 'answers' -o -iname 'answer_*' -o -iname '*_answers.*' \
          -o -iname 'musterloesung*' -o -iname '*.solution' \
        \) -print | sed 's|^\./||')
if [ -n "$LEAKS" ]; then
  echo "!! refusing to publish -- these look like answer material:" >&2
  echo "$LEAKS" | sed 's/^/     /' >&2
  exit 1
fi
# A content-based check was tried here and removed: neither "NotImplementedError"
# nor "TODO" separates a skeleton from a solution. Solutions keep
# NotImplementedError in their self-test `except` handlers, exercise 1 has none
# to begin with, and several solutions still carry main()'s TODO comments. Every
# variant either blocked legitimate publishes or missed real solutions, so the
# name/path check above is the guard, and the primary protection remains that
# model answers live in a separate private repository with no route into this one.

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

NEW_LIST="$WORK/manifest.new"
(cd "$STAGE" && find . -type f | sed 's|^\./||' | LC_ALL=C sort) > "$NEW_LIST"

# Snapshot the PREVIOUS manifest before overwriting it. The safety net below
# must ask "did we publish this file last time?", and the new manifest can no
# longer answer that for a file we have just stopped publishing.
OLD_LIST="$WORK/manifest.old"
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

tar -c -C "$STAGE" . | tar -x -C "$COURSE_REPO/$SUBDIR"
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
  [ "$BRANCH" != "main" ] && git checkout -q main 2>/dev/null || true
  echo
  echo ">> dry run complete. Nothing committed, working tree restored."
  echo "   Review the list above, then re-run with --push to commit and push."
  exit 0
fi

git commit -q -m "IRS practical: sync experiments/IRS from upstream

Synced from the standalone IRS_Practical repository. Student-facing
skeletons, demo-data generator and README only; worked solutions and
generated data are deliberately not included.

Files this sync owns are listed in experiments/IRS/.published-by-irs-practical.
Anything else under experiments/IRS -- Rohdaten/ in particular -- is left
untouched."

if [ "$BRANCH" = "main" ]; then
  git push origin main
  echo ">> pushed to $GITLAB_URL ($SUBDIR)"
  exit 0
fi

# GitLab can open the merge request as part of the push, so this needs no
# separate visit to the web UI. The options are ignored by non-GitLab remotes.
TITLE="IRS practical: sync experiments/IRS"
MR_URL="${GITLAB_URL%.git}/-/merge_requests/new?merge_request%5Bsource_branch%5D=$BRANCH"
echo ">> pushing '$BRANCH' and requesting a merge request into main"

# Try the push options first: GitLab opens the MR itself, so there is no second
# step. Older GitLab, or any non-GitLab remote, rejects unknown push options and
# would fail the whole push -- so fall back to a plain push and hand over the URL.
if git push --force-with-lease \
     -o merge_request.create \
     -o merge_request.target=main \
     -o merge_request.title="$TITLE" \
     -o merge_request.remove_source_branch \
     origin "$BRANCH" 2>&1 | tee "$WORK/push.log"; then
  echo ">> pushed; GitLab prints the merge-request URL just above."
elif grep -q "does not support push options" "$WORK/push.log"; then
  echo ">> remote does not support push options; pushing without them"
  if git push --force-with-lease origin "$BRANCH"; then
    echo ">> pushed. Open the merge request here:"
    echo "   $MR_URL"
  else
    echo "!! push failed -- see the error above." >&2
    exit 1
  fi
else
  echo "!! push failed -- see the error above." >&2
  echo "   If the branch already has an open merge request, re-push it plainly:" >&2
  echo "       git -C $COURSE_REPO push --force-with-lease origin $BRANCH" >&2
  exit 1
fi
echo
echo "   Merge request (if not created automatically):"
echo "   $MR_URL"
