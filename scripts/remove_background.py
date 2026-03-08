#!/usr/bin/env python3
"""
Background removal for scanned photos/drawings on a coloured canvas.

Strategy (mirrors Photoshop's Background Eraser / contiguous Magic Wand):
  1. Sample the canvas colour from all four corners.
  2. Flood-fill from the image border through pixels that are similar to the
     canvas colour.  Only border-connected pixels can become transparent —
     any canvas colour that appears *inside* the photo/drawing is unreachable
     and stays fully opaque.
  3. Apply a soft colour-distance-based alpha to the reachable region so that
     shadows (which are darker versions of the canvas colour) fade out
     gradually rather than being hard-cut.
  4. Crop to the bounding box of non-transparent pixels.

Requires: numpy, Pillow, scipy
  pip install numpy pillow scipy
"""

import argparse
from pathlib import Path

import numpy as np
from PIL import Image


# ---------------------------------------------------------------------------
# Colour helpers
# ---------------------------------------------------------------------------

CORNERS = {
    'top-left':     lambda a, s: a[0:s,       0:s      ],
    'top-right':    lambda a, s: a[0:s,       a.shape[1]-s:],
    'bottom-left':  lambda a, s: a[a.shape[0]-s:, 0:s  ],
    'bottom-right': lambda a, s: a[a.shape[0]-s:, a.shape[1]-s:],
}


def sample_background_color(
    img_array: np.ndarray,
    sample_size: int = 50,
    corner: str = 'all',
) -> np.ndarray:
    """
    Sample canvas colour from one or all four corners.

    corner : 'all' (median of all four — default, robust when any corner may
             be covered by the photo) or one of 'top-left', 'top-right',
             'bottom-left', 'bottom-right' (use when a specific corner is
             always clear canvas, e.g. photos where shade varies per scan).
    """
    h, w = img_array.shape[:2]
    s = min(sample_size, h // 4, w // 4)
    ch = img_array.shape[2]

    if corner == 'all':
        selected = list(CORNERS.values())
    else:
        # Accept a single name or a '+'-joined combination, e.g. 'top-right+bottom-left'
        names = [c.strip() for c in corner.split('+')]
        invalid = [n for n in names if n not in CORNERS]
        if invalid:
            raise ValueError(f"Unknown corner(s) {invalid}. Valid: {list(CORNERS)}")
        selected = [CORNERS[n] for n in names]

    regions = [fn(img_array, s) for fn in selected]

    all_pixels = np.concatenate([r.reshape(-1, ch) for r in regions], axis=0)
    return np.median(all_pixels, axis=0)


def color_distance(img_array: np.ndarray, bg_color: np.ndarray) -> np.ndarray:
    """Per-pixel Euclidean distance from bg_color in RGB space."""
    diff = img_array.astype(np.float32) - bg_color.astype(np.float32)
    return np.sqrt(np.sum(diff ** 2, axis=2))


def soft_alpha_from_distance(
    distance: np.ndarray,
    threshold: float,
    softness: float,
) -> np.ndarray:
    """
    distance < threshold            → alpha 0   (fully transparent)
    threshold < distance < t+soft   → linear ramp (shadow preserved)
    distance > threshold + softness → alpha 255 (fully opaque)
    """
    alpha = np.clip((distance - threshold) / softness, 0.0, 1.0)
    return (alpha * 255).astype(np.uint8)


# ---------------------------------------------------------------------------
# Crop detection
# ---------------------------------------------------------------------------

def find_content_bbox(
    img_array: np.ndarray,
    bg_color: np.ndarray,
    threshold: float,
    tolerance: float = 20,
    content_fraction: float = 0.02,
) -> tuple:
    """
    Find the bounding box of the photo/drawing by scanning rows and columns.

    A row/column is considered "content" if at least `content_fraction` of its
    pixels differ from the canvas colour by more than (threshold + tolerance).
    The default fraction of 0.02 (2 %) detects photos/drawings that occupy as
    little as ~2 % of the canvas width or height, which covers the full range
    of expected scan sizes.  Scanner noise that occasionally pushes a canvas
    pixel over the distance threshold is typically ≪ 1 % of any single row, so
    it is safely below the 2 % bar.

    Returns: (left, top, right, bottom)
    """
    h, w = img_array.shape[:2]
    is_bg = color_distance(img_array, bg_color) < (threshold + tolerance)

    row_bg_fraction = is_bg.mean(axis=1)   # (h,)
    col_bg_fraction = is_bg.mean(axis=0)   # (w,)

    content_rows = np.where(row_bg_fraction < (1.0 - content_fraction))[0]
    content_cols = np.where(col_bg_fraction < (1.0 - content_fraction))[0]

    if len(content_rows) == 0 or len(content_cols) == 0:
        return (0, 0, w, h)

    return (
        int(content_cols.min()),
        int(content_rows.min()),
        int(content_cols.max()) + 1,
        int(content_rows.max()) + 1,
    )


# ---------------------------------------------------------------------------
# Flood-fill
# ---------------------------------------------------------------------------

def border_connected_background(
    img_array: np.ndarray,
    bg_color: np.ndarray,
    flood_threshold: float,
) -> np.ndarray:
    """
    Flood-fill from the image border through pixels whose colour distance
    from bg_color is below flood_threshold.

    Returns a boolean mask (same H×W shape) that is True for every pixel
    reachable from the border — i.e. the connected canvas background.

    Pixels *not* in this mask will never be made transparent, regardless
    of their colour.  This is what protects orange/canvas-coloured areas
    that appear inside the photo.

    Uses 4-connectivity (up/down/left/right) to match Photoshop behaviour.
    Requires scipy.
    """
    try:
        from scipy.ndimage import label
    except ImportError:
        raise ImportError(
            "scipy is required for flood-fill background detection.\n"
            "Install with:  pip install scipy"
        )

    is_bg = color_distance(img_array, bg_color) < flood_threshold

    # 8-connected structure — catches canvas pixels only reachable diagonally
    structure = np.ones((3, 3), dtype=int)

    labeled, _ = label(is_bg, structure=structure)

    # Collect component IDs that touch any of the four image edges
    border_labels: set = set()
    border_labels.update(labeled[0,  :].tolist())   # top row
    border_labels.update(labeled[-1, :].tolist())   # bottom row
    border_labels.update(labeled[:,  0].tolist())   # left col
    border_labels.update(labeled[:, -1].tolist())   # right col
    border_labels.discard(0)                        # 0 = non-background label

    if not border_labels:
        return np.zeros(is_bg.shape, dtype=bool)

    return np.isin(labeled, list(border_labels))


# ---------------------------------------------------------------------------
# Edge softening
# ---------------------------------------------------------------------------

def apply_edge_softening(
    img_array: np.ndarray,
    alpha: np.ndarray,
    photo_mask: np.ndarray,
    edge_width: int = 5,
    sigma: float = 1.5,
    desaturation: float = 1.0,
) -> tuple:
    """
    Two effects applied within `edge_width` pixels of the photo boundary:

    1. Desaturation – pixels are blended toward greyscale proportionally to
       their proximity to the edge.  `desaturation` controls the maximum
       strength at the very edge:
         1.0 → fully greyscale at the boundary  (strongest, good for photos)
         0.5 → 50 % grey at the boundary        (moderate, good for drawings)
         0.0 → no desaturation at all

    2. Alpha blur – a Gaussian blur (radius `sigma`) is applied to the alpha
       channel in the transition zone, removing jagged/pixelated edges.
       Deep interior pixels are kept at 255.

    photo_mask : boolean array — True where pixels belong to the photo
                 (i.e. ~bg_mask from the flood fill).
    """
    from scipy.ndimage import binary_closing, distance_transform_edt, gaussian_filter, label

    # Keep only the largest connected component of photo_mask.
    # Small isolated islands (enclosed dust specks, scanner noise that the
    # border flood-fill couldn't reach) would otherwise each produce their own
    # distance-transform edge zone, resulting in multiple visible edge rectangles.
    struct8 = np.ones((3, 3), dtype=int)
    labeled, n_comp = label(photo_mask, structure=struct8)
    if n_comp > 1:
        sizes = np.bincount(labeled.ravel())
        sizes[0] = 0                          # ignore the background label
        photo_mask = labeled == sizes.argmax()

    # Smooth the photo/canvas boundary before computing the distance transform.
    # The flood-fill boundary is pixel-jagged; without smoothing, the edge zone
    # follows every concavity and extends unevenly into the photo interior.
    # binary_closing fills small gaps and rounds concave corners so the
    # resulting edge zone is uniform all the way around.
    smooth_struct = np.ones((3, 3), dtype=bool)
    smooth_mask = binary_closing(photo_mask, structure=smooth_struct, iterations=3)

    # Distance of each photo pixel from the nearest canvas pixel (in pixels)
    interior_dist = distance_transform_edt(smooth_mask)

    # --- 1. Desaturate near the edge ---
    edge_zone = (interior_dist > 0) & (interior_dist <= edge_width)
    if edge_zone.any() and desaturation > 0:
        # blend: 0 right at the boundary → 1 at edge_width
        blend = np.zeros_like(interior_dist, dtype=np.float32)
        blend[edge_zone] = (interior_dist[edge_zone] / edge_width).astype(np.float32)

        img_float = img_array.astype(np.float32)
        luminance = (  0.299 * img_float[:, :, 0]
                     + 0.587 * img_float[:, :, 1]
                     + 0.114 * img_float[:, :, 2])

        # sat: how much of the original colour to keep
        # At boundary (blend=0): sat = 1 - desaturation
        # At edge_width (blend=1): sat = 1.0 (always full colour)
        sat = 1.0 - desaturation * (1.0 - blend)
        for c in range(img_float.shape[2]):
            img_float[:, :, c] = np.where(
                edge_zone,
                sat * img_float[:, :, c] + (1.0 - sat) * luminance,
                img_float[:, :, c],
            )
        img_array = np.clip(img_float, 0, 255).astype(np.uint8)

    # --- 2. Blur alpha at the boundary ---
    alpha_blurred = gaussian_filter(alpha.astype(np.float32), sigma=sigma)
    deep_interior = interior_dist > edge_width
    outside_photo = interior_dist == 0   # outside the smooth_mask boundary
    # Three zones:
    #   deep interior  → always 255 (fully opaque photo content)
    #   outside photo  → keep original alpha (blur must not bleed onto canvas)
    #   transition zone → smoothed alpha
    alpha_out = np.where(
        deep_interior, np.uint8(255),
        np.where(outside_photo, alpha,
                 np.clip(alpha_blurred, 0, 255).astype(np.uint8)),
    ).astype(np.uint8)

    return img_array, alpha_out


# ---------------------------------------------------------------------------
# Main processing
# ---------------------------------------------------------------------------

def remove_background(
    input_path: Path,
    output_path: Path,
    threshold: float = 30,
    softness: float = 40,
    sample_size: int = 50,
    padding: int = 0,
    edge_width: int = 5,
    edge_sigma: float = 1.5,
    desaturation: float = 1.0,
    shadow_desaturation: float = 0.0,
    protect_inset: int = 0,
    corner: str = 'all',
) -> None:
    """
    Remove canvas background from a scanned photo/drawing and crop to content.

    Parameters
    ----------
    threshold : float
        Colour distance below which a pixel is fully transparent (default 30).
    softness : float
        Width of the soft transition / shadow-gradient zone (default 40).
    sample_size : int
        Corner region size for canvas colour sampling (default 50).
    padding : int
        Extra pixels to keep around the crop (default 0).
    edge_width : int
        Pixels inward from the photo boundary for desaturation + alpha blur
        (default 5).  Set to 0 to disable.
    edge_sigma : float
        Gaussian blur radius for alpha smoothing at the boundary (default 1.5).
    desaturation : float
        Desaturation strength at the photo edge interior: 1.0=fully grey,
        0.0=no change (default 1.0).
    shadow_desaturation : float
        Desaturation of the semi-transparent shadow/transition zone (the
        canvas-side pixels that couldn't be fully removed).  1.0=fully grey,
        0.0=no change (default 0.0).  Use 1.0 for photos where canvas colour
        bleeds into the shadow and cannot be removed.
    protect_inset : int
        Pixels inward from the detected photo rectangle that are forced fully
        opaque regardless of flood-fill result (default 0 = disabled).
        Increase when the flood fill bleeds into photo content that is
        colour-adjacent to the canvas (e.g. an orange face near the edge).
        The strip within this inset of the photo boundary is still left to
        the flood fill so shadow effects work at the true photo edge.
    """
    img = Image.open(input_path).convert('RGB')
    img_array = np.array(img)
    h, w = img_array.shape[:2]

    # 1. Identify canvas colour
    bg_color = sample_background_color(img_array, sample_size, corner=corner)
    print(f"  Canvas colour : RGB({bg_color[0]:.0f}, {bg_color[1]:.0f}, {bg_color[2]:.0f})")

    # 2. Colour distance map
    distance = color_distance(img_array, bg_color)

    # 3. Flood-fill border-connected background.
    #    Done before bbox detection so the bbox can be derived from the flood-fill
    #    result, which is the most accurate separation of canvas from content.
    flood_threshold = threshold + softness
    bg_mask = border_connected_background(img_array, bg_color, flood_threshold)
    pct = 100.0 * bg_mask.mean()
    print(f"  Connected bg  : {bg_mask.sum():,} px ({pct:.1f}% of image)")

    # 4. Content bounding box — derived from the largest connected component of
    #    ~bg_mask (i.e. the photo/drawing itself).  This handles any photo size,
    #    any degree of slant, and automatically ignores isolated scanner artifacts
    #    on the canvas that row/column fraction scanning would have included.
    from scipy.ndimage import label as _label
    _labeled, _n = _label(~bg_mask, structure=np.ones((3, 3), dtype=int))
    if _n > 0:
        _sizes = np.bincount(_labeled.ravel())
        _sizes[0] = 0
        _main = _labeled == _sizes.argmax()
        _rows = np.where(_main.any(axis=1))[0]
        _cols = np.where(_main.any(axis=0))[0]
        if len(_rows) > 0 and len(_cols) > 0:
            cx_left, cx_top, cx_right, cx_bottom = (
                int(_cols.min()), int(_rows.min()),
                int(_cols.max()) + 1, int(_rows.max()) + 1,
            )
        else:
            cx_left, cx_top, cx_right, cx_bottom = 0, 0, w, h
    else:
        cx_left, cx_top, cx_right, cx_bottom = 0, 0, w, h
    print(f"  Content bbox  : ({cx_left}, {cx_top}) → ({cx_right}, {cx_bottom})")

    # 5. Build alpha
    alpha = soft_alpha_from_distance(distance, threshold, softness)
    alpha = np.where(bg_mask, alpha, np.uint8(255)).astype(np.uint8)

    # 5.5. Protect content interior from flood-fill bleed.
    #      Any pixel more than `protect_inset` pixels inside the detected photo
    #      rectangle is forced fully opaque regardless of what the flood fill
    #      decided.  We also record this as a boolean mask so the desaturation
    #      step can exclude it precisely.
    protected_interior = np.zeros((h, w), dtype=bool)
    if protect_inset > 0:
        pi_top    = cx_top    + protect_inset
        pi_bottom = cx_bottom - protect_inset
        pi_left   = cx_left   + protect_inset
        pi_right  = cx_right  - protect_inset
        if pi_bottom > pi_top and pi_right > pi_left:
            alpha[pi_top:pi_bottom, pi_left:pi_right] = 255
            protected_interior[pi_top:pi_bottom, pi_left:pi_right] = True

    # 5.6. Desaturate the canvas / shadow zone.
    #
    #      The desaturation boundary is derived from two signals OR-ed together:
    #
    #        alpha < 255   – semi-transparent pixels ARE the shadow/transition
    #                        zone.  After protect_inset has forced the deep photo
    #                        interior back to 255, these pixels follow the actual
    #                        slanted/curved scan edge precisely — no rectangular
    #                        assumption, no flood-fill bleed inland.
    #
    #        border_strip  – a narrow strip (sample_size px) at the physical
    #                        image edge catches fully-opaque canvas pixels that
    #                        the flood fill missed (scanner colour variation,
    #                        glare).  Using the physical edge rather than the
    #                        content bbox avoids a straight rectangular artefact
    #                        appearing at the photo boundary when the scan is
    #                        slightly rotated.
    #
    #      protected_interior is always excluded so the deep photo interior can
    #      never be desaturated regardless of flood-fill or alpha anomalies.
    if shadow_desaturation > 0:
        bs = sample_size  # border strip width == corner sampling zone
        border_strip = np.ones((h, w), dtype=bool)
        border_strip[bs:h-bs, bs:w-bs] = False
        desat_zone = (~protected_interior
                      & (border_strip | (alpha < 255))
                      & (alpha > 0))
        if desat_zone.any():
            img_f = img_array.astype(np.float32)
            lum = (0.299 * img_f[:, :, 0]
                 + 0.587 * img_f[:, :, 1]
                 + 0.114 * img_f[:, :, 2])
            for c in range(img_f.shape[2]):
                img_f[:, :, c] = np.where(
                    desat_zone,
                    (1.0 - shadow_desaturation) * img_f[:, :, c]
                    + shadow_desaturation * lum,
                    img_f[:, :, c],
                )
            img_array = np.clip(img_f, 0, 255).astype(np.uint8)

    # 6. Edge softening (desaturate + blur alpha at photo boundary)
    if edge_width > 0:
        # Clip photo mask to the content bbox so that canvas pixels outside
        # the detected photo area are never treated as a photo boundary.
        # This prevents edge/desaturation effects from appearing on the canvas.
        photo_mask_for_edge = ~bg_mask
        photo_mask_for_edge[:cx_top,    :] = False
        photo_mask_for_edge[cx_bottom:, :] = False
        photo_mask_for_edge[:, :cx_left]   = False
        photo_mask_for_edge[:, cx_right:]  = False
        img_array, alpha = apply_edge_softening(
            img_array, alpha, photo_mask_for_edge,
            edge_width=edge_width,
            sigma=edge_sigma,
            desaturation=desaturation,
        )

    # 7. Crop using already-computed content bbox + padding
    left   = max(0, cx_left   - padding)
    top    = max(0, cx_top    - padding)
    right  = min(w, cx_right  + padding)
    bottom = min(h, cx_bottom + padding)

    print(f"  Content area  : ({left}, {top}) → ({right}, {bottom})"
          f"  [{right-left} × {bottom-top} px]")

    result = Image.fromarray(np.dstack([img_array, alpha]), 'RGBA')
    result = result.crop((left, top, right, bottom))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.save(output_path, 'PNG')
    print(f"  Saved: {output_path} ({result.width} × {result.height})")


def process_folder(
    input_dir: Path,
    output_dir: Path,
    threshold: float = 30,
    softness: float = 40,
    sample_size: int = 50,
    padding: int = 0,
    edge_width: int = 5,
    edge_sigma: float = 1.5,
    desaturation: float = 1.0,
    shadow_desaturation: float = 0.0,
    protect_inset: int = 0,
    corner: str = 'all',
) -> None:
    """Process all images in a folder."""
    extensions = {'.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp'}
    images = sorted(f for f in input_dir.iterdir() if f.suffix.lower() in extensions)

    print(f"Found {len(images)} images in {input_dir}")
    print(f"threshold={threshold}  softness={softness}  edge_width={edge_width}  edge_sigma={edge_sigma}")
    print()

    for i, img_path in enumerate(images, 1):
        print(f"[{i}/{len(images)}] {img_path.name}")
        try:
            remove_background(
                img_path,
                output_dir / f"{img_path.stem}.png",
                threshold=threshold,
                softness=softness,
                sample_size=sample_size,
                padding=padding,
                edge_width=edge_width,
                edge_sigma=edge_sigma,
                desaturation=desaturation,
                shadow_desaturation=shadow_desaturation,
                protect_inset=protect_inset,
                corner=corner,
            )
        except Exception as e:
            print(f"  ERROR: {e}")

    print(f"\nDone! Output: {output_dir}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description='Remove canvas background from scanned photos/drawings.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
How it works:
  The script flood-fills from the image border through pixels similar to the
  canvas colour.  Only border-connected pixels can become transparent, so any
  canvas colour inside the photo/drawing is automatically protected.

Examples:
  python remove_background.py scan.jpg output.png
  python remove_background.py data/raw/ data/output/
  python remove_background.py scan.jpg out.png --threshold 40 --softness 60

Tuning guide:
  --threshold    ↑ if canvas colour still shows at edges
                 ↓ if content near the photo border turns transparent
  --softness     ↑ for longer/softer shadow gradients
  --edge-width   pixels inward over which saturation fades and alpha blurs
  --edge-sigma   Gaussian blur radius for alpha smoothing (higher = softer)
  --padding      breathing room around the crop
        """,
    )
    parser.add_argument('input',  type=Path, help='Input image or folder')
    parser.add_argument('output', type=Path, help='Output image (.png) or folder')
    parser.add_argument('--threshold', type=float, default=30,
                        help='Colour distance for full transparency (default: 30)')
    parser.add_argument('--softness', type=float, default=40,
                        help='Soft-edge / shadow-gradient width (default: 40)')
    parser.add_argument('--sample-size', type=int, default=50,
                        help='Corner region size for canvas colour sampling (default: 50)')
    parser.add_argument('--padding', type=int, default=0,
                        help='Extra pixels to keep around the crop (default: 0)')
    parser.add_argument('--edge-width', type=int, default=5,
                        help='Pixels inward from boundary for desaturation + alpha blur (default: 5, 0=off)')
    parser.add_argument('--edge-sigma', type=float, default=1.5,
                        help='Gaussian blur radius for alpha edge smoothing (default: 1.5)')
    parser.add_argument('--desaturation', type=float, default=1.0,
                        help='Desaturation strength at the photo edge interior: 1.0=fully grey, 0.0=no change (default: 1.0)')
    parser.add_argument('--shadow-desaturation', type=float, default=0.0,
                        help='Desaturation of semi-transparent shadow pixels: 1.0=fully grey, 0.0=no change (default: 0.0)')
    parser.add_argument('--protect-inset', type=int, default=0,
                        help='Pixels inside photo rectangle forced opaque to stop flood-fill bleed (default: 0=off)')
    parser.add_argument('--corner', default='all',
                        choices=['all', 'top-left', 'top-right', 'bottom-left', 'bottom-right'],
                        help='Which corner(s) to sample the canvas colour from (default: all)')

    args = parser.parse_args()
    kwargs = dict(
        threshold=args.threshold,
        softness=args.softness,
        sample_size=args.sample_size,
        padding=args.padding,
        edge_width=args.edge_width,
        edge_sigma=args.edge_sigma,
        desaturation=args.desaturation,
        shadow_desaturation=args.shadow_desaturation,
        protect_inset=args.protect_inset,
        corner=args.corner,
    )

    if args.input.is_dir():
        process_folder(args.input, args.output, **kwargs)
    else:
        remove_background(args.input, args.output, **kwargs)


if __name__ == '__main__':
    main()
