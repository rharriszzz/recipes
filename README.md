# Recipes

A small, dependency-free static recipe website, published at **https://rharriszzz.github.io/recipes/**.

Ingredients and instructions stay together in cooking order. The original ivory background, Tahoma/Arial type, brown text, and red italic instructions are preserved. Ingredients are bold. A higher-contrast option is available; print uses darker ink and hides navigation.

## Build, check, and preview

Requires Python 3.10+; Node 20+ is used only for the interaction tests. No package installation is needed.

```sh
python3 scripts/build.py
python3 scripts/validate.py
node tests/search.test.cjs
python3 scripts/preview.py
```

Open **http://127.0.0.1:8000/recipes/**. The preview deliberately keeps the production `/recipes/` path. Stop it with Ctrl-C. Rebuild after editing source files, then refresh the browser. `_site/` is generated and ignored by Git.

For hosting at the domain root instead, pass `--base-path /` to both build and validation.

## Repository structure

| Path | Purpose |
| --- | --- |
| `recipes/*.json` | One editable source file per recipe |
| `scripts/build.py` | Shared page templates and static generator |
| `static/style.css`, `static/site.js` | Responsive/print design and title/category filters |
| `static/` | Local images, favicon, and other public assets |
| `archive/fiberwoman/` | Unmodified downloaded recipe HTML and original CSS |
| `archive/local/` | Recipe-only copies from the old local website backups |
| `archive/chatgpt/` | Recovered recipe artifacts and explicitly identified transcriptions |
| `archive/retrieval.json` | Original-site crawl URLs, statuses, links, and SHA-256 hashes |
| `docs/` | Migration inventory, audit, version decisions, and missing-source report |
| `tests/search.test.cjs` | Tests of the actual browser script with a DOM fixture |
| `.github/workflows/pages.yml` | Build, validate, test, and deploy to Pages |

The generated site is fully static. It uses no external fonts, libraries, analytics, accounts, or runtime APIs. Browsing and recipe content work without JavaScript. Search, category filtering, the contrast preference, and the print button are progressive enhancements; the browser's own Print command always works.

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
