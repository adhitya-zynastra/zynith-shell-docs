# INVALID / CONTAMINATED MEASUREMENTS

These numbers were produced and briefly believed. They are recorded so nobody rediscovers them in a log and treats
them as data. **None of them may enter an authoritative table.**

## Source of contamination

An incremental build following a layout change to `src/ui/signal.h` produced a binary with mixed `Signal::State`
layouts across translation units. It crashed at startup in an unrelated constructor and, before that was
understood, every CPU figure taken from it was inflated. Full analysis:
`04_Incidents/postmortems/2026-09-21-incremental-build-abi-skew.md`.

| Discarded figure | What it claimed | Reality on a clean build |
|---|---|---|
| noctalia idle **6.92 %**, niri 5.67 % (at `08f5454`) | The lifetime fix had tripled idle CPU | 1.40 % / 0.40 % |
| noctalia idle **3.67 %** (at `e9e27b0`) | A partial regression existed | same as above; the build was also incremental |
| noctalia idle **6.50–7.17 %** across several samples | A real regression somewhere in the shell | artifact |
| **192–206 ms** CPU per wallpaper apply | Applying was extremely expensive | **38 ms** |
| "apply x5" and state-audit tables taken in that window | — | re-measured entirely after the clean rebuild |

## A second, unrelated invalid metric

During the wallpaper-quality investigation, a Laplacian sharpness comparison put the rendered card at **3 242**
against **6 398** for the reference tier, suggesting the promotion had failed. That comparison was invalid: the
reference used ImageMagick's Lanczos resampling while the shell uses GPU bilinear filtering, and the crops were not
aligned. The authoritative evidence is the instrumented `frameW = 753.6 / texW = 768`.

## Rule derived from this

Record `build=clean|incremental|instrumented` next to every measurement. Only `clean` may be quoted. Counters
(decode counts, cache hits, context-switch counts per operation) are acceptable from instrumented builds because
they are not timing-dependent — those rows are marked as such in `optimizations.csv`.
