# danyzmaj — visual system

Durable rules. Exact values live in `tokens/danyzmaj.css` and `tokens/danyzmaj.tokens.json`;
this file owns the decisions those values serve.

## Direction contract

**THESIS** — danyzmaj is one person who signs the work, so the identity is a *struck imprint*, not a
startup logo. It refuses the solo-contractor default page: near-black canvas, Inter, one neon accent,
a grid of project cards, an "available for work" green dot.

**OWN-WORLD** — A press bed and the sheets struck on it. Warm iron-oxide black ground; cinnabar seal
ink carrying whole regions; brass hairlines instead of borders; bone sheets for anything that behaves
like paper. Didone display (the punch-cutter's own voice) against a workhorse grotesque. Nothing is
rounded except the seal. Recognizable with all content removed.

**STORY** — A client sees a craftsman's imprint before reading a word, understands the system in one
scroll, and leaves with the files.

**FIRST VIEWPORT** — Full-bleed press bed. The seal struck top-right at plate scale; `DANYZMAJ` set
across the width in Didone beneath it; one brass hairline; the imprint line and the domain in mono.

**FORM** — The colophon of a one-person workshop, rendered in the world's *saturated* materials
(seal paste and iron oxide) rather than its softest ones (cream paper, warm serif on ivory). First on
the derivation list of seven; the paper-and-letterpress rendition was explicitly rejected as the
default this world's clichés would have produced. Selected in-thread: the seed/dice script that
normally assigns the direction is not installed in this environment, so no roll was performed.

## Colour

Strategy: **Committed** — one saturated colour carries the surface, at page scale, in fields that own
whole regions. Not accents scattered over neutral.

- `ink #171210` is the ground. Chosen from the use scene, not the category: this is a workshop bed,
  and the cinnabar has to look *wet* on it. Light is never the ground.
- `cinnabar #DA3A20` is stamp ink. **Marks and display type only.** It measures 4.08:1 on ink and
  3.91:1 on bone — both below 4.5:1 — so it is forbidden for body copy in either direction.
- `oxide #8E1F0E` exists solely because cinnabar cannot carry text. 7.66:1 against bone in both
  directions. Use it for red text on sheets and for red fields that must hold small copy.
- `brass #C08A2E` replaces every neutral border. Hairlines, small-caps labels, metadata. 6.12:1 on ink.
- `bone #F2EDE4` is paper: sheet grounds and primary text on dark. `bone-dim` is secondary,
  `ash #948881` is the floor at 5.39:1 — nothing sits below it.
- Secondary text on a coloured surface is tinted from that hue, never grey.

## Type

- **Display: Bodoni Moda**, `opsz 72–96`, `wght 500–700`. Chosen because Bodoni cut his own punches
  and printed his own books — the exact profession this identity is built on — and because the
  Didone hairline makes cinnabar look struck rather than printed. Never below ~28px: the hairlines
  break. Tracking `-0.022em` at display sizes.
- **Text: Archivo**, 400–600. A workhorse grotesque that holds at 13px and stays out of the way.
- **Mono: JetBrains Mono**. Code, token values, measurements, URLs. Never a costume for "technical".
- Small-caps labels take `0.16em` tracking and brass. They are a *system* (plate numbers, field
  labels, metadata), not an eyebrow over every section.
- Body measure caps at 68ch. Display caps at 6rem.

## Geometry and depth

- Radius is `0`. The only curves in the system are the seal ring, the dragon itself, and an icon
  *display* container at `0.2 × side` (`--dz-radius-icon`). The shipped app-icon files are square
  on purpose: iOS, Android and the app stores apply their own mask, so rounding the source would
  round it twice. Round it only when you are drawing the container yourself.
- Borders are brass hairlines at ~46% opacity. A coloured `border-left` thicker than 1px is not part
  of this system.
- Depth is a **strike**: a hard 2px offset with no blur, plus one wide soft shadow —
  `--dz-shadow-strike` for boxes, `--dz-filter-strike` for a transparent shape such as the seal,
  where a box-shadow would trace the bounding box instead of the mark. Never a zero-offset halo,
  never glass.

## The mark

Three cuts, all the same animal, drawn as a dragon coiled into the letter **Z**:

| cut | file | use | detail |
|---|---|---|---|
| primary | `logo/mark.svg` | ≥96px | full dorsal crest, nostril, fang |
| small | `logo/mark-small.svg` | 40–96px | 3 crest spikes, heavier body, no nostril or fang |
| tiny | `logo/mark-tiny.svg` | 16–40px | 2 crest spikes, one horn, heaviest body, widest gape |

- Clearspace: `0.25 × mark height` on all four sides.
- The dragon always faces **left** (heraldic dexter). It is never mirrored, rotated, outlined,
  gradient-filled, or given a drop shadow of its own.
- The mark is a single filled path with `fill-rule: nonzero`. Eye and nostril are reversed-winding
  holes, so the mark works on any ground in one colour. Keep it that way: no second colour inside it.
- **The hole invariant.** Flood-filling the rendered background must leave exactly the sanctioned
  holes and nothing else: eye plus nostril on the primary cut, eye alone on small and tiny. Any
  other enclosed region is a defect — the ribbon's inner offset crossing itself at too tight a bend,
  or a spike pinching against the horn. Both happened during drawing and both are fixed by widening
  the geometry, never by nudging the fill rule. Re-check after any change to `build/generate.py`.
- Single-colour only: cinnabar, ink, or bone. The seal is the only container it may sit inside.
- Seal minimum 96px; below that use a cut of the bare mark.

## Motion

One authored moment: **the strike**. The seal lands from `scale(1.14) rotate(-8deg)` with an
exponential ease-out over 620ms, and the offset shadow appears as it settles. Interactive elements
answer with a press — 2px down, the hard offset shadow gone, an oxide fill darkening to
`cinnabar-struck` — over 180ms. Content is visible by default;
everything honours `prefers-reduced-motion`.

## Prohibitions with a reason

- No cards as page structure. This world composes in registers: one shared frame, cells divided by
  hairlines, the way a plate book rules its page — see `.register` and `.swatches` in the guide. A
  grid of individually bordered boxes is the thing this identity refuses. Nested cards never.
- No gradient text and no glass. Emphasis comes from weight, size, and the cinnabar field.
- No stock iconography. Any icon is drawn in the dragon's own chisel grammar or it does not ship.
- The dorsal crest, the offset strike shadow, and plate numbering are **native** to this world — they
  are the system, not decoration to be linted away. Plate numbers are load-bearing: the file index
  cites them.
