#!/usr/bin/env python3
"""
Process all drawings in data/raw/drawings/ → data/raw/output/

Tuned for pencil/ink drawings on an orange canvas:
  - Higher threshold (55) to cut through the orange firmly
  - Moderate desaturation (0.6) at edges — drawings often have coloured
    marks right to the edge, so we don't want to grey them out too hard
"""

import sys
from pathlib import Path

# Allow importing remove_background from the same scripts/ directory
sys.path.insert(0, str(Path(__file__).parent))
from remove_background import process_folder

ROOT       = Path(__file__).parent.parent
INPUT_DIR  = ROOT / "data" / "raw" / "drawings"
OUTPUT_DIR = ROOT / "data" / "drawings_raw"

process_folder(
    input_dir     = INPUT_DIR,
    output_dir    = OUTPUT_DIR,
    threshold     = 55,
    softness      = 45,
    padding       = 30,
    edge_width    = 5,
    edge_sigma    = 1.5,
    desaturation             = 0.6,
    white_balance_percentile = 97.0,
    prefix                   = 'd_',
    output_format            = 'webp',
)
