#!/usr/bin/env python3
"""
suggest_replies.py — generate AI-suggested email replies using the Claude Code
CLI (headless mode), so generation draws on the user's existing Claude plan
rather than a separate pay-per-token API key.

Input:  a JSON object on stdin, e.g.
        {"sender": "a@b.com", "subject": "Lunch?", "body": "Free Friday?"}

Output: a JSON object on stdout, e.g.
        {"replies": ["Sure, Friday works...", "..."]}

On error: a human-readable message on stderr and a non-zero exit code.

No third-party dependencies — stdlib only, so this can run with the system
Python3 that ships on macOS without any pip install.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_PATH = SCRIPT_DIR / "config.json"
EXAMPLE_CONFIG_PATH = SCRIPT_DIR / "config.example.json"

# do shell script (used by AppleScript) runs with a minimal PATH that often
# doesn't include where the claude CLI actually lives, so we search common
# install locations explicitly.
COMMON_CLAUDE_LOCATIONS = [
    Path.home() / ".local" / "bin" / "claude",
    Path.home() / ".claude" / "local" / "claude",
    Path("/opt/homebrew/bin/claude"),
    Path("/usr/local/bin/claude"),
    Path("/usr/bin/claude"),
]

DEFAULT_CONFIG = {
    "name": "",
    "signature": "",
    "tone": "friendly, concise, professional",
    "language": "English",
    "num_suggestions": 3,
    "claude_path": "",
    "claude_model": "",
}

CLAUDE_TIMEOUT_SECONDS = 90


class SuggestRepliesError(RuntimeError):
    """Raised for any expected failure; message is shown to the user."""


def load_config() -> dict:
    path = CONFIG_PATH if CONFIG_PATH.exists() else EXAMPLE_CONFIG_PATH
    if not path.exists():
        return dict(DEFAULT_CONFIG)
    try:
        with open(path, "r", encoding="utf-8") as f:
            user_config = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        raise SuggestRepliesError(f"Could not read config at {path}: {exc}") from exc
    config = dict(DEFAULT_CONFIG)
    config.update({k: v for k, v in user_config.items() if v not in (None, "")})
    if path == EXAMPLE_CONFIG_PATH:
        print(
            f"Warning: no config.json found; using {EXAMPLE_CONFIG_PATH.name} "
            "defaults. Run install.sh or copy config.example.json to config.json.",
            file=sys.stderr,
        )
    return config


def resolve_claude_binary(config: dict) -> str:
    configured = config.get("claude_path", "")
    if configured:
        candidate = Path(os.path.expanduser(configured))
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)
        raise SuggestRepliesError(
            f"config.json sets claude_path={configured!r} but that file is not "
            "an executable. Fix or clear claude_path in config.json."
        )

    found = shutil.which("claude")
    if found:
        return found

    for candidate in COMMON_CLAUDE_LOCATIONS:
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)

    raise SuggestRepliesError(
        "Could not find the Claude Code CLI ('claude'). Install it from "
        "https://claude.com/claude-code and make sure `claude` works in a "
        "normal terminal, or set \"claude_path\" in "
        f"{CONFIG_PATH} to its full path (try `which claude`)."
    )


def read_input() -> dict:
    raw = sys.stdin.read()
    if not raw.strip():
        raise SuggestRepliesError("No input received on stdin (expected a JSON object).")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SuggestRepliesError(f"Input was not valid JSON: {exc}") from exc

    sender = str(data.get("sender") or "").strip()
    subject = str(data.get("subject") or "").strip()
    body = str(data.get("body") or "").strip()

    if not body and not subject:
        raise SuggestRepliesError("The selected message has no subject or body to reply to.")

    return {"sender": sender, "subject": subject, "body": body}


def truncate(text: str, max_chars: int = 6000) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n[...message truncated...]"


def build_prompt(email: dict, config: dict, count: int) -> str:
    name = config.get("name") or "the recipient"
    tone = config.get("tone") or "friendly, concise, professional"
    language = config.get("language") or "English"

    return f"""You are drafting email replies on behalf of {name}.

Original message:
From: {email['sender'] or '(unknown sender)'}
Subject: {email['subject'] or '(no subject)'}

{truncate(email['body']) or '(no body text)'}

Write {count} distinct possible reply {"options" if count > 1 else "option"} to this
email, in {language}, in a {tone} tone. Each reply should:
- Be a complete, ready-to-send email body (greeting through closing line).
- Directly address what the sender asked or said.
- NOT include a final signature/sign-off name (e.g. no "Best, {name}") — that is
  appended automatically afterward. It's fine to end with a closing phrase like
  "Best," or "Thanks," with no name after it.
- Be meaningfully different from the other options in approach or length, if more
  than one is requested (e.g. a short direct reply vs. a warmer/more detailed one).

Respond with ONLY a JSON array of {count} string{"s" if count != 1 else ""} —
no markdown code fences, no explanation, no extra text before or after the array.
Example shape: ["reply text one", "reply text two"]"""


def extract_json_array(text: str) -> list:
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1 or end < start:
        raise SuggestRepliesError(
            "Claude's response did not contain a JSON array. Raw output:\n" + text[:2000]
        )
    snippet = text[start : end + 1]
    try:
        parsed = json.loads(snippet)
    except json.JSONDecodeError as exc:
        raise SuggestRepliesError(
            f"Could not parse Claude's reply suggestions as JSON: {exc}\nRaw output:\n"
            + text[:2000]
        ) from exc
    if not isinstance(parsed, list) or not all(isinstance(x, str) for x in parsed):
        raise SuggestRepliesError("Claude's response was not a JSON array of strings.")
    cleaned = [s.strip() for s in parsed if s.strip()]
    if not cleaned:
        raise SuggestRepliesError("Claude returned no usable reply suggestions.")
    return cleaned


def call_claude(claude_bin: str, prompt: str, config: dict) -> str:
    cmd = [claude_bin, "-p", prompt]
    if config.get("claude_model"):
        cmd += ["--model", config["claude_model"]]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=CLAUDE_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        raise SuggestRepliesError(
            f"Claude Code did not respond within {CLAUDE_TIMEOUT_SECONDS}s. "
            "Try again, or check that `claude` works normally in a terminal."
        ) from exc
    except OSError as exc:
        raise SuggestRepliesError(f"Failed to run '{claude_bin}': {exc}") from exc

    if result.returncode != 0:
        stderr = (result.stderr or "").strip()
        hint = ""
        if "login" in stderr.lower() or "auth" in stderr.lower():
            hint = " You may need to run `claude` once in a terminal and log in."
        raise SuggestRepliesError(
            f"Claude Code exited with an error (code {result.returncode}).{hint}\n"
            f"{stderr[:1500] or '(no error output)'}"
        )

    if not result.stdout.strip():
        raise SuggestRepliesError("Claude Code returned no output.")

    return result.stdout


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--count",
        type=int,
        default=None,
        help="Number of reply suggestions to generate (overrides config.json).",
    )
    args = parser.parse_args()

    try:
        config = load_config()
        count = args.count if args.count and args.count > 0 else int(
            config.get("num_suggestions") or 3
        )
        email = read_input()
        claude_bin = resolve_claude_binary(config)
        prompt = build_prompt(email, config, count)
        raw_output = call_claude(claude_bin, prompt, config)
        replies = extract_json_array(raw_output)[:count]
    except SuggestRepliesError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(json.dumps({"replies": replies}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
