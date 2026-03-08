#!/usr/bin/env python3
"""
Process all photos in data/raw/photos/ → data/raw/output/

Tuned for photographic prints on an orange canvas:
  - Higher threshold (50) so orange-tinted areas inside the photo are not deleted
  - shadow_desaturation=1.0 converts the semi-transparent shadow zone to greyscale,
    eliminating orange bleed-through that cannot be removed by alpha alone
  - Wider edge zone (10 px) with full interior desaturation for clean edges
  - Stronger alpha blur (sigma 2.0) for a smoother composite edge
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from remove_background import process_folder

ROOT       = Path(__file__).parent.parent
INPUT_DIR  = ROOT / "data" / "raw" / "photos"
OUTPUT_DIR = ROOT / "data" / "scans"

process_folder(
    input_dir          = INPUT_DIR,
    output_dir         = OUTPUT_DIR,
    threshold          = 35,
    softness           = 45,
    padding            = 35,
    edge_width         = 13,
    edge_sigma         = 2.0,
    desaturation       = 0.5,
    shadow_desaturation= 1.0,
    protect_inset      = 50,
    corner             = 'all',
    corner_inset       = 50,
    prefix             = 's_',
    output_format      = 'webp',
)
