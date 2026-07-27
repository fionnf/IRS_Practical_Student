# The interactive bench page

`index.html` is the **IRS Practical Bench** — a single, self-contained page with
four interactive instruments:

1. **Interferometer Console** — window length, apodization, zero-filling
2. **Rovibrational Simulator** — drag Bₑ, Dₑ, ν₀, temperature, isotopes
3. **Normal Mode Explorer** — animated modes, live dipole and polarizability
4. **Symmetry & Character Tables** — 34 molecules across 15 point groups, with
   IR/Raman activity *derived* from the character table rather than looked up

It is linked from Section 0 and Section F of the lab manual.

## Hosting it

The file has **no external dependencies at all** — every font, style and script
is inlined, and the only external-looking URL in it is the SVG XML namespace,
which is an identifier and not a fetch. Verified with a headless browser: five
tabs render, zero console errors, zero failed network requests. So it can be
served by anything that serves static files, and students need no account of any
kind to open it.

**Live at <https://irs-practical.vercel.app/>** — this is the URL both lab
manuals point at. It is a Vercel project tracking this repository, so every push
to `master` redeploys it automatically; there is nothing to do by hand.

`vercel.json` in the repository root drives that deploy. It pins `framework`,
`installCommand` and `buildCommand` to no-ops and sets `outputDirectory` to
`docs`, giving a pure static deploy with this directory as the web root. Leave
Vercel's **Root Directory** at the repository root: pointing it at `docs` makes
Vercel look for `docs/vercel.json` instead and the config silently stops
applying.

**Alternatives**, should the Vercel project ever go away:

- **GitHub Pages**, no extra service and no config:
  `Settings ▸ Pages ▸ Source: Deploy from a branch ▸ master ▸ /docs`, which
  serves it at `https://fionnf.github.io/IRS_Practical/`.
- **Netlify / Cloudflare Pages**: import the repository and publish `docs/`.

If you move it, update the URL in **five** places — three `\url{}` references in
`IRS-Manual.tex`, two in `IRS_Assistant_Manual.tex` — plus the repository
READMEs.

**Offline**: the file works from `file://` too. Copy it onto a lab machine or a
USB stick and it behaves identically — useful if the lab network is restricted.

## Updating it

The page is generated from sources kept with the course material rather than
edited here by hand. Regenerate, then replace `index.html`, keeping the
`<!doctype html>` / `<html>` / `<head>` / `<body>` wrapper — Claude artifacts are
published without it, and a browser given the unwrapped file falls back to quirks
mode.
