# Rogue Assembly faction description

**[View the current design](https://purplezyn.github.io/faction-description/)**

This repository is the working version of our modular Torn faction description. The main page always shows the latest build. It does not change the faction description inside Torn until you add the images there.

## Where to find things

| What you want to change | Where to go |
| --- | --- |
| Wording, rules, perks, five leaders and their roles | [content.json](content.json) |
| Current scene and cover images | [artwork/](artwork/) |
| Layout, fonts, image generation | [scripts/build.py](scripts/build.py) |
| Automatic build and publishing | [.github/workflows/build.yml](.github/workflows/build.yml) |

## Make an update

1. Edit **content.json** or replace the relevant file in **artwork/**.
2. Commit the change to **main**.
3. Wait for **Build faction description** in the Actions tab to finish. The preview updates automatically.

Only the five main leaders have names and roles on the page. Other characters are artwork without member captions or implied roles. The leadership art includes two supporting figures behind the five main leaders; there is no separate VIP section.

## Artwork files

- `cover.jpg` — rose emblem and faction wordmark
- `clubhouse.jpg` — community scene
- `leadership.jpg` — five leaders with two supporting figures behind them
- `rooftop.jpg` — faction activities scene
- `armory.jpg` — equipment and support scene
- `panel-background.jpg` — repeating background shared by every section
- `thorn-overlay.png` — transparent vine rails and subtle corners shared by every scene

The images are separate from the editable wording. Changing text does not require remaking artwork.

## Build locally

Install Python, Pillow (`pip install -r requirements.txt`) and DejaVu fonts (`fonts-dejavu-core` on Ubuntu), then run:

```sh
python scripts/build.py
```

Open **build/index.html** to review. That folder is generated and ignored by Git, so it does not clutter this repository. GitHub Actions publishes it directly without creating extra image-update commits.

## Review and eventual Torn installation

- [Current preview](https://purplezyn.github.io/faction-description/)
- [Full-page image](https://purplezyn.github.io/faction-description/full-preview.png)
- [Image embed markup](https://purplezyn.github.io/faction-description/torn-embed-snippet.html)

The old `/redesign/` preview URL redirects to the current main page. Test the embed markup in Torn's editor when you are ready; the preview alone does not validate Torn's editor behavior.

## Older versions

Previous drafts, old artwork, and old configurations are recoverable through **Git history**. They have been removed from the current folder tree so there is only one active version. No history was erased.

## Shared rose-and-thorn theme

Every section uses the same background at a fixed scale. It repeats down the page with mirrored joins, and the pattern continues across section boundaries. Text can grow without stretching the flowers. The transparent overlay frames the cover and every scene with subtle corner vines, while edge decoration stays outside the text column. Source portraits stay separate from the theme, so a future image replacement receives the same framing automatically.
