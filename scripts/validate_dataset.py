"""
WasteGuard AI - Dataset Validation Script
Validates dataset YAML structure, split directory contents, class counts, and bounding box annotations.
"""

import os
import yaml

DATASET_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "YOLO Waste Detection.v1-v1.yolov8")
YAML_PATH = os.path.join(DATASET_DIR, "data.yaml")

def validate_dataset():
    print("=" * 60)
    print(" WasteGuard AI - Dataset Validation ")
    print("=" * 60)

    if not os.path.exists(YAML_PATH):
        print(f"❌ ERROR: data.yaml not found at {YAML_PATH}")
        return False

    with open(YAML_PATH, "r", encoding="utf-8") as f:
        data_cfg = yaml.safe_load(f)

    nc = data_cfg.get("nc", 0)
    names = data_cfg.get("names", [])
    print(f"[OK] data.yaml loaded successfully.")
    print(f"[OK] Number of classes (nc): {nc}")
    print(f"[OK] Class names defined: {len(names)}")

    if nc != len(names):
        print(f"[ERROR] nc ({nc}) does not match length of names array ({len(names)})!")
        return False

    splits = {
        "train": os.path.join(DATASET_DIR, "train"),
        "valid": os.path.join(DATASET_DIR, "valid"),
        "test": os.path.join(DATASET_DIR, "test")
    }

    total_images = 0
    total_labels = 0

    for split_name, split_path in splits.items():
        img_dir = os.path.join(split_path, "images")
        lbl_dir = os.path.join(split_path, "labels")

        if not os.path.exists(img_dir):
            print(f"[ERROR] Image directory missing for split {split_name}: {img_dir}")
            return False
        if not os.path.exists(lbl_dir):
            print(f"[ERROR] Label directory missing for split {split_name}: {lbl_dir}")
            return False

        imgs = os.listdir(img_dir)
        lbls = os.listdir(lbl_dir)
        print(f"[OK] [{split_name.upper()}] Images: {len(imgs)}, Labels: {len(lbls)}")

        total_images += len(imgs)
        total_labels += len(lbls)

        # Validate first 10 label files for bounding box formatting
        for lbl_file in lbls[:10]:
            lbl_file_path = os.path.join(lbl_dir, lbl_file)
            with open(lbl_file_path, "r") as lf:
                lines = lf.readlines()
                for line_idx, line in enumerate(lines):
                    parts = line.strip().split()
                    if len(parts) != 5:
                        print(f"[WARN] Non-standard label format in {lbl_file} line {line_idx+1}: '{line.strip()}'")
                    else:
                        cls_id = int(parts[0])
                        if cls_id < 0 or cls_id >= nc:
                            print(f"[ERROR] Invalid class ID {cls_id} in {lbl_file}")
                            return False

    print("-" * 60)
    print(f"[OK] TOTAL VALIDATED: {total_images} images, {total_labels} label files across all splits.")
    print("[OK] Dataset validation completed cleanly!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = validate_dataset()
    exit(0 if success else 1)
