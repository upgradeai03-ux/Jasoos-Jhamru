"""
WasteGuard AI - YOLOv8 Custom Training Script
Standalone script to train YOLO model on the verified 13.1k Waste Detection dataset.
DOES NOT run automatically during application launch.
"""

import os
import sys
import yaml
import torch

try:
    from ultralytics import YOLO
    ULTRALYTICS_AVAILABLE = True
except ImportError:
    ULTRALYTICS_AVAILABLE = False


def train_waste_model(
    epochs: int = 10,
    batch_size: int = 8,
    img_size: int = 640,
    model_base: str = "yolov8n.pt",
    output_model_name: str = "wasteguard_yolov8.pt"
):
    print("=" * 60)
    print(" WasteGuard AI - YOLO Model Training Initializer ")
    print("=" * 60)

    if not ULTRALYTICS_AVAILABLE:
        print("[ERROR] Ultralytics is not installed! Run `pip install ultralytics` first.")
        return False

    # 1. Inspect Hardware
    cuda_available = torch.cuda.is_available()
    device = "0" if cuda_available else "cpu"
    print(f"[INFO] Hardware Device Selected: {device} ({'GPU CUDA' if cuda_available else 'CPU Mode'})")

    if not cuda_available:
        print("[WARN] Training on CPU. Setting conservative batch size and epoch limit to avoid high CPU load.")
        batch_size = min(batch_size, 4)

    # 2. Validate Dataset YAML
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dataset_dir = os.path.join(project_root, "YOLO Waste Detection.v1-v1.yolov8")
    yaml_path = os.path.join(dataset_dir, "data.yaml")

    if not os.path.exists(yaml_path):
        print(f"[ERROR] data.yaml not found at: {yaml_path}")
        return False

    with open(yaml_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    nc = cfg.get("nc", 0)
    print(f"[OK] Dataset YAML verified: {nc} classes detected.")

    # 3. Configure Output directories
    models_dir = os.path.join(project_root, "models")
    os.makedirs(models_dir, exist_ok=True)
    target_model_path = os.path.join(models_dir, output_model_name)

    print(f"[INFO] Training parameters:")
    print(f"  - Base Model: {model_base}")
    print(f"  - Epochs: {epochs}")
    print(f"  - Batch Size: {batch_size}")
    print(f"  - Image Resolution: {img_size}")
    print(f"  - Target Saved Model Path: {target_model_path}")
    print("-" * 60)

    # 4. Initialize & Execute Training
    try:
        model = YOLO(model_base)
        print("[INFO] Starting YOLOv8 training execution...")

        results = model.train(
            data=yaml_path,
            epochs=epochs,
            batch=batch_size,
            imgsz=img_size,
            device=device,
            project=os.path.join(project_root, "runs"),
            name="wasteguard_train",
            exist_ok=True
        )

        # Copy best model weights to models/ directory
        best_weights = os.path.join(project_root, "runs", "wasteguard_train", "weights", "best.pt")
        if os.path.exists(best_weights):
            import shutil
            shutil.copy(best_weights, target_model_path)
            print(f"[OK] Training successful! Trained weights saved to: {target_model_path}")
            return True
        else:
            print("[WARN] Training completed, but best.pt weights file was not found in output run.")
            return False

    except Exception as e:
        print(f"[ERROR] Model training failed: {str(e)}")
        return False


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Train WasteGuard AI YOLO Model")
    parser.add_argument("--epochs", type=int, default=5, help="Number of training epochs")
    parser.add_argument("--batch", type=int, default=4, help="Batch size")
    parser.add_argument("--imgsz", type=int, default=640, help="Image size")
    args = parser.parse_args()

    success = train_waste_model(epochs=args.epochs, batch_size=args.batch, img_size=args.imgsz)
    sys.exit(0 if success else 1)
