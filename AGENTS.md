# Repository Guidelines

## Project Overview
Personal brand landing page for **danyzmaj** (deployed at `https://www.danyzmaj.com/`). A single self-contained HTML file renders an animated SVG logomark on a dark "letterpress" background. No application logic, no backend.

## Architecture & Data Flow
- Zero-dependency static site: one HTML document with inline `<style>`, inline SVG, and one tiny inline `<script>` (a single click listener). No external requests (favicon is an inline `data:image/svg+xml` URI).
- **Tap-morph architecture** (branch `feat/dragon-scroll-logo`): tapping/clicking the mark toggles it between the Z monogram and a top-down dragon. The whole page is a `<button class="trigger">` wrapping the SVG; JS only toggles `.awake` on `<html>` and mirrors it to `aria-pressed` — no per-frame JS.
- The choreography itself is pure CSS: `--p` is a registered custom property (`@property --p{syntax:'<number>'}`) that CSS-transitions 0→1 (`.awake`) or 1→0 on the toggle. Sub-timeline ramps (`--p1` straighten, `--ph` head flip, `--p2` wings, `--p3` fire) are `clamp(0,calc(…),1)` windows of `--p`, defined on the `svg` and recomputed live every animation frame as `--p` interpolates — this reactive recompute is what makes a single transitioned number drive a multi-beat sequence.
- Forward and reverse use different tokens: `html{transition:--p 1400ms var(--reveal)}` for the awakening (evenly-paced `cubic-bezier(0.4,0,0.2,1)` so all four beats stay legible — do NOT reuse the punchy `--ease` token here, it front-loads the whole show into the first 300ms), `html:not(.awake){…var(--recoil)}` for a quicker back-loaded snap home. Re-verify pacing by sampling `getComputedStyle(document.documentElement).getPropertyValue('--p')` at several `setTimeout` points after a click if you touch these curves — don't judge by end-state screenshots alone.
- SVG is split into anatomical groups — `#spine`, `#head` (`.side` profile / `.crown` top-down layers), `#tail`, `#wings` (`.fold`), `#spark`/`#fire` — each animated with `calc()`-interpolated CSS transforms (`transform-box:view-box`, absolute `px` origins). Transforms + opacity only; the world is ink/bone die-cut, so NEVER cross-fade with alpha — reveals use scale collapse/expand (e.g. the head's profile→bird's-eye card-flip).
- At `--p:0` the mark must render pixel-identical to the original monogram; path data is duplicated in the favicon data URI and must stay in sync with the `.side`/skeleton paths.
- Layout: unchanged from the original single static viewport (`body` grid, `overflow:hidden`, no scroll container) — the interaction lives entirely in the button/CSS, not in page height.
- SVG layering (paint order): wings → tail → spine → head → spark; `.body` (bone) with `.hole` (ink cutouts), `.acc` (ember accent).

## Key Directories
Flat repo — no directories.
- `index.html` — the entire site.
- `.gitignore` — ignores Python bytecode, `.DS_Store`, `.worktrees/`.

## Development Commands
No build, lint, or test tooling. Preview locally:
```sh
open index.html                 # macOS, file:// is sufficient
python3 -m http.server 8000     # or serve over HTTP
```

## Code Conventions & Common Patterns
- **Everything inline**: keep CSS in the `<head>` `<style>` block and SVG inline; do not split into separate files or add dependencies.
- **Design tokens** live as CSS custom properties on `:root` with poetic comments:
  `--ink:#171210` (background), `--bone:#F2EDE4` (mark), `--ember:#FF6A1F` (accent), `--ease` (620ms entrance flourish), `--reveal`/`--recoil` (tap-morph in/out curves). Reference tokens via `var(--…)`; never hardcode these colors elsewhere. `theme-color` meta mirrors `--ink`.
- **Compact CSS style**: no spaces after `:` or around `{}`, one rule per line where short.
- **Accessibility is deliberate**: visually-hidden `<h1>` for the page title (kept independent of the interactive control), the tappable mark is a real `<button>` with its own `aria-label`/`aria-pressed` (the inner `svg` is `aria-hidden`), a visible `:focus-visible` ring in `--ember`, and a `prefers-reduced-motion` query that disables the `--p` transition (`html{transition:none}`) so the toggle snaps instead of scrubbing — preserve all of these when editing.
- **Animation**: entrance `strike` (620ms, `--ease`) plays once on load; infinite `pulse` on `.acc`; the tap morph is a CSS transition on `--p`, not a keyframe — see the tap-morph architecture note above for timing tokens.
- Viewport sizing uses `min-height:100svh` with `100vh` fallback and `min(58vmin,620px)` for the mark — keep the fluid-with-cap pattern.

## Important Files
- `index.html` — entry point, styles, markup, favicon: the whole project.

## Runtime/Tooling Preferences
- No runtime, package manager, or framework — and none should be introduced. Changes must keep the page a single dependency-free HTML file.
- `.gitignore`'s Python entries only anticipate ad-hoc local scripts (e.g., `http.server`); there is no Python code in the repo.

## Testing & QA
- No test framework. QA is visual: open the page in a browser, verify the mark at rest matches the original monogram exactly, click/tap it and watch the full sequence (skeleton straightens → head flips to bird's-eye → wings unfold → fire blooms above the snout), tap again to confirm it recoils cleanly back to the Z, and tap rapidly to confirm interruption doesn't glitch.
- Also verify: keyboard activation (Tab to focus, Enter/Space to trigger, visible focus ring), no-JS (scripts disabled → static Z, button present but inert), reduced-motion (instant snap, no transition), and mobile/desktop centering.
- When touching SVG paths, update both the inline `<svg>` and the favicon data URI.
