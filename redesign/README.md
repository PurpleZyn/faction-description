# Cinematic redesign — review draft

The GitHub Pages workflow builds this review draft at https://purplezyn.github.io/faction-description/redesign/ alongside the original layout. Changes to main rebuild the preview automatically. Publishing here does not update the Torn faction description.

## Review and edit

- Open `preview/index.html` locally, or inspect `preview/full-preview.png`.
- Edit `content.json` for all section wording, names, roles, recruitment links and perk values.
- For the Pages output, use `python redesign/build_preview.py --output docs/redesign`.
- Run `python redesign/build_preview.py` from the repository root (Pillow requirements plus DejaVu fonts).
- Generated PNGs contain rendered text, but source copy stays separate from the artwork and reflows on rebuild.
- The brand wordmark and Derlin's shirt lettering are part of the artwork.

## Content decisions

The user-provided recruitment copy supersedes the old config: 250 monthly respect, $1m vault balance, daily activity, age 19+, level 15+. Monthly ranked wars and weekly chains remain. Core screenshot confirms 1,000-hit chain capacity. Peace-mode screenshot confirms +10 travel capacity, 45% reduced travel fees, 6% strength/speed and 5% defense/dexterity gym gains. These are explicitly labeled as peace-mode perks; no war-mode details are included. Free Xanax is described for wars, following the latest recruitment copy.

Ivory is a full leadership member, alongside Sativa, Derlin, Bee and Purple. John, Van and DungBeetle are VIP Rogues. Image order matches caption order. Old footer GIF is excluded.

## Art provenance

Cover, leadership, VIP and panel-background assets were made with the built-in image-generation tool using user-supplied character and brand references. Art direction: cinematic gothic headquarters, violet roses and blackened silver thorns; recognizable individual outfits; warm skin tones and violet edge lighting; no embedded names, roles or changeable requirements. All project assets are in this directory.

## Before release

This is an assembled review draft. Review copy, character likenesses and spacing at the intended Torn width. The user and faction will approve the design before installing the resulting image URLs in Torn. The existing root preview remains available.
