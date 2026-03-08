#!/usr/bin/env python3
"""
Resize processed drawings and scans preserving relative subject sizes.

Two-pass pipeline:
  Pass 1 — measure the non-transparent content bbox of every drawing in
            drawings_raw/. The bbox size reflects actual subject size:
            a small harvestman has a small bbox, a large stork has a large one.
  Pass 2 — pin the largest bbox to MAX_PX; scale all others proportionally.
            This preserves relative sizes while keeping every image ≤ MAX_PX,
            so the CSS max-width never flattens the size differences.

Scans are resized to exactly match their paired drawing (stretch if needed).
Reading from *_raw/ and writing to final dirs makes this idempotent.

Run order:
    python3 scripts/process_drawings.py   # → data/drawings_raw/
    python3 scripts/process_photos.py     # → data/scans_raw/
    python3 scripts/resize_outputs.py     # → data/drawings/ + data/scans/
"""

import numpy as np
from pathlib import Path
from PIL import Image

ROOT             = Path(__file__).parent.parent
DRAWINGS_SRC_DIR = ROOT / "data" / "drawings_raw"
DRAWINGS_OUT_DIR = ROOT / "data" / "drawings"
SCANS_SRC_DIR    = ROOT / "data" / "scans_raw"
SCANS_OUT_DIR    = ROOT / "data" / "scans"

MAX_PX = 750   # longest side of the largest subject in the final output


def content_bbox_longest(img: Image.Image) -> int:
    """Longest side of the non-transparent content bounding box."""
    if img.mode != 'RGBA':
        return max(img.size)
    alpha = np.array(img)[:, :, 3]
    rows = np.where(alpha.any(axis=1))[0]
    cols = np.where(alpha.any(axis=0))[0]
    if len(rows) == 0 or len(cols) == 0:
        return max(img.size)
    return max(int(rows[-1] - rows[0] + 1), int(cols[-1] - cols[0] + 1))


def resize_longest(img: Image.Image, longest: int) -> Image.Image:
    """Scale img so its longest side equals `longest`, preserving aspect ratio."""
    w, h = img.size
    scale = longest / max(w, h)
    return img.resize((round(w * scale), round(h * scale)), Image.LANCZOS)


def main():
    if not DRAWINGS_SRC_DIR.exists():
        print(f"ERROR: {DRAWINGS_SRC_DIR} not found.")
        print("Run process_drawings.py first.")
        return
    if not SCANS_SRC_DIR.exists():
        print(f"ERROR: {SCANS_SRC_DIR} not found.")
        print("Run process_photos.py first.")
        return

    DRAWINGS_OUT_DIR.mkdir(parents=True, exist_ok=True)
    SCANS_OUT_DIR.mkdir(parents=True, exist_ok=True)

    drawings = sorted(DRAWINGS_SRC_DIR.glob("d_*.webp"))
    print(f"Found {len(drawings)} drawings in {DRAWINGS_SRC_DIR.name}/\n")

    # Pass 1 — measure content bboxes
    bbox_map: dict[Path, int] = {}
    for drawing in drawings:
        try:
            with Image.open(drawing) as d_img:
                bbox_map[drawing] = content_bbox_longest(d_img)
        except Exception:
            pass

    max_bbox = max(bbox_map.values()) if bbox_map else 1
    min_bbox = min(bbox_map.values()) if bbox_map else 1
    print(f"Content bbox range: {min_bbox}–{max_bbox} px")
    print(f"Output range:       {round(min_bbox/max_bbox*MAX_PX)}–{MAX_PX} px\n")

    resized = skipped = missing = corrupt = 0

    # Pass 2 — resize proportionally
    for drawing in drawings:
        if drawing not in bbox_map:
            continue
        stem = drawing.stem[2:]   # strip "d_" prefix
        scan = SCANS_SRC_DIR / f"s_{stem}.webp"

        if not scan.exists():
            print(f"  MISSING  scan: s_{stem}.webp")
            missing += 1
            continue

        try:
            with Image.open(drawing) as d_img:
                bbox   = bbox_map[drawing]
                d_orig = d_img.size
                target_longest = round(bbox / max_bbox * MAX_PX)
                d_out  = resize_longest(d_img.copy(), target_longest)
        except Exception as e:
            print(f"  CORRUPT  {drawing.name}: {e}")
            corrupt += 1
            continue

        target_w, target_h = d_out.size

        with Image.open(scan) as s_img:
            s_orig = s_img.size
            s_out  = s_img.resize((target_w, target_h), Image.LANCZOS)

        d_out.save(DRAWINGS_OUT_DIR / drawing.name, 'WEBP', quality=88)
        print(f"  {stem}  [drawing]  {d_orig[0]}×{d_orig[1]} → {d_out.size[0]}×{d_out.size[1]}"
              f"  (bbox={bbox}/{max_bbox} × {MAX_PX} = {target_longest})")
        resized += 1

        s_out.save(SCANS_OUT_DIR / scan.name, 'WEBP', quality=88)
        stretch = (s_orig[0] / target_w, s_orig[1] / target_h)
        note = f"  (stretch {stretch[0]:.2f}×{stretch[1]:.2f})" if abs(stretch[0] - stretch[1]) > 0.01 else ""
        print(f"  {stem}  [scan]     {s_orig[0]}×{s_orig[1]} → {s_out.size[0]}×{s_out.size[1]}{note}")
        resized += 1

    print(f"\nDone. resized={resized}  skipped={skipped}  corrupt={corrupt}  missing={missing}")


if __name__ == '__main__':
    main()
