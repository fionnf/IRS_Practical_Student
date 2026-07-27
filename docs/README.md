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

**GitHub Pages** (no extra service, no config):
`Settings ▸ Pages ▸ Source: Deploy from a branch ▸ master ▸ /docs`.
It then appears at `https://fionnf.github.io/IRS_Practical/`, which is the URL
the lab manual points at.

**Vercel / Netlify / Cloudflare Pages**: import the repository and serve the
`docs/` directory. `vercel.json` in the repository root already sets
`outputDirectory` to `docs`, so a Vercel import needs no further configuration.
If you deploy somewhere with a different domain, update the three `\url{}`
references in `IRS-Manual.tex` and the two in `IRS_Assistant_Manual.tex`.

**Offline**: the file works from `file://` too. Copy it onto a lab machine or a
USB stick and it behaves identically — useful if the lab network is restricted.

## Updating it

The page is generated from sources kept with the course material rather than
edited here by hand. Regenerate, then replace `index.html`, keeping the
`<!doctype html>` / `<html>` / `<head>` / `<body>` wrapper — Claude artifacts are
published without it, and a browser given the unwrapped file falls back to quirks
mode.
