# Design Tokens — Geometry, Typography, Colour, Contrast

**Implemented 2026‑09‑26 (sixth batch).** Code: `src/ui/tokens.*`, `src/ui/typography.*`,
`src/ui/semantic_color.*`, `src/render/text/font_spec.h`. Tests: `design_tokens_test`, `cairo_text_renderer_test`.

Tokens are **design-system constants, not settings**. Each names a decision by its purpose, so every surface asking
"what radius does a floating surface have?" gets one answer. `Style`'s constants stay as the storage and remain
valid; tokens name them and add the steps `Style` lacked.

## Geometry (`ui::tokens`)

| Token | Values (scale 1) | Notes |
|---|---|---|
| Spacing | Inline 4 · Related 8 · Control 12 · Group 16 · **Section 24 · Surface 32 · Composition 48 · Stage 64** | the scale previously stopped at 16; density multiplies spacing only |
| Radius — Surface | max(`scaledRadiusXl`, 16) = **16 px** at the preset's 0.6 corner scale | **replaced three private copies** (panels, toasts, wallpaper browser) — no visual change |
| Radius — Plate | `scaledRadiusXl` (≈ 7.2 px) | cards embedded in a surface |
| Radius — Control | `scaledRadiusLg` (≈ 5.4 px) | buttons, fields, tiles |
| Radius — Stage | 0 | full-bleed compositions |
| `pill(h)`, `concentric(parent, inset)` | h/2; parent − inset (≥ 4) | capsules; nested corners sharing a centre |
| Stroke | hairline 1 · focus 2 · emphasis 3 | |
| Control heights | 32 / 38 / 44 | = `Style` |
| Icons / icon containers | 16 / 20 / 24 · 32 / 40 / 48 | containers are new |

## Typography (`ui::type`)

**Three faces, one job each:**
- **Interface:** `[shell].font_family`, Montserrat here. Inter is the recommended face.
- **Display:** `[shell].display_font_family`, else Space Grotesk, else the interface face.
- **Data:** JetBrains Mono.

Each face is a **Pango family list**, so an uninstalled font degrades to the next one instead of a random system
default. As of this batch **Inter, Space Grotesk and Sora are not installed**; only JetBrains Mono is. The display
role therefore renders in Montserrat until I install Space Grotesk. Sora is used nowhere; no role needed it.

| Role | Size / weight | Face | Tabular | For |
|---|---|---|---|---|
| `display` | 64 / Light | display | ✓ | hero numerals: a clock, a surface's one big value |
| `headline` | 32 / Normal | display | ✓ | a section's primary value |
| `title` | 20 / Medium | interface | | surface and section titles (= old header size) |
| `subtitle` | 16 / Medium | interface | | primary rows (= old title size) |
| `body` | 14 / Normal | interface | | everything else (= old body size) |
| `label` | 13 / Medium | interface | | control labels, captions (= old caption size) |
| `micro` | 11 / Medium | interface | | tags, counts (= old mini size) |
| `numeric` | 14 / Medium | interface | ✓ | numbers that change, in the UI voice |
| `data` | 13 / Normal | mono | ✓ | literal technical values |

- **The ramp spans 11 → 64 px (5.8×)**, where the old ramp spanned 11 → 20 (1.8×). The middle steps are the old
  sizes, so existing text keeps its size.
- **Tabular figures:** a role asks for them with a `" #tnum=1"` suffix. The text renderer splits it into family and
  OpenType feature (`pango_font_description_set_features`, Pango ≥ 1.56; this machine has 1.57.1).
  - **Measured:** Montserrat "1111" is 28 px wide and "0000" 52 px without the feature; with it they are equal.
  - A test also checks that letters measure identically with and without the suffix. That proves the suffix never
    leaks into the family name, which would otherwise fall back to a different font and could pass by accident.
- **Not implemented:** letter-spacing (tracking) and uppercase transforms need text-pipeline support that does not
  exist yet. They were left out rather than specified without effect.

## Semantic colour (`ui::color`)

These are resolved to the existing wallpaper-derived palette roles; no palette entry was added and the theme
engine is unchanged.

| Semantic | Resolves to |
|---|---|
| Accent / OnAccent | primary / on_primary |
| Surface / OnSurface / Muted | surface / on_surface / on_surface_variant |
| Hairline | on_surface @ 0.12 |
| Error / OnError | error / on_error |
| **Warning** | **error** — the palette has no warning role; the battery widget already used error for warnings. A real warning tone needs the theme engine to produce one (future work) |
| SelectionFill / SelectionEdge | primary @ 0.16 / primary @ 0.5 — the nav indicator now takes these |
| Scrim | shadow @ 0.46 — the live modal backdrop's strength |

There is no "success" colour: success is the absence of error.

## Contrast

WCAG 2.x ratios, built on the relative-luminance function the shell already had (`readableTextColorForBackground`
uses it). `legibleOn(background, preferred, minRatio)`:
- keeps the preferred colour if it reaches the ratio;
- otherwise picks whichever of the palette's on-surface and surface contrasts more;
- reports `needsScrim` when neither reaches it.

The principle — colour by role and readability, not per component — came from the Ryoku study. The implementation
is our own: WCAG ratios, where Ryoku uses CIE L\* tone distance. **No surface consumes it yet**; its consumers are
text on the wallpaper (lock screen, desktop widgets), which Batch 7 redesigns.
