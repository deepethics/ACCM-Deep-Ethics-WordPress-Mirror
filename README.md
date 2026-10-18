# ACCM Deep Ethics WordPress Mirror

WordPress-ready full-content mirror snapshots of selected **ACCM Deep Ethics Project** pages, generated for [deepethics.nl](https://deepethics.nl/) recovery and public continuity.

## Status

**Draft pilot — five complete pages only.**

The files in `wordpress-export/` are marked `post_status: draft`. They test Git it Write transport, Markdown conversion, long-page handling, links, front matter, and WordPress rendering before the mirror expands to the complete public-page set.

## Source and authority

- Canonical project: https://github.com/deepethics/ACCM-Deep-Ethics-Project
- Public project site: https://deepethics.github.io/ACCM-Deep-Ethics-Project/
- WordPress mirror: https://deepethics.nl/
- Transport folder: `wordpress-export/`
- Manifest: `wordpress-export-manifest.json`

The ACCM Deep Ethics Project repository remains the actively edited canonical source. This repository holds complete, WordPress-ready snapshots with source provenance. Editing an export directly can create divergence and should be followed by regeneration or an explicit correction record.

## Pilot files

- About the ACCM Deep Ethics Project
- For who?
- 10+1 Metaflux — Mutual Correction
- 16 Anchor Ethics
- Potential Science Paper Candidate Draft — V03b

Each pilot file carries the complete source-page body. Jekyll front matter is replaced with Git it Write front matter, Jekyll `relative_url` expressions are expanded into public URLs, and source provenance is retained. The About page inlines the complete README that its Jekyll page includes.

These are **full normalized mirrors**, not summaries.

## Intended Git it Write settings for the pilot

- Owner: `deepethics`
- Repository: `ACCM-Deep-Ethics-WordPress-Mirror`
- Branch: `main`
- Folder: `wordpress-export`
- Post type: `page`
- Author: the designated project administrator
- Content template: `%%content%%`
- Update operation: **Pull only changes**

Automatic webhooks remain disabled until the manual five-page draft update has been inspected successfully.

## Publication rule

A completed synchronization is an execution event, not proof that the representation remained faithful. Check titles, status, slugs, complete-section survival, links, images, attribution, qualifiers, correction routes, and the Git it Write log after every new transformation path.

## License status

No separate license is installed here. This mirror does not silently change the licensing status of the source project.
