# ACCM Deep Ethics WordPress Mirror

WordPress-ready full-content mirror snapshots of selected **ACCM Deep Ethics Project** pages, generated for [deepethics.nl](https://deepethics.nl/) recovery and public continuity.

## Status

**Complete public-page draft mirror — 136 full-content pages.**

Every file in `wordpress-export/` is marked `post_status: draft`. The mirror covers every public page listed in the canonical project's PDF index while keeping WordPress publication a separate, reviewable decision.

## Source and authority

- Canonical project: https://github.com/deepethics/ACCM-Deep-Ethics-Project
- Public project site: https://deepethics.github.io/ACCM-Deep-Ethics-Project/
- WordPress mirror: https://deepethics.nl/
- Transport folder: `wordpress-export/`
- Manifest: `wordpress-export-manifest.json`

The ACCM Deep Ethics Project repository remains the actively edited canonical source. This repository holds complete, WordPress-ready snapshots with source provenance. Editing an export directly can create divergence and should be followed by regeneration or an explicit correction record.

## Export coverage

The manifest records 136 source-to-export mappings, including canonical HTML, PDF, raw-source, source-commit, and Git-blob provenance. The five original pilot slugs remain stable so Git it Write updates those drafts rather than creating duplicates.

Each export carries the complete source-page body. Jekyll front matter is replaced with Git it Write front matter, Jekyll `relative_url` expressions are expanded, included source files are recursively inlined, the Meta Quotes data loop is rendered, and source provenance is retained. The two local C1/C2 illustrations are copied into `_images/` for Git it Write image import.

These are **full normalized mirrors**, not summaries.

## Git it Write settings

- Owner: `deepethics`
- Repository: `ACCM-Deep-Ethics-WordPress-Mirror`
- Branch: `main`
- Folder: `wordpress-export`
- Post type: `page`
- Author: the designated project administrator
- Content template: `%%content%%`
- Update operation: **Pull only changes**

Automatic webhooks remain disabled. Use **Pull only changes** for controlled draft synchronization. Do not use **Pull all files** during routine updates.

## Regeneration

From a checkout of this mirror repository, with the canonical repository available locally:

```bash
python3 tools/generate_full_mirror.py /path/to/ACCM-Deep-Ethics-Project
```

The generator treats the canonical PDF index as the public-page inventory. It removes stale export files, regenerates every draft, and refreshes `wordpress-export-manifest.json`.

## Publication rule

A completed synchronization is an execution event, not proof that the representation remained faithful. Check titles, status, slugs, complete-section survival, links, images, attribution, qualifiers, correction routes, and the Git it Write log after every new transformation path.

## License status

No separate license is installed here. This mirror does not silently change the licensing status of the source project.
