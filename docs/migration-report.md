# Migration report

Migration date: **November 1, 2026**. Destination: **https://rharriszzz.github.io/recipes/**.

## Counts and coverage

| Measure | Count |
| --- | ---: |
| Recipes actively linked by the live original index | 9 |
| Additional recipe filenames in index comments | 2 |
| Total original recipes discovered | **11** |
| Original recipe pages retrieved live | 10 |
| Original recipe recovered from local backup | 1 (Waffles) |
| Original recipes migrated | **11 of 11** |
| Additional complete ChatGPT main recipes migrated | 4 |
| Additional standalone side-dish entry | 1 (Musaengchae, also in bibimbap) |
| Total published recipe entries | **16** |
| Linked recipe photographs or downloadable assets on the old site | 0 |
| Unrecovered original recipe contents | 0 |

The complete URL → archived source → editable JSON → published page mapping is in [migration-inventory.json](migration-inventory.json). The checked ingredient/instruction fragment counts and verification details are in [content-audit.json](content-audit.json).

## Original-site investigation

The `/recipes/` entry is a meta refresh to `recipes.html`. The index, all active recipe links, commented-out recipe links, each recipe's internal links, and the original stylesheet were inspected. No linked recipe subdirectories or secondary recipe indexes were found. The crawler follows internal links inside the recipe directory, including references hidden in HTML comments. Its statuses, links, and content hashes are preserved in [retrieval.json](../archive/retrieval.json).

The root Fiberwoman home page was also inspected; its photographs concern weaving, baskets, and textiles, so they were not substituted for recipe photographs. Recipe pages reference only the shared CSS and navigation, apart from the attribution link in Sausage, Squash, and Posole Soup. That original Emeril URL remains in the attribution; its external destination is historical and may have changed.

Waffles is commented out and its live page returns 404. Its complete HTML was recovered from `xo/web/recipes/waffles.html` and independently matched against the `thornbackup` copy. Both recipe-only backup sets and two older downloaded recipe indexes are archived. The two backup sets are byte-identical. All backup recipes still available live match their live versions byte-for-byte. The index differs: the newer live index includes Enchiladas and Posole Soup, while old index downloads also actively linked the now-commented recipes. See [local-comparison.json](local-comparison.json).

## Additional source/version decisions

- **Fish Chowder / Haddock Chowder:** `haddock_chowder_v3.pdf` and `fish_chowder_final.pdf` have identical content after their titles. One entry uses the final requested title, **Fish Chowder**. Both PDFs are archived. It includes haddock, bacon, and a two-day base/finish method. Earlier haddock PDF filenames appeared in Library search but were not combined with the final artifact.
- **Cod and Potato Chowder:** a distinct, complete October 4 conversation recipe with one pound of cod, six celery stalks, Vidalia onion, and leek. The entire recipe response was inspected. The archive explicitly identifies its plain-text transcription from rendered chat content; it is not misrepresented as an original Markdown export. The larger-liquid option stays in its original notes. No explicit final approval was visible, and this uncertainty is recorded in metadata.
- **Smoked Salmon Potato Chowder:** the actual final PDF was downloaded from Library and imported, preserving its interleaved contents. Earlier filenames were visible; the final artifact was used independently of other chowders.
- **Dolsot Bibimbap for Two:** the actual August 22 HTML and matching PDF were recovered. The HTML preserves every section, ingredient, and instruction, including the oven-heated stone bowls. Its daikon side dish is also made separately browsable as **Musaengchae**; this is an exact section extraction, not another invented version.
- **Chicken with Cabbage and Peanuts:** the recovered Szechuan conversation returns to the same original website recipe. Its initial generic 2023 AI suggestion is not an approved replacement and was not added as a duplicate. No separately approved Kung Pao variation was recovered.

Known missing or only partially inspected conversational material, including Orange Roughy Chowder, is listed in [missing-sources.md](missing-sources.md). No content was inferred from the task's recipe summaries.

## Content and formatting audit

The original body text after each recipe heading was compared independently with attribution plus imported content, ignoring whitespace only. Quantities, units, punctuation, fractions, spelling, order, preparation clauses, notes, and optional ingredients remain unchanged. Generated recipe text is checked again against its JSON source. The HTML and PDF-derived additional recipes have source-specific content checks; the fish PDF conversion checks every source item and the original instruction order.

The original stylesheet specified `#fffff0`, `#993311`, Tahoma/Arial/sans-serif, and red `#ff3333` italics. These defaults remain. Ingredients were ordinary-weight in most original HTML; they are now bold as requested. Italic preparation clauses remain immediately beside their ingredients, and standalone instructions remain indented within the same chronological sequence. Original blank lines become small gaps. Invalid nested/unclosed italics in Potatoes in Green Sauce were repaired semantically without changing any text.

Differences deliberately introduced:

1. **Tuna, Egg, and Potato Salad heading:** the original HTML `<title>` and index correctly name the salad, but its copied `<h3>` says “Potatoes in Green Sauce.” The new heading uses the correct title. The original mismatch is preserved in the archive and `metadata.original_heading`.
2. **Fish PDF interleaving:** its original separate ingredient list was moved beside first use, preserving every ingredient amount and the instruction sequence. No allocation of quantities was invented.
3. Responsive width, readable spacing, semantic headings, keyboard focus, skip navigation, and shared browsing controls were added. Links use `/recipes/` consistently; old `<slug>.html` paths and `recipes.html` also resolve on the new site.
4. The exact bright red defaults are retained. An optional persistent higher-contrast setting darkens instructions. Print uses darker brown/red on white, smaller type, and no browsing controls to conserve paper.
5. Bibimbap's title includes “for Two” for browsing clarity; its original document and source title remain archived. The recipe's quantities are unchanged.

## Owner review items

These do not block publication:

- Confirm the title correction for Tuna, Egg, and Potato Salad.
- Waffles contains the source phrase “mix in 1/2 cup of the flour, then mix in the of the flour.” It is preserved verbatim; supply a deliberate correction if desired.
- Other original spelling errors and unusual quantities, including salt amounts, are preserved. This migration has not silently edited cooking content.
- Cod chowder is a complete recovered response, with approval uncertainty recorded. Confirm it if you want an explicitly approved version marker.
- Supply the remaining approved recipes listed in the missing-source report when convenient.

## Build and publication

The existing local Git repository had no commits or remote. It was connected to the already-existing empty `rharriszzz/recipes` repository; no repository was created. GitHub reported administrator access and Pages already configured with `build_type: workflow` and HTTPS enforced.

The site uses Python's standard library to generate `_site/` from one JSON file per recipe and shared templates. Normal builds have no third-party dependencies or network requests. GitHub Actions builds, validates, tests interactions, uploads the Pages artifact, and deploys `main` through the supported Pages Actions mechanism. Pull requests run build/checks without publishing. No DNS records or Fiberwoman files were changed.

See [qa.md](qa.md) for executed checks, browser-verification limits, and deployment verification. Editing and future-import instructions are in the [README](../README.md) and [content guide](content-guide.md).
