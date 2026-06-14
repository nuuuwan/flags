"""
Every flag in the world, grouped by colour similarity.

Here's how it was made.

Each flag is first converted into a "colour fingerprint" — a long list of numbers
describing its colours, pixel by pixel.

We then apply PCA (Principal Component Analysis) to distil all that colour data down to just two dimensions: the axes along which the flags differ the most from one another.

Each flag is then placed on a map using those two axes. Flags with similar colours and patterns cluster together; flags with very different colour schemes end up far apart.

The positions are slightly adjusted so that no two flags overlap.

PS: June 14th is Flag Day in the USA — the date in 1777 when the first official US flag was adopted.
"""

import os

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
from PIL import Image
from sklearn.decomposition import PCA

FLAGS_DIR = os.path.join(os.path.dirname(__file__), "..", "images", "flags")
ASPECT_RATIO = 16 / 9
THUMB_HEIGHT = 15  # height of each flag thumbnail in pixels
THUMB_WIDTH = round(
    THUMB_HEIGHT * ASPECT_RATIO
)  # max width; flags scale to fit within both
N_GRID_POSITIONS = 2000

VECTOR_SIZE = (16, 9)
OUTPUT_PATH = os.path.join(
    os.path.dirname(__file__), "..", "images", "output", "cluster.png"
)
FIG_W = 24
FIG_SIZE = (FIG_W, round(FIG_W / ASPECT_RATIO, 1))


def build_vector(img_path: str) -> np.ndarray:
    img = Image.open(img_path).convert("RGB").resize(VECTOR_SIZE)
    return np.array(img, dtype=np.float32).flatten() / 255.0


def load_flags(flags_dir: str):
    import hashlib

    codes, vectors, thumbs = [], [], []
    seen_hashes = set()
    for fname in sorted(os.listdir(flags_dir)):
        if not fname.lower().endswith(".png"):
            continue
        path = os.path.join(flags_dir, fname)
        img_hash = hashlib.md5(open(path, "rb").read()).hexdigest()
        if img_hash in seen_hashes:
            continue
        seen_hashes.add(img_hash)
        code = fname[:-4]
        codes.append(code)
        vectors.append(build_vector(path))
        thumb = Image.open(path).convert("RGBA")
        thumb.thumbnail((THUMB_WIDTH, THUMB_HEIGHT), Image.LANCZOS)
        thumbs.append(np.array(thumb))
    return codes, np.array(vectors), thumbs


def assign_to_grid(coords):
    """Assign flags to the nearest available grid position, closest flag first."""
    n_cols = int(np.ceil(np.sqrt(N_GRID_POSITIONS)))
    n_rows = int(np.ceil(N_GRID_POSITIONS / n_cols))

    # All integer grid positions
    gx, gy = np.meshgrid(np.arange(n_cols), np.arange(n_rows))
    grid = np.column_stack(
        [gx.ravel().astype(float), gy.ravel().astype(float)]
    )

    # Normalise PCA coords to the grid's index range
    norm = coords.astype(float).copy()
    norm[:, 0] = (
        (norm[:, 0] - norm[:, 0].min())
        / (norm[:, 0].max() - norm[:, 0].min() + 1e-9)
        * (n_cols - 1)
    )
    norm[:, 1] = (
        (norm[:, 1] - norm[:, 1].min())
        / (norm[:, 1].max() - norm[:, 1].min() + 1e-9)
        * (n_rows - 1)
    )

    # For every (flag, grid slot) pair compute distance, then assign greedily
    # from closest pair to furthest, skipping already-used flags or slots.
    n_flags = len(norm)
    dists = np.linalg.norm(
        norm[:, np.newaxis, :] - grid[np.newaxis, :, :], axis=2
    )  # (n_flags, n_slots)
    pairs = np.array(
        np.unravel_index(np.argsort(dists, axis=None), dists.shape)
    ).T  # sorted (flag, slot)

    assigned_flags = set()
    assigned_slots = set()
    result = np.empty_like(norm)
    for flag_idx, slot_idx in pairs:
        if flag_idx in assigned_flags or slot_idx in assigned_slots:
            continue
        result[flag_idx] = grid[slot_idx]
        assigned_flags.add(flag_idx)
        assigned_slots.add(slot_idx)
        if len(assigned_flags) == n_flags:
            break
    return result


def render(codes, coords, thumbs, output_path: str):
    fig, ax = plt.subplots(figsize=FIG_SIZE)
    ax.set_facecolor("#f8f8f8")
    fig.patch.set_facecolor("#f8f8f8")

    for code, (x, y), thumb in zip(codes, coords, thumbs):
        img_box = OffsetImage(thumb, zoom=1.0)
        ab = AnnotationBbox(img_box, (x, y), frameon=False)
        ax.add_artist(ab)

    margin = 0.5  # half a grid cell of padding on each side
    ax.set_xlim(coords[:, 0].min() - margin, coords[:, 0].max() + margin)
    ax.set_ylim(coords[:, 1].min() - margin, coords[:, 1].max() + margin)
    ax.axis("off")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_path, dpi=450, bbox_inches="tight")
    print(f"Saved: {output_path}")
    plt.close()
    os.system("open " + output_path)


def main():
    print("Loading flags...")
    codes, vectors, thumbs = load_flags(FLAGS_DIR)
    print(f"Loaded {len(codes)} flags.")

    print("Running PCA...")
    pca = PCA(n_components=2, random_state=42)
    coords = pca.fit_transform(vectors)
    print(f"Explained variance: {pca.explained_variance_ratio_}")

    print("Assigning flags to grid...")
    coords = assign_to_grid(coords)

    print("Rendering plot...")
    render(codes, coords, thumbs, OUTPUT_PATH)


if __name__ == "__main__":
    main()
