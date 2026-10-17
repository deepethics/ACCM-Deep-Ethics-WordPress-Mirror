# ACCM Deep Ethics WordPress Mirror

WordPress-ready mirror snapshots of selected **ACCM Deep Ethics Project** pages, generated for [deepethics.nl](https://deepethics.nl/) recovery and public continuity.

## Status

**Draft pilot — five pages only.**

The files in `wordpress-export/` are deliberately marked `post_status: draft`. They test Git it Write transport, Markdown conversion, links, front matter, and WordPress rendering without replacing the existing published summaries.

## Source and authority

- Canonical project: https://github.com/deepethics/ACCM-Deep-Ethics-Project
- Public project site: https://deepethics.github.io/ACCM-Deep-Ethics-Project/
- WordPress mirror: https://deepethics.nl/
- Transport folder: `wordpress-export/`
- Manifest: `wordpress-export-manifest.json`

GitHub project pages remain the actively edited source. This repository holds derived WordPress-ready representations and their provenance. Editing a generated export directly can create divergence and should be followed by regeneration or an explicit correction record.

## Pilot files

- About
- For Who?
- 10+1 Baseline
- 16 Anchor Ethics
- Beta Paper V03b

Each pilot file is a bounded Topologetic orientation summary. The later recovery build may add a normalized full-page snapshot beneath that summary so deepethics.nl remains readable when the canonical publication surface is unavailable.

## Intended Git it Write settings for the pilot

- Owner: `deepethics`
- Repository: `ACCM-Deep-Ethics-WordPress-Mirror`
- Branch: `main`
- Folder: `wordpress-export`
- Post type: `page` during the isolated draft pilot
- Author: the designated project administrator
- Content template: `%%content%%`
- First operation: **Pull only changes**

Do not configure automatic webhooks until the manual five-page draft pull has been inspected successfully.

## Publication rule

A completed synchronization is an execution event, not proof that the representation remained faithful. Check titles, status, slugs, links, images, attribution, qualifiers, correction routes, and the Git it Write log after every new transformation path.

## License status

No separate license is installed here. This mirror does not silently change the licensing status of the source project.
