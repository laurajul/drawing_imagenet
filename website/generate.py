#!/usr/bin/env python3
"""
Generate website/index.html from available scan/drawing pairs.

Local dev (run from project root):
    python3 website/generate.py

Deployment build (paths relative to site root, used by CI):
    python3 website/generate.py --deploy
"""

import argparse
import json
import re
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument(
    "--deploy",
    action="store_true",
    help="Emit image paths relative to the site root instead of website/",
)
args = parser.parse_args()

ROOT = Path(__file__).parent.parent
SCANS_DIR = ROOT / "data" / "scans"
DRAWINGS_DIR = ROOT / "data" / "drawings"
SELECTION_DIR = ROOT / "data" / "selection"
OUT = Path(__file__).parent / "index.html"

# Local: index.html lives in website/, images in ../data/
# Deploy: index.html is at site root, images at data/
REL_SCANS = "data/scans" if args.deploy else "../data/scans"
REL_DRAWINGS = "data/drawings" if args.deploy else "../data/drawings"


def find_json(class_id: str, class_name: str) -> dict | None:
    """Search selection/ (and subdirs) for matching json."""
    stem = f"{class_id}_{class_name}"
    for p in SELECTION_DIR.rglob(f"{stem}.json"):
        with open(p) as f:
            return json.load(f)
    return None


def collect_entries() -> list[dict]:
    entries = []
    for scan in sorted(SCANS_DIR.glob("s_*.webp")):
        m = re.match(r"s_(n\d+)_(.+)\.webp", scan.name)
        if not m:
            continue
        class_id, class_name = m.group(1), m.group(2)
        drawing = DRAWINGS_DIR / f"d_{class_id}_{class_name}.webp"
        if not drawing.exists():
            continue
        meta = find_json(class_id, class_name)
        if meta is None:
            continue
        entries.append({
            "class_id": class_id,
            "class_name": class_name,
            "scan": f"{REL_SCANS}/{scan.name}",
            "drawing": f"{REL_DRAWINGS}/{drawing.name}",
            "meta": meta,
        })
    return entries


def format_scan_caption(meta: dict) -> str:
    fields = ["class_folder", "class_name", "original_filename"]
    lines = [f'"{k}": "{meta[k]}"' for k in fields if k in meta]
    return "\n".join(lines)


def format_drawing_caption(meta: dict) -> str:
    lines = []
    for k in ["drawing_start", "drawing_end"]:
        if k in meta:
            lines.append(f'"{k}": "{meta[k]}"')
    if "elapsed_seconds" in meta:
        lines.append(f'"elapsed_seconds": {meta["elapsed_seconds"]}')
    return "\n".join(lines)


def entry_html(e: dict) -> str:
    heading = f"{e['class_id']}_{e['class_name']}"
    scan_cap = format_scan_caption(e["meta"])
    draw_cap = format_drawing_caption(e["meta"])
    alt_scan = f"scan of {e['class_name'].replace('_', ' ')}"
    alt_draw = f"drawing of {e['class_name'].replace('_', ' ')}"
    return f"""
    <section class="entry" id="{heading}">
      <h2>{heading}</h2>
      <div class="entry-grid">
        <div class="entry-col">
          <div class="img-wrap lazy" data-src="{e['scan']}">
            <noscript><img src="{e['scan']}" alt="{alt_scan}" loading="lazy"></noscript>
          </div>
          <pre class="caption">{scan_cap}</pre>
        </div>
        <div class="entry-col">
          <div class="img-wrap lazy" data-src="{e['drawing']}">
            <noscript><img src="{e['drawing']}" alt="{alt_draw}" loading="lazy"></noscript>
          </div>
          <pre class="caption">{draw_cap}</pre>
        </div>
      </div>
    </section>"""


CSS = """\
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --margin: 20%;
  --gap: 2.5rem;
  --mono: 'Courier New', Courier, monospace;
}

body {
  font-family: system-ui, -apple-system, sans-serif;
  color: #111;
  background: #fff;
  font-size: 16px;
  line-height: 1.5;
}

/* ── Header ── */
header {
  padding: 1.25rem var(--margin);
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}

header h1 {
  font-size: 2rem;
  font-weight: 900;
  letter-spacing: -0.02em;
}

nav a {
  margin-left: 1.5rem;
  text-decoration: none;
  color: #111;
  font-size: 0.95rem;
}
nav a:hover { text-decoration: underline; }

/* ── Description block ── */
.description {
  margin: 0 var(--margin) 3rem;
  padding: 1.5rem;
  background: #e4e4e4;
  font-size: 0.9rem;
  color: #555;
  min-height: 7rem;
}

/* ── Entry sections ── */
.entry {
  margin: 0 var(--margin) 4rem;
}

.entry h2 {
  font-size: 1.4rem;
  font-weight: 700;
  margin-bottom: 1.25rem;
  letter-spacing: -0.01em;
}

.entry-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--gap);
}

/* ── Image wrapper with lazy fade-in ── */
.img-wrap {
  background: #d8d8d8;
  min-height: 160px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  margin-bottom: 0.6rem;
}

.img-wrap img {
  width: 100%;
  height: auto;
  display: block;
  opacity: 0;
  transition: opacity 0.4s ease;
}

.img-wrap img.loaded { opacity: 1; }

/* ── Captions ── */
.caption {
  font-family: var(--mono);
  font-size: 0.72rem;
  line-height: 1.6;
  color: #333;
  white-space: pre-wrap;
}
"""

JS = """\
(function () {
  var lazyWraps = document.querySelectorAll('.img-wrap.lazy');

  function load(wrap) {
    var src = wrap.dataset.src;
    if (!src) return;
    var img = document.createElement('img');
    img.alt = wrap.dataset.alt || '';
    img.onload = function () { img.classList.add('loaded'); };
    img.src = src;
    wrap.appendChild(img);
    wrap.classList.remove('lazy');
  }

  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          load(entry.target);
          io.unobserve(entry.target);
        }
      });
    }, { rootMargin: '200px 0px' });

    lazyWraps.forEach(function (w) { io.observe(w); });
  } else {
    // Fallback: load everything immediately
    lazyWraps.forEach(load);
  }
}());
"""


def generate(entries: list[dict]) -> str:
    entries_html = "".join(entry_html(e) for e in entries)
    count = len(entries)
    subtitle = f"{count} drawing{'s' if count != 1 else ''}" if count else "no drawings yet"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Drawing Imagenet</title>
  <style>
{CSS}  </style>
</head>
<body>

<header>
  <h1>Drawing Imagenet</h1>
  <nav>
    <a href="#">home</a>
    <a href="#">about</a>
  </nav>
</header>

<div class="description">
  Project description — style: justified paragraph (Blocksatz)
</div>

<main>{entries_html}
</main>

<script>
{JS}</script>
</body>
</html>
"""


if __name__ == "__main__":
    entries = collect_entries()
    html = generate(entries)
    OUT.write_text(html, encoding="utf-8")
    print(f"Generated {OUT} with {len(entries)} entries.")
    for e in entries:
        print(f"  {e['class_id']}_{e['class_name']}")
