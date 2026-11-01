# Recipe content guide

Each `recipes/<slug>.json` is ordinary UTF-8 JSON. Edit it in any text editor; no HTML page editing is needed. Filenames should match the `slug`. The index, categories, count, and pages are generated automatically.

## Metadata

- `schema_version`: currently `1`.
- `slug`: stable lowercase words separated by hyphens. Changing it changes the URL.
- `title`, optional `subtitle`: plain text; omit a subtitle with `null`.
- `categories`, `tags`: lists of strings. Categories appear as filter buttons. Tags are retained for provenance/future expansion; the current search intentionally matches recipe titles.
- `source_url`: the actual original document or conversation URL.
- `attribution`: inline objects `{ "type": "text", "text": "…" }` or `{ "type": "link", "text": "…", "href": "https://…" }`. Preserve wording and attribution near the title.
- `servings`: plain text or `null`; never guess a yield. If it already appears in the attribution, it is not displayed twice.
- `notes`: optional plain-text notes, displayed after the recipe.
- `variations`: optional objects with `title` and a separate `blocks` sequence. Give a variation its own source file instead when quantities/method conflict substantially.
- `photos`: optional objects with `src` relative to `static/`, required `alt`, and optional `caption`.
- `metadata`: `imported` and `revised` dates, `source_file` relative to the repository, `source_sha256`, `origin`, and any version-selection notes. Preserve original filenames and source sections.

Find a source hash with:

```sh
shasum -a 256 archive/path/to/source.html
```

## Interleaved content

`blocks` is a single chronological sequence, not separate ingredient and instruction arrays. Each `line` has one or more typed `parts`. Use `ingredient` for bold quantities/ingredients and `instruction` for red italics. A preparation clause can follow an ingredient on the same line. Example structure only:

```json
[
  {"type":"section","text":"Prepare the vegetables"},
  {"type":"line","parts":[
    {"type":"ingredient","text":"[Exact ingredient quantity from source]"},
    {"type":"instruction","text":", [Preparation from source]"}
  ]},
  {"type":"line","parts":[
    {"type":"instruction","text":"[Exact next instruction from source]"}
  ]},
  {"type":"break"},
  {"type":"note","text":"[Original note or variation]"}
]
```

A `section` becomes a heading. `break` adds a small gap. `note` is plain prose. Normal whitespace is handled by the template; do not add HTML tags or indentation characters. Text is escaped automatically. Unicode fractions and accents are supported. Keep the original unit spellings and quantities.

For a conventional source with separate ingredients and directions, move each ingredient to its first use without changing its wording or amount; preserve instruction order. Keep an explicit conversion record and verify every original ingredient, instruction, and note. Do not split a single ingredient amount between steps unless the source specifies the allocation.

## Validation and intentional revisions

`python3 scripts/validate.py` checks required metadata, archive hashes, ingredient/instruction styling, full rendered content, internal paths, assets, anchors, and known-source fidelity. The original migration comparison ignores whitespace only. It does not autocorrect spelling or units.

For a deliberate recipe revision, preserve the prior source, archive the new approved source, update `metadata.revised`, `source_file`, and its hash, and document the change. The historical fidelity checks for specific migrated recipes should be updated deliberately to recognize the new version; do not simply disable a failing check. Run the build and validation after editing.

Before publishing, inspect a desktop view, a narrow phone view, and print preview. Try a combined category/title search, no-results search, reset, back-to-index link, and a direct category URL. Verify long instructions and section headings remain readable.
