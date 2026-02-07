#!/usr/bin/env python3
"""
Script to display ImageNet images one class at a time for drawing reference.
Tracks which classes have been shown and saves selected images with metadata.
"""

import os
import json
import random
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


# Paths
BASE_DIR = Path(__file__).parent.parent
TRAIN_DIR = BASE_DIR / "data" / "imagenet-mini" / "train"
SELECTION_DIR = BASE_DIR / "data" / "selection"
INDEX_FILE = BASE_DIR / "misc" / "index.txt"
CLASS_INDEX_FILE = BASE_DIR / "data" / "imagenet_class_index.json"


def load_class_index():
    """Load the ImageNet class index mapping."""
    with open(CLASS_INDEX_FILE, "r") as f:
        data = json.load(f)
    # Create mapping from folder name (wnid) to class name
    return {v[0]: v[1] for v in data.values()}


def load_visited_classes():
    """Load the set of already visited class folders."""
    if not INDEX_FILE.exists():
        return set()
    with open(INDEX_FILE, "r") as f:
        return set(line.strip() for line in f if line.strip())


def save_visited_class(class_folder):
    """Append a visited class folder to the index file."""
    with open(INDEX_FILE, "a") as f:
        f.write(f"{class_folder}\n")


def get_next_class(visited):
    """Get the next unvisited class folder."""
    all_classes = sorted(os.listdir(TRAIN_DIR))
    unvisited = [c for c in all_classes if c not in visited]
    if not unvisited:
        return None
    return random.choice(unvisited)


def get_images_in_class(class_folder):
    """Get all images from the class folder."""
    class_path = TRAIN_DIR / class_folder
    images = [f for f in os.listdir(class_path) if f.lower().endswith(('.jpeg', '.jpg', '.png'))]
    return images


def display_image(image_path):
    """Display an image using the system's default image viewer."""
    # Open with default system viewer
    if sys.platform == 'linux':
        subprocess.Popen(['xdg-open', str(image_path)],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL)
    elif sys.platform == 'darwin':  # macOS
        subprocess.Popen(['open', str(image_path)])
    else:  # Windows
        os.startfile(str(image_path))


def save_selection(source_path, class_folder, class_name, original_filename, start_time, end_time):
    """Save the image and metadata to the selection folder."""
    # Create output filename
    ext = Path(original_filename).suffix
    output_basename = f"{class_folder}_{class_name}"
    output_image = SELECTION_DIR / f"{output_basename}{ext}"
    output_json = SELECTION_DIR / f"{output_basename}.json"

    # Copy image
    shutil.copy2(source_path, output_image)

    # Calculate elapsed time
    elapsed_seconds = (end_time - start_time).total_seconds()

    # Create metadata
    metadata = {
        "class_folder": class_folder,
        "class_name": class_name,
        "original_filename": original_filename,
        "drawing_start": start_time.isoformat(),
        "drawing_end": end_time.isoformat(),
        "elapsed_seconds": elapsed_seconds
    }

    # Save metadata
    with open(output_json, "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"Saved: {output_image.name}")
    print(f"Metadata: {output_json.name}")
    print(f"Elapsed time: {elapsed_seconds:.1f} seconds")


def main():
    # Ensure directories exist
    SELECTION_DIR.mkdir(parents=True, exist_ok=True)
    INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Load class index
    class_index = load_class_index()

    while True:
        # Load visited classes
        visited = load_visited_classes()

        # Get next class
        class_folder = get_next_class(visited)
        if class_folder is None:
            print("All classes have been visited!")
            break

        # Get class name from index
        class_name = class_index.get(class_folder, "unknown")

        # Get all images from this class
        all_images = get_images_in_class(class_folder)
        if not all_images:
            print(f"No images found in {class_folder}, skipping...")
            save_visited_class(class_folder)
            continue

        # Track shown images for this class
        shown_images = set()

        # Image selection loop (for skipping within same class)
        class_done = False
        while not class_done:
            # Get an unshown image
            available_images = [img for img in all_images if img not in shown_images]
            if not available_images:
                print("No more images in this class. Moving to next class...")
                save_visited_class(class_folder)
                break

            image_filename = random.choice(available_images)
            shown_images.add(image_filename)
            image_path = TRAIN_DIR / class_folder / image_filename

            # Display info
            print(f"\n{'='*50}")
            print(f"Class folder: {class_folder}")
            print(f"Class name: {class_name}")
            print(f"Image: {image_filename}")
            print(f"Images remaining in class: {len(available_images) - 1}")
            print(f"Classes remaining: {1000 - len(visited) - 1}")
            print(f"{'='*50}")

            # Record start time and display image
            start_time = datetime.now()
            display_image(image_path)

            # Ask if done
            while True:
                response = input("\nDone? (yes/skip/quit): ").strip().lower()
                if response in ['yes', 'y']:
                    end_time = datetime.now()
                    save_selection(image_path, class_folder, class_name, image_filename, start_time, end_time)
                    save_visited_class(class_folder)
                    class_done = True
                    break
                elif response in ['skip', 's']:
                    print("Showing another image from the same class...")
                    break  # Break inner loop, continue outer loop to show next image
                elif response in ['quit', 'q']:
                    print("Exiting...")
                    return
                else:
                    print("Please type 'yes', 'skip', or 'quit'")

        # Ask if continue
        response = input("\nShow next image? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("Exiting...")
            break

    print("\nDone!")


if __name__ == "__main__":
    main()
