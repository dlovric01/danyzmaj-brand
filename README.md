# danyzmaj — brand kit

Open **`propositions.html`** for the current shortlist: three fire-breathing Z marks, two fanged ones,
and the fanged Z built out as a dark theme. Earlier rounds sit beside it:
`propositions-fanged-four.html`, `propositions-all-nine.html`, `propositions-round-two.html`, or **`index.html`** for the
full kit built out of direction 01. That is the brand guide: seven plates and a file index, and it
is built out of the real assets, so if a file is broken you see it there first.

`DESIGN.md` is the system and why each rule exists. `PRODUCT.md` is what the company is.

## The idea in one line

`zmaj` is *dragon*. The mark is a dragon drawn as the letter **Z**, struck like a printer's device
on everything that leaves the workshop.

## Pick the right file

| You are doing | Use |
|---|---|
| Website header, dark background | `logo/lockup-horizontal-inverse.svg` |
| Website header, light background | `logo/lockup-horizontal.svg` |
| Square space — app store, profile, sticker | `logo/lockup-stacked-inverse.svg` |
| Just the creature, ≥96px | `logo/mark.svg` (`-ink`, `-bone` for other grounds) |
| Just the creature, 40–96px | `logo/mark-small.svg` |
| Just the creature, 16–40px | `logo/mark-tiny.svg` |
| A stamp — invoice, footer, sign-off, packaging | `logo/seal.svg` (never below 96px) |
| Browser tab | `logo/favicon.svg` + `favicon-16/32/48.png` |
| iOS home screen | `logo/apple-touch-icon-180.png` |
| App / store icon | `logo/app-icon-512.png`, `app-icon-1024.png` |
| GitHub, X, LinkedIn avatar | `social/avatar-512.png` (safe under a circle crop) |
| Link preview when someone shares danyzmaj.com | `social/og.png` (1200×630) |
| Etching, embroidery, one-colour print | `logo/lockup-horizontal-mono-*.svg` |
| Anything needing type without the creature | `logo/wordmark*.svg` |

Every logo SVG is one filled path with no font dependency — the wordmark is outlined, so it renders
identically in a browser, in Illustrator, on a laser cutter, or in a t-shirt printer's software.

## Wire it into a site

```html
<link rel="icon" type="image/svg+xml" href="logo/favicon.svg">
<link rel="apple-touch-icon" sizes="180x180" href="logo/apple-touch-icon-180.png">
<meta property="og:image" content="social/og.png">
<link rel="stylesheet" href="tokens/danyzmaj.css">
```

Then use the variables: `var(--dz-ink)`, `var(--dz-cinnabar)`, `var(--dz-bone)`, `var(--dz-space-6)`.
`tokens/danyzmaj.tokens.json` carries the same values for anything that is not CSS.

## Five rules that matter more than the rest

1. **Cinnabar `#DA3A20` never sets body text.** It measures 4.08:1 on ink and 3.91:1 on bone — both
   below the 4.5:1 floor. It is for the mark and for display type. When you need red on text, or a red
   field with a sentence in it, use oxide `#8E1F0E`.
2. **Pick the cut by rendered size**, not by convenience. A primary mark at 24px turns to mush; that
   is what the tiny cut is for.
3. **Clearspace is 0.25 × mark height** on all four sides. Nothing enters it.
4. **App icons ship square on purpose.** iOS, Android and the app stores apply their own rounded
   mask. Round the container only when you are drawing it yourself — `0.2 × side`, as the favicon does.
5. **The dragon faces left, sits flat, and is one solid colour.** Never mirrored, rotated, stretched,
   recoloured, gradient-filled or shadowed. Plate 02 shows each of those failing.

## Still yours to decide

- **Tagline.** Three candidates are parked at the bottom of the guide. None is committed.
- **What you sell, in your own words.** The system assumes contract software work — inferred from
  your setup, never stated by you. Nothing visual depends on it; only descriptor copy does.
- **Founding year, entity name, registration line** for the imprint. Not invented here.

## Regenerating the assets

The dragon is parametric, not a traced drawing: a variable-width ribbon along a spine, a dorsal crest
placed on that ribbon's own normals, and a head built from overlapping angular masses. Tune a number
and every file updates.

```sh
python3 build/generate.py     # rewrites logo/, social/og.svg, guide/ — no dependencies
```

Verified two ways: regenerating reproduces every shipped SVG byte for byte, and flood-filling the
rendered marks leaves exactly the holes that are supposed to be there — eye plus nostril on the
primary cut, eye alone on small and tiny — and no stray sliver anywhere else.

The PNGs are rasterised from those SVGs (16, 32, 48, 180, 512, 1024, 1200×630, 2048). Any SVG→PNG
tool works; keep the exact pixel sizes.

To change the wordmark itself — different letters, weight or tracking — re-outline it:

```sh
python3 -m venv build/.venv && build/.venv/bin/pip install fonttools
cd build
curl -sSL -o BodoniModa.ttf "https://raw.githubusercontent.com/google/fonts/main/ofl/bodonimoda/BodoniModa%5Bopsz%2Cwght%5D.ttf"
curl -sSL -o Archivo.ttf    "https://raw.githubusercontent.com/google/fonts/main/ofl/archivo/Archivo%5Bwdth%2Cwght%5D.ttf"
.venv/bin/python outline.py   # rewrites wordmark.json + archivo.json
python3 generate.py
```

Bodoni Moda and Archivo are OFL-licensed; the font binaries are deliberately not committed here.
