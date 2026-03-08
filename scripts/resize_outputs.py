#!/usr/bin/env python3
"""
Resize processed drawings and scans so pairs are pixel-identical in size,
while preserving relative subject sizes.

Pipeline per class:
  1. Measure the drawing's content bounding box (non-transparent pixels).
  2. Resize the drawing so its content bbox longest side × SCALE,
     preserving the drawing's own aspect ratio.
  3. Resize the scan to exactly match the drawing's final dimensions,
     stretching/squeezing as needed so the pair is consistent.
     ("Scans follow drawings.")

Example: SCALE=1.3, drawing content bbox longest side = 80 px
  → target longest = 104 px
  drawing 95×110  → 90×104   (AR preserved)
  scan    130×80  → 90×104   (squeezed/stretched to match drawing exactly)
"""

import numpy as np
from pathlib import Path
from PIL import Image

ROOT         = Path(__file__).parent.parent
DRAWINGS_DIR = ROOT / "data" / "drawings"
SCANS_DIR    = ROOT / "data" / "scans"

SCALE = 1.3


def content_bbox_longest(img: Image.Image) -> int:
    """Return the longest side of the non-transparent content bounding box."""
    if img.mode != 'RGBA':
        # No alpha channel — treat entire image as content
        return max(img.size)
    alpha = np.array(img)[:, :, 3]
    rows = np.where(alpha.any(axis=1))[0]
    cols = np.where(alpha.any(axis=0))[0]
    if len(rows) == 0 or len(cols) == 0:
        return max(img.size)
    bbox_h = int(rows[-1] - rows[0] + 1)
    bbox_w = int(cols[-1] - cols[0] + 1)
    return max(bbox_w, bbox_h)


def resize_longest(img: Image.Image, longest: int) -> Image.Image:
    """Scale img so its longest side equals `longest`, preserving aspect ratio."""
    w, h = img.size
    scale = longest / max(w, h)
    return img.resize((round(w * scale), round(h * scale)), Image.LANCZOS)


def main():
    drawings = sorted(DRAWINGS_DIR.glob("d_*.webp"))
    print(f"Found {len(drawings)} drawings\n")

    resized = skipped = missing = corrupt = 0

    for drawing in drawings:
        stem = drawing.stem[2:]   # strip "d_" prefix
        scan = SCANS_DIR / f"s_{stem}.webp"

        if not scan.exists():
            print(f"  MISSING  scan: s_{stem}.webp")
            missing += 1
            continue

        try:
            with Image.open(drawing) as d_img:
                bbox_longest = content_bbox_longest(d_img)
                d_orig = d_img.size
                target_longest = round(bbox_longest * SCALE)
                d_out = resize_longest(d_img.copy(), target_longest)
        except Exception as e:
            print(f"  CORRUPT  {drawing.name}: {e}")
            corrupt += 1
            continue

        target_w, target_h = d_out.size

        with Image.open(scan) as s_img:
            s_orig = s_img.size
            s_out  = s_img.resize((target_w, target_h), Image.LANCZOS)

        # Save drawing
        if d_out.size != d_orig:
            d_out.save(drawing, 'WEBP', quality=88)
            print(f"  {stem}  [drawing]  {d_orig[0]}×{d_orig[1]} → {d_out.size[0]}×{d_out.size[1]}"
                  f"  (bbox={bbox_longest} × {SCALE} = {target_longest})")
            resized += 1
        else:
            skipped += 1

        # Save scan
        if s_out.size != s_orig:
            s_out.save(scan, 'WEBP', quality=88)
            stretch = (s_orig[0]/target_w, s_orig[1]/target_h)
            note = f"  (stretch {stretch[0]:.2f}×{stretch[1]:.2f})" if stretch[0] != stretch[1] else ""
            print(f"  {stem}  [scan]     {s_orig[0]}×{s_orig[1]} → {s_out.size[0]}×{s_out.size[1]}{note}")
            resized += 1
        else:
            skipped += 1

    print(f"\nDone. resized={resized}  skipped={skipped}  corrupt={corrupt}  missing={missing}")


if __name__ == '__main__':
    main()
