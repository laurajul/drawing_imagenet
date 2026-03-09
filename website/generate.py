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

from PIL import Image as PILImage

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
DESCRIPTION_FILE = ROOT / "md" / "description.md"
ABOUT_FILE       = ROOT / "md" / "about.md"
OUT       = Path(__file__).parent / "index.html"
ABOUT_OUT = Path(__file__).parent / "about.html"

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


def img_display_size(path: Path) -> tuple[int, int]:
    with PILImage.open(path) as img:
        return img.size


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
        try:
            sw, sh = img_display_size(scan)
            dw, dh = img_display_size(drawing)
        except Exception as e:
            print(f"  SKIP {class_id}_{class_name}: {e}", flush=True)
            continue
        entries.append({
            "class_id": class_id,
            "class_name": class_name,
            "scan": f"{REL_SCANS}/{scan.name}",
            "drawing": f"{REL_DRAWINGS}/{drawing.name}",
            "scan_w": sw, "scan_h": sh,
            "draw_w": dw, "draw_h": dh,
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
          <div class="img-wrap lazy" data-src="{e['scan']}" data-width="{e['scan_w']}" data-height="{e['scan_h']}">
            <noscript><img src="{e['scan']}" alt="{alt_scan}" width="{e['scan_w']}" height="{e['scan_h']}" loading="lazy"></noscript>
          </div>
          <pre class="caption">{scan_cap}</pre>
        </div>
        <div class="entry-col">
          <div class="img-wrap lazy" data-src="{e['drawing']}" data-width="{e['draw_w']}" data-height="{e['draw_h']}">
            <noscript><img src="{e['drawing']}" alt="{alt_draw}" width="{e['draw_w']}" height="{e['draw_h']}" loading="lazy"></noscript>
          </div>
          <pre class="caption">{draw_cap}</pre>
        </div>
      </div>
    </section>"""


CSS = """\
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --img-width: 90%;
  --text-width: 60%;
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
  width: var(--text-width);
  margin: 0 auto;
  padding: 1.25rem 0;
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
  width: var(--text-width);
  margin: 0 auto 3rem;
  padding: 1.5rem;
  background: #fff;
  font-size: 0.9rem;
  color: #555;
}

.description p {
  margin-bottom: 1em;
  text-align: justify;
}

.description h2 {
  font-size: 0.95rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: #111;
  margin: 2rem 0 0.6rem;
}

.description em {
  font-style: italic;
}

.description .footnotes {
  margin-top: 2.5rem;
  padding-top: 1rem;
  border-top: 1px solid #ddd;
  font-size: 0.75rem;
  color: #888;
  line-height: 1.7;
}

.description sup {
  font-size: 0.65rem;
  vertical-align: super;
  line-height: 0;
}

/* ── About page layout ── */
.about-intro {
  width: var(--text-width);
  margin: 0 auto 3rem;
  padding: 1.5rem;
  font-size: 0.9rem;
  color: #555;
}

.about-intro p {
  margin-bottom: 1em;
  text-align: justify;
}

.about-intro h2 {
  font-size: 0.95rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: #111;
  margin: 2rem 0 0.6rem;
}

.about-intro em { font-style: italic; }

.about-body {
  width: 85%;
  max-width: 1100px;
  margin: 0 auto 3rem;
  padding: 1.5rem;
  font-size: 0.9rem;
  color: #555;
  columns: 2;
  column-gap: 3.5rem;
}

.about-body h2 {
  column-span: all;
  font-size: 0.95rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: #111;
  margin: 2rem 0 0.6rem;
}

.about-body p {
  margin-bottom: 1em;
  text-align: justify;
}

.about-body em { font-style: italic; }

.about-body sup {
  font-size: 0.65rem;
  vertical-align: super;
  line-height: 0;
}

.about-body .footnotes {
  column-span: all;
  margin-top: 2.5rem;
  padding-top: 1rem;
  border-top: 1px solid #ddd;
  font-size: 0.75rem;
  color: #888;
  line-height: 1.7;
}

@media (max-width: 768px) {
  .about-intro,
  .about-body {
    width: 90%;
  }
  .about-body {
    columns: 1;
  }
}

/* ── Entry sections ── */
.entry {
  width: var(--img-width);
  margin: 0 auto 4rem;
}

.entry h2 {
  font-size: 1.4rem;
  font-weight: 700;
  margin-bottom: 1.25rem;
  letter-spacing: -0.01em;
}

.entry-grid {
  display: flex;
  gap: var(--gap);
  align-items: flex-start;
  justify-content: center;
}

@media (max-width: 768px) {
  .entry-grid {
    flex-direction: column;
    align-items: center;
  }
}

/* ── Image wrapper ── */
/* No container sizing — images render at their exact pixel dimensions.
   Small subjects appear small; large subjects appear large. */
.img-wrap {
  display: block;
  margin-bottom: 0.6rem;
}

.img-wrap img {
  display: block;
  max-width: 750px;
  height: auto;
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
  var all = Array.prototype.slice.call(document.querySelectorAll('.img-wrap.lazy'));

  function load(wrap) {
    var src = wrap.dataset.src;
    if (!src) return;
    var img = document.createElement('img');
    img.alt = wrap.dataset.alt || '';
    if (wrap.dataset.width) img.style.width = wrap.dataset.width + 'px';
    img.onload = function () { img.classList.add('loaded'); };
    img.src = src;
    wrap.appendChild(img);
    wrap.classList.remove('lazy');
  }

  // Load first 6 wrappers (≈ 3 entries) immediately — no observer delay.
  var eager = all.slice(0, 6);
  var deferred = all.slice(6);
  eager.forEach(load);

  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          load(entry.target);
          io.unobserve(entry.target);
        }
      });
    }, { rootMargin: '600px 0px' });  // preload 600 px ahead of viewport

    deferred.forEach(function (w) { io.observe(w); });
  } else {
    deferred.forEach(load);
  }
}());
"""


def md_inline(s: str) -> str:
    """Convert inline markdown to HTML: *italic*, [text](url)."""
    s = re.sub(r"\*(.+?)\*", r"<em>\1</em>", s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
    return s


def load_description() -> str:
    if not DESCRIPTION_FILE.exists():
        return ""
    md_text = DESCRIPTION_FILE.read_text(encoding="utf-8")
    blocks = re.split(r"\n{2,}", md_text.strip())
    out = []
    for block in blocks:
        block = block.strip()
        if not block or block == "---":
            continue
        out.append(f"<p>{md_inline(block)}</p>")
    return "\n  ".join(out)


def generate(entries: list[dict]) -> str:
    entries_html = "".join(entry_html(e) for e in entries)
    description_html = load_description()
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
    <a href="index.html">home</a>
    <a href="about.html">about</a>
  </nav>
</header>

<div class="description">
  {description_html}
</div>

<main>{entries_html}
</main>

<script>
{JS}</script>
</body>
</html>
"""


def load_about() -> str:
    """Convert md/about.md to HTML for the about page.

    The ## Abstract section is wrapped in <div class="about-intro">.
    All remaining sections are wrapped in <div class="about-body"> (two-column layout).

    Supported markdown:
      ## Heading       → <h2>
      *italic*         → <em>
      [n]              → <sup>[n]</sup>  (citation markers)
      blank lines      → paragraph breaks
      ## Notes section → wrapped in <div class="footnotes">
    """
    if not ABOUT_FILE.exists():
        return ""
    text = ABOUT_FILE.read_text(encoding="utf-8")

    def inline(s):
        s = re.sub(r"\*(.+?)\*", r"<em>\1</em>", s)
        s = re.sub(r"(?<!\n)\[(\d+)\]", r"<sup>[\1]</sup>", s)
        s = re.sub(r"&(?!amp;|lt;|gt;|#)", "&amp;", s)
        return s

    blocks = re.split(r"\n{2,}", text.strip())
    intro_lines = []
    body_lines = []
    in_abstract = False
    in_body = False
    in_footnotes = False

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        if block.startswith("## "):
            heading = block[3:].strip()
            if heading.lower() == "abstract":
                in_abstract = True
                in_body = False
                intro_lines.append(f"  <h2>{heading}</h2>")
            elif heading.lower() == "notes":
                in_abstract = False
                in_body = True
                body_lines.append('  <div class="footnotes">')
                in_footnotes = True
            else:
                in_abstract = False
                in_body = True
                body_lines.append(f"  <h2>{heading}</h2>")
            continue

        if in_abstract:
            intro_lines.append(f"  <p>{inline(block)}</p>")
        elif in_body:
            if in_footnotes:
                body_lines.append(f"    <p>{inline(block)}</p>")
            else:
                body_lines.append(f"  <p>{inline(block)}</p>")

    if in_footnotes:
        body_lines.append("  </div>")

    intro_html = "\n".join(intro_lines)
    body_html = "\n".join(body_lines)
    return (
        f'<div class="about-intro">\n{intro_html}\n</div>\n\n'
        f'<div class="about-body">\n{body_html}\n</div>\n'
    )


def generate_about() -> str:
    about_html = load_about()
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Drawing Imagenet — About</title>
  <style>
{CSS}  </style>
</head>
<body>

<header>
  <h1>Drawing Imagenet</h1>
  <nav>
    <a href="index.html">home</a>
    <a href="about.html">about</a>
  </nav>
</header>

{about_html}

</body>
</html>
"""


if __name__ == "__main__":
    entries = collect_entries()
    html = generate(entries)
    OUT.write_text(html, encoding="utf-8")
    print(f"Generated {OUT} with {len(entries)} entries.")
    for e in entries:
        print(f"  {e['class_id']}_{e['class_name']}  "
              f"scan={e['scan_w']}×{e['scan_h']}  "
              f"drawing={e['draw_w']}×{e['draw_h']}")

    about_html = generate_about()
    ABOUT_OUT.write_text(about_html, encoding="utf-8")
    print(f"Generated {ABOUT_OUT}.")
