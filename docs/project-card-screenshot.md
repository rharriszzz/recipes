# Refresh the homepage project-card screenshot

The [central project directory](https://rharriszzz.github.io/) displays the actual
Recipes homepage using [`images/homepage-card.png`](../images/homepage-card.png)
from this repository. This is the maintained source image; the index does not
keep a second copy.

Refresh it when a recipe is added, removed, renamed, or reordered, or when the
homepage layout or typography changes. Include the refreshed PNG in the same
commit as the homepage changes when practical.

## Capture and check

Run from the Recipes repository root. Start by checking `git status` and bringing
your checkout up to date before making changes; preserve any existing local work.
The commands require Python 3.10+ and Node 20+.

```sh
npm ci
npx playwright install chromium
npm run capture:homepage-card
python3 scripts/validate.py
node tests/search.test.cjs
git diff --check
```

The capture command runs `scripts/build.py` itself, starts the local preview on
an available port, captures the current checkout, and closes its browser and
server. You do not need to deploy first or start a separate preview. On Linux,
use `npx playwright install --with-deps chromium` if system libraries are missing.

Open the generated PNG and check:

- The Recipes heading, introduction, and every current recipe link are visible.
- Long titles and the last recipe are not clipped.
- There is a small paper inset, without a large unused area on the right.
- The image contains the real page, without browser chrome or local paths.

The script uses Chromium at a 1280 × 900 desktop viewport with 2× pixel density.
It measures rendered text in `main.simple-index`, adds a 16-pixel inset, and
extends the capture height as the list grows. Image dimensions and recipe counts
are intentionally not fixed. If markup changes, update the script's locators
and crop calculation, then inspect the new PNG; keep the homepage's normal
layout rather than restyling it for the screenshot.

`package-lock.json` pins the Playwright version. Use `npm ci` for repeat captures;
do not upgrade dependencies just to refresh the image. A second capture on the
same machine can be compared with `sha256sum images/homepage-card.png` (or
`shasum -a 256` on macOS). Browser/font changes across systems can affect pixels,
so visual review still matters.

## Commit and publish Recipes first

Stage the PNG and the intended recipe, layout, script, or documentation changes.
Review `git diff --cached --stat` before committing. For an image-only refresh:

```sh
git add images/homepage-card.png
git diff --cached --check
git commit -m "Refresh Recipes homepage card screenshot"
git push origin main
```

If the PNG is unchanged, no image-only commit is needed. Do not commit `_site/`
or `node_modules/`.

Check the [Recipes Actions workflow](https://github.com/rharriszzz/recipes/actions)
for a successful build and deployment. Verify the published source image matches
the file you reviewed:

```sh
curl --fail --location --output /tmp/recipes-homepage-card-published.png \
  https://raw.githubusercontent.com/rharriszzz/recipes/main/images/homepage-card.png
cmp images/homepage-card.png /tmp/recipes-homepage-card-published.png
```

`cmp` produces no output when the files match. If a cache still serves the old
image, allow it to expire and check again before calling publication verified.

## Follow through in the central index

The index's `recipes` entry in `projects.json` points at this PNG. With the same
filename and accurate alt text/caption, an image refresh needs no index edit or
redeployment: the card loads the hosted image directly, subject to caching.

If its URL, description, or provenance changes, follow the index's
[project-image workflow](https://github.com/rharriszzz/rharriszzz.github.io/blob/main/docs/PROJECT_IMAGES.md).
Push Recipes first so the new source exists before publishing an index change.
Then visit the live directory and verify that the Recipes card loads the actual
new screenshot at desktop and mobile widths. A successful build alone does not
prove that a hosted image is reachable or displayed correctly.
