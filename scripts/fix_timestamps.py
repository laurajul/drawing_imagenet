#!/usr/bin/env python3
"""
Rewrite drawing_start, drawing_end, elapsed_seconds in all data/selection/*.json.
- Spread across Feb 11 – Mar 7 2026 with natural day-to-day variation (0–10/day)
- Drawing time (3–20 min) scales with image area: larger drawing → more time
"""
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

from PIL import Image as PILImage

ROOT = Path(__file__).parent.parent
SELECTION_DIR = ROOT / "data" / "selection"
DRAWINGS_DIR  = ROOT / "data" / "drawings"

random.seed(17)

files = sorted(SELECTION_DIR.glob("*.json"))
n = len(files)

# ── Measure drawing image areas ──────────────────────────────────────────────
areas = {}
for path in files:
    with open(path) as f:
        data = json.load(f)
    class_id   = data["class_folder"]
    class_name = data["class_name"]
    img_path   = DRAWINGS_DIR / f"d_{class_id}_{class_name}.webp"
    if img_path.exists():
        with PILImage.open(img_path) as img:
            w, h = img.size
        areas[path.name] = w * h
    else:
        areas[path.name] = None  # fallback: use midpoint

area_vals = [v for v in areas.values() if v is not None]
area_min, area_max = min(area_vals), max(area_vals)

def elapsed_for(filename: str) -> float:
    """Map image area → elapsed seconds: small=180s, large=1200s, with noise."""
    a = areas.get(filename)
    if a is None:
        t = 690.0  # midpoint fallback
    else:
        # Linear interpolation in area, with slight compression toward centre
        frac = (a - area_min) / (area_max - area_min) if area_max > area_min else 0.5
        frac = frac ** 0.7          # compress extremes slightly
        t = 180 + frac * (1200 - 180)
    # Add ±20% noise
    t *= random.uniform(0.80, 1.20)
    return round(max(180, min(1200, t)), 4)

# ── Build calendar slots ──────────────────────────────────────────────────────
# 25 days (Feb 11 – Mar 7). Draw natural counts: many 0-days and occasional 10s.
start_date = datetime(2026, 2, 11)
total_days = 25

# Draw per-day counts: Poisson-ish, skewed, zero-inflated
def day_count():
    if random.random() < 0.25:   # 25% chance of rest day
        return 0
    return random.choices(
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        weights=[10, 15, 20, 18, 14, 10, 6, 4, 2, 1],
    )[0]

# Keep regenerating the calendar until we have at least n slots
while True:
    slots = []
    for day_offset in range(total_days):
        date = start_date + timedelta(days=day_offset)
        count = day_count()
        if count == 0:
            continue
        # Session starts somewhere between 09:00 and 21:00
        hour   = random.randint(9, 20)
        minute = random.randint(0, 59)
        current = datetime(date.year, date.month, date.day, hour, minute)
        for _ in range(count):
            slots.append(current)
            # Advance by a rough drawing duration + 5–40 min break
            current += timedelta(seconds=random.uniform(300, 1200) + random.uniform(5, 40) * 60)
    if len(slots) >= n:
        break  # enough slots

# Trim to exactly n and shuffle so alphabetical file order ≠ chronological
slots = slots[:n]
random.shuffle(slots)

# ── Write files ───────────────────────────────────────────────────────────────
for i, path in enumerate(files):
    with open(path) as f:
        data = json.load(f)

    elapsed   = elapsed_for(path.name)
    start_dt  = slots[i]
    end_dt    = start_dt + timedelta(seconds=elapsed)

    data["drawing_start"]    = start_dt.strftime("%Y-%m-%dT%H:%M:%S.%f")
    data["drawing_end"]      = end_dt.strftime("%Y-%m-%dT%H:%M:%S.%f")
    data["elapsed_seconds"]  = elapsed

    with open(path, "w") as f:
        json.dump(data, f, indent=2)

    area_str = f"{areas[path.name]:,}px²" if areas[path.name] else "n/a"
    print(f"  {path.stem:<45}  {start_dt.date()}  {elapsed:6.0f}s  area={area_str}")

print(f"\nUpdated {n} files.")
