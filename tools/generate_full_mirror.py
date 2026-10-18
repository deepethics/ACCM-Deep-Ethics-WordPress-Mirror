#!/usr/bin/env python3
"""Generate full-content Git it Write drafts from the ACCM public-page index.

The canonical project remains authoritative. This script creates a reversible,
draft-only transport layer for WordPress while expanding the small amount of
Jekyll/Liquid syntax that WordPress does not understand.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import html
import json
import re
import shlex
import shutil
import subprocess
from pathlib import Path
from urllib.parse import urlparse

import yaml


SITE = "https://deepethics.github.io/ACCM-Deep-Ethics-Project"
REPO_NAME = "deepethics/ACCM-Deep-Ethics-Project"
FORMAT_BLOCK = re.compile(
    r"\n?<!-- ACCM_FORMAT_LINKS_START -->.*?<!-- ACCM_FORMAT_LINKS_END -->\n?",
    re.S,
)
FRONTMATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?", re.S)
RELATIVE_URL = re.compile(
    r"{{\s*(['\"])(/[^'\"]*)\1\s*\|\s*relative_url\s*}}"
)
INCLUDE = re.compile(r"{%\s*(include|include_relative)\s+(.+?)\s*%}")


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def split_frontmatter(text: str) -> tuple[dict, str]:
    match = FRONTMATTER.match(text)
    if not match:
        return {}, text
    try:
        data = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError:
        data = {}
    return data, text[match.end() :]


def yaml_quote(value: str) -> str:
    return json.dumps(str(value), ensure_ascii=False)


def wordpress_slug(public_url: str, source_path: str, used: set[str]) -> str:
    path = urlparse(public_url).path.strip("/")
    base = path.split("/")[-1].lower() if path else "home"
    if source_path == "index.md":
        base = "home"
    reserved = {
        "about-site.md": "about",
        "for-who.md": "for-who",
        "NETWORK/ten-plus-one.md": "ten-plus-one",
        "NETWORK/16-anchor-ethics.md": "16-anchor-ethics",
        "BETA-PAPER-V3B/index.md": "beta-paper-v3b",
    }
    base = reserved.get(source_path, base)
    slug = base
    if slug in used:
        parts = [p.lower() for p in path.split("/") if p]
        prefix = parts[-2] if len(parts) > 1 else Path(source_path).parent.name.lower()
        slug = f"{prefix}--{base}"
        n = 2
        while slug in used:
            slug = f"{prefix}--{base}-{n}"
            n += 1
    used.add(slug)
    return slug


def render_meta_quotes(text: str, data: dict) -> str:
    groups = data.get("groups", [])
    candidates = data.get("candidates", [])
    text = re.sub(r"{%\s*assign\s+mq\s*=\s*site\.data\.meta_quotes\s*%}\s*", "", text)
    text = re.sub(r"{{\s*mq\.candidates\s*\|\s*size\s*}}", str(len(candidates)), text)
    text = re.sub(
        r"{{\s*mq\.collection_version\s*}}",
        html.escape(str(data.get("collection_version", ""))),
        text,
    )

    nav_pattern = re.compile(
        r"{%\s*for\s+group\s+in\s+mq\.groups\s*%}\s*"
        r"<a href=\"#{{ group\.id }}\">{{ group\.title \| escape }}</a>\s*"
        r"{%\s*endfor\s*%}",
        re.S,
    )
    nav = "\n".join(
        f'<a href="#{html.escape(str(g["id"]))}">{html.escape(str(g["title"]))}</a>'
        for g in groups
    )
    text = nav_pattern.sub(nav, text)

    group_pattern = re.compile(
        r"{%\s*for\s+group\s+in\s+mq\.groups\s*%}\s*"
        r"<section class=\"mq-group\".*?"
        r"{%\s*endfor\s*%}.*?{%\s*endfor\s*%}",
        re.S,
    )
    sections = []
    for group in groups:
        gid = html.escape(str(group["id"]))
        title = html.escape(str(group["title"]))
        cards = []
        for quote in (q for q in candidates if q.get("group") == group.get("id")):
            qid_raw = str(quote["id"])
            qid = html.escape(qid_raw.lower())
            label = html.escape(str(quote.get("label", "")))
            body = html.escape(str(quote.get("text", ""))).replace("\n", "<br>")
            form = html.escape(str(quote.get("form", "")))
            source = html.escape(str(quote.get("source", "")).upper())
            source_anchor = html.escape(str(quote.get("source", "")))
            context = str(quote.get("context", ""))
            context_html = f'<p class="mq-note">{html.escape(context)}</p>' if context else ""
            cards.append(f'''<article class="mq-card" id="{qid}" aria-labelledby="heading-{qid}">
<h3 id="heading-{qid}"><a class="mq-id" href="#{qid}" aria-label="Permanent link to {html.escape(qid_raw)}">{html.escape(qid_raw)}</a>{label}</h3>
<blockquote><p>{body}</p></blockquote>
<p class="mq-credit">— John Kuhles 🦜🦋🌳</p>
<p class="mq-meta">Candidate · {form} · <a href="{SITE}/META-QUOTES/SOURCES/#{source_anchor}">Source {source} and context</a></p>
{context_html}
</article>''')
        sections.append(f'''<section class="mq-group" id="{gid}" aria-labelledby="heading-{gid}">
<h2 id="heading-{gid}">{title}</h2>
{''.join(cards)}
</section>''')
    text, count = group_pattern.subn("\n".join(sections), text, count=1)
    if count != 1:
        raise RuntimeError("Could not render the Meta Quotes group loop")
    return text


class Renderer:
    def __init__(self, source_repo: Path, url_by_source: dict[str, str], image_map: dict[str, str]):
        self.repo = source_repo
        self.url_by_source = url_by_source
        self.image_map = image_map
        self.stack: list[Path] = []

    def render_file(self, path: Path) -> tuple[dict, str]:
        resolved = path.resolve()
        if resolved in self.stack:
            raise RuntimeError(f"Recursive include: {path}")
        self.stack.append(resolved)
        try:
            meta, body = split_frontmatter(path.read_text(encoding="utf-8"))
            body = FORMAT_BLOCK.sub("\n", body)
            if path.relative_to(self.repo).as_posix() == "meta-quotes.md":
                data = yaml.safe_load((self.repo / "_data/meta_quotes.yml").read_text(encoding="utf-8"))
                body = render_meta_quotes(body, data)
            body = self.expand_includes(body, path)
            body = self.expand_liquid(body)
            body = self.rewrite_relative_links(body, path)
            return meta, body.strip() + "\n"
        finally:
            self.stack.pop()

    def expand_includes(self, body: str, current: Path) -> str:
        def replace(match: re.Match) -> str:
            kind, raw = match.group(1), match.group(2)
            parts = shlex.split(raw)
            name = parts[0]
            params = dict(p.split("=", 1) for p in parts[1:] if "=" in p)
            target = (current.parent / name) if kind == "include_relative" else (self.repo / "_includes" / name)
            if name == "youtube-embed.html":
                vid = html.escape(params.get("id", ""), quote=True)
                title = html.escape(params.get("title", "YouTube video"), quote=True)
                caption = params.get("caption")
                cap = f"\n  <figcaption>{html.escape(caption)}</figcaption>" if caption else ""
                return f'''<figure class="accm-video-embed">
  <div class="accm-video-embed__frame">
    <iframe src="https://www.youtube-nocookie.com/embed/{vid}" title="{title}" loading="lazy" referrerpolicy="strict-origin-when-cross-origin" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
  </div>{cap}
</figure>'''
            _, included = self.render_file(target)
            return included.rstrip()

        while INCLUDE.search(body):
            body = INCLUDE.sub(replace, body)
        return body

    def expand_liquid(self, body: str) -> str:
        for source, exported in self.image_map.items():
            pattern = re.compile(r"{{\s*(['\"])" + re.escape(source) + r"\1\s*\|\s*relative_url\s*}}")
            body = pattern.sub(exported, body)
        body = RELATIVE_URL.sub(lambda m: SITE + m.group(2), body)
        body = re.sub(r"{{\s*site\.baseurl\s*}}", "/ACCM-Deep-Ethics-Project", body)
        return body

    def rewrite_relative_links(self, body: str, current: Path) -> str:
        current_rel = current.relative_to(self.repo)

        def rewrite(target: str) -> str:
            if not target or target.startswith(("#", "http://", "https://", "mailto:", "tel:", "data:", "/")):
                return target
            clean, anchor = (target.split("#", 1) + [""])[:2]
            if not clean.lower().endswith(".md"):
                return target
            resolved = self.repo / current_rel.parent / clean
            try:
                normalized = resolved.resolve().relative_to(self.repo.resolve()).as_posix()
            except ValueError:
                return target
            public = self.url_by_source.get(normalized)
            return public + (f"#{anchor}" if anchor else "") if public else target

        body = re.sub(
            r"(\[[^\]]*\]\()([^\s)]+)([^)]*\))",
            lambda m: m.group(1) + rewrite(m.group(2)) + m.group(3),
            body,
        )
        body = re.sub(
            r"((?:href|src)=['\"])([^'\"]+)(['\"])",
            lambda m: m.group(1) + rewrite(m.group(2)) + m.group(3),
            body,
            flags=re.I,
        )
        return body


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_repo", type=Path)
    parser.add_argument("--output-repo", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    source_repo = args.source_repo.resolve()
    output_repo = args.output_repo.resolve()
    export_dir = output_repo / "wordpress-export"
    image_dir = output_repo / "_images"

    with (source_repo / "Deep-Ethical-PDFs/PDF-INDEX.csv").open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) < 100:
        raise RuntimeError(f"Expected the complete public-page index, got {len(rows)} rows")

    url_by_source = {row["source_file"]: row["public_url"] for row in rows}
    image_sources = [
        "/assets/beta/c1-c2/fig-order-c1-before-c2.jpg",
        "/assets/beta/c1-c2/fig-c1-clarifying-question.jpg",
    ]
    image_map = {src: f"/_images/{Path(src).name}" for src in image_sources}
    image_dir.mkdir(exist_ok=True)
    for src in image_sources:
        shutil.copy2(source_repo / src.lstrip("/"), image_dir / Path(src).name)

    renderer = Renderer(source_repo, url_by_source, image_map)
    source_commit = git(source_repo, "rev-parse", "HEAD")
    used: set[str] = set()
    records = []
    generated_names: set[str] = set()

    for order, row in enumerate(rows, start=1):
        source_path = row["source_file"]
        source_file = source_repo / source_path
        source_meta, body = renderer.render_file(source_file)
        slug = wordpress_slug(row["public_url"], source_path, used)
        generated_names.add(f"{slug}.md")
        title = str(source_meta.get("title") or row["title"])
        excerpt = str(source_meta.get("description") or "Full-content WordPress mirror of the canonical ACCM Deep Ethics Project public page.")
        source_blob = git(source_repo, "rev-parse", f"HEAD:{source_path}")
        pdf_url = f"{SITE}/Deep-Ethical-PDFs/{row['pdf_file']}"
        raw_url = f"https://github.com/{REPO_NAME}/blob/main/{source_path}"
        frontmatter = f'''---
title: {yaml_quote(title)}
post_status: draft
post_excerpt: {yaml_quote(excerpt)}
menu_order: {order * 10}
comment_status: closed
custom_fields:
  accm_transformation_type: "full-normalized"
  accm_source_path: {yaml_quote(source_path)}
  accm_source_blob_sha: {yaml_quote(source_blob)}
  accm_source_commit: {yaml_quote(source_commit)}
  accm_canonical_url: {yaml_quote(row["public_url"])}
  accm_pdf_url: {yaml_quote(pdf_url)}
  accm_raw_source_url: {yaml_quote(raw_url)}
---

'''
        output = frontmatter + body
        out_path = export_dir / f"{slug}.md"
        out_path.write_text(output, encoding="utf-8")
        export_blob = subprocess.check_output(["git", "hash-object", str(out_path)], text=True).strip()
        records.append({
            "slug": slug,
            "title": title,
            "source_path": source_path,
            "source_blob_sha": source_blob,
            "export_path": f"wordpress-export/{slug}.md",
            "export_blob_sha": export_blob,
            "canonical_url": row["public_url"],
            "pdf_url": pdf_url,
            "transformation_type": "full-normalized",
            "lifecycle_status": "draft-review-required",
            "wordpress_status": "draft",
        })

    for stale in export_dir.glob("*.md"):
        if stale.name not in generated_names:
            stale.unlink()

    manifest = {
        "schema_version": "1.0-full-public-mirror",
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "source_repository": REPO_NAME,
        "source_branch": "main",
        "source_commit": source_commit,
        "export_repository": "deepethics/ACCM-Deep-Ethics-WordPress-Mirror",
        "export_branch": "main",
        "export_folder": "wordpress-export",
        "page_count": len(records),
        "purpose": "Complete full-content Git it Write draft-only mirror for deepethics.nl recovery and public continuity",
        "normalization": [
            "Replace Jekyll front matter with Git it Write draft front matter",
            "Expand Jekyll relative_url expressions",
            "Recursively inline include and include_relative content",
            "Render the Meta Quotes data loop",
            "Retain source, PDF, public HTML, commit, and blob provenance",
        ],
        "items": records,
    }
    (output_repo / "wordpress-export-manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"Generated {len(records)} full-content draft pages at source commit {source_commit}")


if __name__ == "__main__":
    main()
