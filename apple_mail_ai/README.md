# Apple Mail AI Reply

An on-demand AI reply assistant for Apple Mail. Select an email, press a
shortcut (or use the Mail Script menu), get a couple of AI-suggested replies,
pick one, and it opens as a **draft** for you to review and send yourself.

**Nothing is ever sent automatically.** This tool only ever creates a draft.

It runs on your existing Claude subscription: the backend shells out to the
[Claude Code CLI](https://claude.com/claude-code) in headless mode
(`claude -p ...`), so usage draws on your Pro/Max plan limits — no separate
Anthropic API key, no separate billing.

macOS + Apple Mail only.

## What you get

- **Suggest Replies** — shows 3 (configurable) distinct reply options for the
  selected email in a picker; pick one and it opens as a draft.
- **Quick Reply** — the fast path: generates a single reply and opens it as a
  draft immediately, no picker.

Both appear as clickable items in Mail's Script menu, and can each be bound
to a keyboard shortcut (see below).

## Prerequisites

1. **macOS** with **Apple Mail** set up.
2. **Claude Code CLI** installed and logged in to your subscription:
   ```sh
   claude -p "say hi in 3 words"
   ```
   should print a short reply. If it asks you to log in, follow the prompts
   once — this plugin reuses that same login.
3. Xcode Command Line Tools (for `osacompile`), if not already installed:
   ```sh
   xcode-select --install
   ```

No Python packages need installing — `suggest_replies.py` only uses the
Python 3 standard library that ships with macOS.

## Install

```sh
bash apple_mail_ai/install.sh
```

This copies the backend to `~/Library/Application Support/AppleMailAI/` (a
stable location independent of this repo checkout) and compiles the
AppleScripts into Mail's Script folder. Re-running it is safe — it will not
overwrite an existing `config.json`.

Then edit your settings:

```sh
open "$HOME/Library/Application Support/AppleMailAI/config.json"
```

```json
{
  "name": "Your Name",
  "signature": "Best,\nYour Name",
  "tone": "friendly, concise, professional",
  "language": "English",
  "num_suggestions": 3,
  "claude_path": "",
  "claude_model": ""
}
```

- `signature` is appended to every suggested reply automatically — the model
  is told not to sign off with a name itself, so you won't get duplicates.
- `claude_path`: leave blank to auto-detect (`which claude`, then common
  install locations). Set this explicitly if scripts fail to find `claude`
  (see Troubleshooting).
- `claude_model`: leave blank to use Claude Code's default model, or set a
  specific model id (e.g. `claude-opus-4-8`) if you want to pin one.

## Enable the Mail Script menu

1. Open **Script Editor** (in Applications/Utilities).
2. Script Editor → Settings → General → check **"Show Script menu in menu bar"**.
3. Switch to **Mail**. You should see a scroll-shaped Script menu in the menu
   bar. Open it → **Suggest Replies** and **Quick Reply** should be listed
   (under a "Mail" or "Applications > Mail" submenu, depending on macOS
   version).

Click either one with a message selected in Mail to try it — this is the
"button" version of the feature.

## Add a keyboard shortcut

Apple Mail has no built-in way to bind a shortcut directly to a Script menu
item, so the standard (non-third-party) route is an Automator **Quick
Action** that runs the compiled script, which you then bind a shortcut to in
System Settings.

For **each** script (repeat for both "Suggest Replies" and "Quick Reply"):

1. Open **Automator** → **File → New** → choose **Quick Action**.
2. Set **"Workflow receives current"** to **no input**, and
   **"in"** to **Mail.app**.
3. In the search box, find the **"Run AppleScript"** action and drag it into
   the workflow.
4. Replace the placeholder script body with:
   ```applescript
   on run {input, parameters}
       tell application "Mail" to run script (POSIX file "SCRIPT_PATH")
       return input
   end run
   ```
   replacing `SCRIPT_PATH` with the full path to the compiled script, e.g.:
   ```
   /Users/YOURNAME/Library/Scripts/Applications/Mail/Suggest Replies.scpt
   ```
   (Simplest way to get the exact path: in Finder, `Cmd+Option+C` on the
   `.scpt` file to copy it, then paste inside the quotes.)
5. Save the Quick Action as **"AI Suggest Replies"** (or **"AI Quick
   Reply"** for the other one).
6. Go to **System Settings → Keyboard → Keyboard Shortcuts → Services**, find
   your new Quick Action under "General", and assign a shortcut (e.g.
   `⌃⌥⌘R` for Suggest Replies, `⌃⌥⌘Q` for Quick Reply).
7. The shortcut now works whenever Mail is frontmost with a message selected.

## Optional: an "AI Reply" mailbox for triage

If you'd like to file certain incoming mail for later attention (purely
organizational — it does **not** trigger anything automatically; generation
only ever happens when you press the shortcut or click the Script menu
item):

1. Mail → Mailbox → New Mailbox… → name it **AI Reply**.
2. Mail → Settings → Rules → Add Rule, matching whatever senders/criteria you
   want, with the action "Move Message" → **AI Reply**.
3. When triaging that mailbox, just select a message and use the shortcut or
   Script menu as normal.

## How replies are drafted

- The AppleScript reads the sender, subject, and body of the selected
  message and pipes it as JSON to `suggest_replies.py`.
- The script builds a prompt (using your `tone`/`language`/`name` from
  `config.json`) and calls `claude -p ...` to get back a JSON array of reply
  options.
- Mail's `reply` command creates a proper threaded draft (quoting the
  original, addressed correctly); your chosen suggestion + signature is
  inserted above the quoted text.
- The draft window opens **for you to review** — no message is ever sent by
  this tool. If Mail's `reply` command fails for some reason, it falls back
  to composing a fresh message addressed to the sender instead, still as a
  draft only.

## Troubleshooting

**"Could not find the Claude Code CLI"**
Run `which claude` in Terminal. If it prints a path, put that exact path in
`claude_path` in `config.json`. If it prints nothing, install Claude Code
first, then re-check.

**"Claude Code exited with an error... You may need to run `claude` once in
a terminal and log in."**
Run `claude` interactively once and complete the login flow, then try again.

**Nothing happens when I click the Script menu item**
Check Script Editor → Settings → General → "Show Script menu in menu bar" is
checked, and that you're looking at the menu while **Mail** (not another
app) is frontmost.

**A macOS permission prompt appears the first time**
That's expected — the script needs permission to control Mail (Automation).
Click OK. If you accidentally denied it, re-enable under
**System Settings → Privacy & Security → Automation**.

**A suggestion took a while / timed out**
`suggest_replies.py` waits up to 90 seconds for Claude Code. If your network
or the CLI is slow, just try again — nothing is sent in the meantime either
way.

**I want to change how many suggestions "Suggest Replies" shows**
Edit `num_suggestions` in `config.json`.

## Notes

- Pure Python 3 standard library — no `pip install` needed.
- This plugin was developed and reviewed without a live macOS/Apple Mail
  environment to test against, since it was built in a Linux sandbox. The
  AppleScript follows well-established, documented idioms, but if something
  doesn't behave as expected, open the `.applescript` source in **Script
  Editor** (Applications/Utilities) and use **Run** there — it gives real
  line-numbered error messages, which is the fastest way to iterate on any
  fix.
