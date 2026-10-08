# Rogue Assembly Faction Description

A config-driven image builder for Rogue Assembly's Torn faction description.

The whole point of this repo is to stop rebuilding one giant image every time a perk, rule, requirement, or Rogue Code item changes. The description is split into stable section URLs, while the editable wording lives in `faction_config.json`.

## Generated sections

The builder creates:

- `docs/recruiting.png` — recruiting banner
- `docs/hero.png` — faction hero artwork
- `docs/about.png` — editable About Our Faction panel
- `docs/rogue-code.png` — editable Rogue Code panel
- `docs/footer.gif` — real animated GIF footer
- `docs/full-preview.png` — static full-page preview
- `docs/torn-embed-snippet.html` — ready-to-copy image tags

## Updating faction information

Edit `faction_config.json` and commit the change. The GitHub Action rebuilds the images without changing their public URLs.

The text panels automatically grow taller when wording wraps onto extra lines, so routine wording changes should not require manually redesigning the image.

## GitHub Pages URLs

Once GitHub Pages is enabled for this repository using **GitHub Actions** as the source:

- https://purplezyn.github.io/faction-description/recruiting.png
- https://purplezyn.github.io/faction-description/hero.png
- https://purplezyn.github.io/faction-description/about.png
- https://purplezyn.github.io/faction-description/rogue-code.png
- https://purplezyn.github.io/faction-description/footer.gif

Preview:

- https://purplezyn.github.io/faction-description/

## Why GIFs work here

Purple's personal signature is rendered into one final PNG, so animated source GIFs get flattened to a single frame. This faction project keeps the animated footer as its own final `footer.gif`, so Torn can display the animation directly without sending it through the PNG compositor.

## Current art source

The first working build reuses Rogue Assembly artwork already stored in the existing PurpleZyn GitHub assets. The art layer is intentionally separate from the generated text panels, so it can be swapped later without touching the faction wording or layout code.
