# Quality assurance

## Completed before publication

- **Original migration coverage:** all 11 filenames discovered from active and commented index links map to archived sources and recipe JSON. Waffles' 404 is resolved by two matching local copies.
- **Content fidelity:** the independent audit compares every original recipe's full text, ingredient quantities, and instruction order, ignoring whitespace only. It checks the generated recipe text and semantic bold/italic fragment counts again. Additional HTML, conversation-transcription, and PDF-extraction checks cover the recovered ChatGPT recipes. See `content-audit.json`.
- **Fractions and characters:** originals retain their literal fraction notation and spelling; the newer sources retain Unicode fractions and punctuation. UTF-8 metadata is generated on every page. The PDF sources were visually inspected in their Library viewers; the final fish PDF was also independently rendered and inspected.
- **Local HTTP verification:** all **53 generated page/asset/source paths** return HTTP 200 and match the built bytes. See `local-http-verification.json`. This includes recipe pages, legacy `.html` aliases, CSS, JavaScript, favicon, and the source archives linked from recipe pages.
- **Search/category logic:** the shipped JavaScript passes tests for case-insensitive title matching, category intersections, query-string initialization, invalid categories, empty results, reset behavior, and blocked local storage. Tests use fixed title/category fixtures so future recipe additions need no test changes. The source audit independently covers all 16 final recipes. No external service is involved.
- **Desktop browser:** the index was visually inspected in Chrome. Its title search returned the expected three chowders in the initial 15-entry version, and the Seafood intersection returned the expected two. The final 16-entry content is covered by the source and HTTP audits; the shipped search script also passes its fixed-fixture tests.
- **Markup/navigation:** every generated page has an English language attribute, viewport metadata, one primary heading, and a content skip link. Internal links, fragments, and asset paths validate under `/recipes/`. No source recipe images were discovered, so no recovered-photo load checks are applicable.

## Visual verification limits

Chrome native automation later stopped exposing a usable window (`cgWindowNotFound`); the browser-access host was also unavailable. Reconnecting and attempting to restore a Chrome window did not recover it. Safari access was not available to this session. This was not worked around with another browser-control mechanism.

Consequently, **final rendered individual recipe pages, phone-width/browser emulation, and print-preview appearance remain unverified**. Responsive and print CSS are implemented, and their content/navigation paths pass automated checks, but these are not represented as completed visual browser tests. In particular, the long multi-section bibimbap and enchilada pages should receive phone and print-preview review when the browser connection is restored. Physical iPhone/Android testing was not performed.

## Production verification

The supported Pages workflow runs build, full source/link validation, and interaction tests before deploying. After deployment, run:

```sh
python3 scripts/verify_site.py https://rharriszzz.github.io/recipes/ --revision COMMIT_SHA
```

This retrieves every generated page and linked local resource, requires HTTP 200, compares each response byte-for-byte with the built artifact, and verifies the recipe count, base path, and deployed Git revision. External historical attribution sites are preserved but not asserted to be available.

The first deployment succeeded in [GitHub Actions run 41332656522](https://github.com/rharriszzz/recipes/actions/runs/41332656522). All 53 production paths matched commit `1cbe8092348dc595eb7fb7489042b0b9bbd9177c`; the response count, base path, and revision also matched. The actual production verification is recorded in [production-verification.json](production-verification.json). A later documentation-only commit can have a newer SHA than that historical verification record; the final deployment must also be verified against its own SHA.
