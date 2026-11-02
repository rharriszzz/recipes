# Recipes

A small, dependency-free static recipe website, published at **https://rharriszzz.github.io/recipes/**.

Ingredients and instructions stay together in cooking order. The original ivory background, Tahoma/Arial type, brown text, and red italic instructions are preserved. Ingredients are bold. A higher-contrast option is available; print uses darker ink and hides navigation.

## Build, check, and preview

Requires Python 3.10+; Node 20+ is used for the interaction tests and optional screenshot tool. Building and testing the website requires no package installation.

```sh
python3 scripts/build.py
python3 scripts/validate.py
node tests/search.test.cjs
python3 scripts/preview.py
```

Open **http://127.0.0.1:8000/recipes/**. The preview deliberately keeps the production `/recipes/` path. Stop it with Ctrl-C. Rebuild after editing source files, then refresh the browser. `_site/` is generated and ignored by Git.

For hosting at the domain root instead, pass `--base-path /` to both build and validation.

## Homepage project-card screenshot

[`images/homepage-card.png`](images/homepage-card.png) is an actual homepage screenshot used by the [central project directory](https://rharriszzz.github.io/). Refresh it whenever the homepage recipe list or layout changes.

To regenerate it from this checkout (Python 3.10+ and Node 20+):

```sh
npm ci
npx playwright install chromium
npm run capture:homepage-card
```

On Linux, use `npx playwright install --with-deps chromium` if browser system libraries are missing. Playwright is only a development dependency for this optional command; the website remains dependency-free.

The script rebuilds and previews the current checkout, then opens `/recipes/` in Chromium at 1280 × 900 and 2× pixel density. After page load and font readiness, it measures text in `main.simple-index` and captures the heading, introduction, and complete recipe list with a 16-pixel inset. This excludes browser chrome, outer margins, and the empty right side. The crop and capture height follow the list as it grows. The browser and preview server close automatically.

Review the regenerated PNG before committing it together with any homepage changes. The directory references this file directly from the Recipes repository; it needs no separate image copy.

## Repository structure

| Path | Purpose |
| --- | --- |
| `recipes/*.json` | One editable source file per recipe |
| `scripts/build.py` | Shared page templates and static generator |
| `static/style.css`, `static/site.js` | Simple index design, recipe formatting, print and contrast controls |
| `static/` | Local images, favicon, and other public assets |
| `archive/fiberwoman/` | Unmodified downloaded recipe HTML and original CSS |
| `archive/local/` | Recipe-only copies from the old local website backups |
| `archive/chatgpt/` | Recovered recipe artifacts and explicitly identified transcriptions |
| `archive/retrieval.json` | Original-site crawl URLs, statuses, links, and SHA-256 hashes |
| `docs/` | Migration inventory, audit, version decisions, and missing-source report |
| `tests/search.test.cjs` | Regression tests for recipe-page contrast/print behavior (historical filename) |
| `.github/workflows/pages.yml` | Build, validate, test, and deploy to Pages |

The generated site is fully static. Its homepage follows the original fiberwoman.com/recipes/recipes.html: a heading, a short introduction, and a compact single-column list of recipe titles, now in larger type. The nine originally active links retain their original order; later and recovered recipes follow, all visible without search or filters. No JavaScript is needed on the homepage. Recipe pages retain their contrasting-color preference and optional print button, and the browser's own Print command always works. No external fonts, libraries, analytics, accounts, or runtime APIs are used.

## Add or edit a recipe

See [the content guide](docs/content-guide.md). Copy a recipe JSON file, choose a unique lowercase hyphenated slug, and keep ingredients and steps interleaved in `blocks`. Write the complete recipe from an actual source. Do not infer missing quantities.

Preserve the original document under `archive/`, record its URL and filename, and set its SHA-256 hash. Photos belong under `static/images/` with meaningful alt text. Only use relevant recovered or owner-supplied photographs.

```sh
python3 scripts/build.py
python3 scripts/validate.py
node tests/search.test.cjs
git add recipes static scripts docs archive
git commit -m "Add or revise a recipe"
git push origin main
```

The GitHub Actions workflow deploys only after the checks pass. Review the run in the repository's **Actions** tab. The existing **Settings → Pages → Build and deployment → Source** is **GitHub Actions**. No DNS or original-site changes are needed. Pull requests build and validate without deploying.

## Migration and future imports

Read [the migration report](docs/migration-report.md), [inventory](docs/migration-inventory.json), [content audit](docs/content-audit.json), and [remaining sources](docs/missing-sources.md).

The CSS is kept formatted for hand editing; tests use fixed fixtures so adding recipes does not require changing test counts. Archival files retain their original bytes and whitespace.

The migration scripts are deliberately separate from the normal build. A production build never fetches the old site or private chats. `scripts/archive_sources.py` recrawls the original recipe directory (including commented-out links), preserving HTML/CSS and recording HTTP failures. It also copies the two known local recipe backups when available on this Mac. Review archival changes before committing them. Do not replace an older archive without preserving its version if the live site has changed.

`scripts/import_legacy.py` converts the known original HTML files. It refuses to overwrite recipe files unless `--overwrite` is explicitly given. `scripts/import_extra.py` records the conversion of the first recovered ChatGPT artifacts and also refuses to overwrite existing files. These are historical import tools, not commands to run each time you edit a recipe. Review every import against its source and extend validation for a new source format.

For new conversational recipes, prefer the latest explicitly approved artifact; retain distinct variations separately, and record approval uncertainty when no approval is visible. Never merge conflicting quantities or methods automatically. Do not publish a whole private ChatGPT export: archive only the authorized recipe material.
