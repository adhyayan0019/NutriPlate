import os
import shutil
import csv
import matplotlib.pyplot as plt
from ultralytics import YOLO

def generate_training_plots(csv_path, output_dir):
    """
    Parses results.csv and creates publication-grade visual curves for:
    - Top-1 and Top-5 Validation Accuracy across 300 epochs
    - Training vs Validation Cross-Entropy Loss
    """
    if not os.path.exists(csv_path):
        print(f"Warning: results.csv not found at {csv_path}")
        return

    epochs, train_loss, val_loss, top1_acc, top5_acc = [], [], [], [], []

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            clean = {k.strip(): v.strip() for k, v in row.items()}
            try:
                ep = int(clean.get('epoch', 0)) + 1
                t_loss = float(clean.get('train/loss', 0))
                v_loss = float(clean.get('val/loss', 0))
                t1 = float(clean.get('metrics/accuracy_top1', 0)) * 100
                t5 = float(clean.get('metrics/accuracy_top5', 0)) * 100

                epochs.append(ep)
                train_loss.append(t_loss)
                val_loss.append(v_loss)
                top1_acc.append(t1)
                top5_acc.append(t5)
            except Exception:
                continue

    if not epochs:
        return

    os.makedirs(output_dir, exist_ok=True)
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')

    # 1. Accuracy Curve
    plt.figure(figsize=(9, 5), dpi=300)
    plt.plot(epochs, top1_acc, color='#10b981', linewidth=2.5, label=f'Top-1 Accuracy (Best: {max(top1_acc):.2f}%)')
    plt.plot(epochs, top5_acc, color='#3b82f6', linewidth=2.5, linestyle='--', label=f'Top-5 Accuracy (Best: {max(top5_acc):.2f}%)')
    plt.title('NutriPlate-Food35 YOLOv8 Classifier Accuracy (300 Epochs)', fontsize=14, fontweight='bold', pad=12)
    plt.xlabel('Epochs', fontsize=12, fontweight='bold')
    plt.ylabel('Validation Accuracy (%)', fontsize=12, fontweight='bold')
    plt.ylim([0, 105])
    plt.legend(loc='lower right', frameon=True, fontsize=11)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'nutriplate_food35_accuracy_curve.png'))
    plt.close()

    # 2. Loss Curve
    plt.figure(figsize=(9, 5), dpi=300)
    plt.plot(epochs, train_loss, color='#ef4444', linewidth=2.2, label='Train Loss')
    plt.plot(epochs, val_loss, color='#f59e0b', linewidth=2.2, linestyle='--', label='Val Loss')
    plt.title('NutriPlate-Food35 Training & Validation Loss Curve', fontsize=14, fontweight='bold', pad=12)
    plt.xlabel('Epochs', fontsize=12, fontweight='bold')
    plt.ylabel('Cross-Entropy Loss', fontsize=12, fontweight='bold')
    plt.legend(loc='upper right', frameon=True, fontsize=11)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'nutriplate_food35_loss_curve.png'))
    plt.close()

def train_nutriplate_food35_model(
    data_dir=r'c:\Users\ADMIN\Downloads\SEProject\datasets\new_khana_internet',
    epochs=300,
    imgsz=224,
    batch=32,
    device='0', # Use NVIDIA GPU 0
    base_model='yolov8s-cls.pt', # Strong Small architecture (11.2M params)
    project=r'c:\Users\ADMIN\Downloads\SEProject\ai-model\runs',
    name='nutriplate_food35_300_epochs'
):
    import torch
    print("=" * 65)
    print("  LAUNCHING NUTRIPLATE-FOOD35 300-EPOCH TRAINING")
    print(f"  Dataset:      {data_dir}")
    print(f"  Base Model:   {base_model}")
    print(f"  Target Epochs:{epochs}")
    print(f"  Batch Size:   {batch}")
    print(f"  Image Size:   {imgsz}x{imgsz}")
    cuda_available = torch.cuda.is_available()
    print(f"  CUDA Active:  {cuda_available}")
    if cuda_available:
        print(f"  GPU Name:     {torch.cuda.get_device_name(0)}")
        print(f"  GPU VRAM:     {torch.cuda.get_device_properties(0).total_memory / (1024**3):.2f} GB")
        chosen_device = 0
    else:
        print("  Notice: CUDA not active in current env, falling back to CPU.")
        chosen_device = 'cpu'
    print("=" * 65)

    model = YOLO(base_model)

    results = model.train(
        data=data_dir,
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        workers=2,
        device=chosen_device,
        project=project,
        name=name,
        patience=35,           # Early stopping if loss doesn't improve for 35 epochs
        save=True,
        plots=True,
        verbose=True,
        degrees=15.0,          # Rotation augmentation
        translate=0.1,         # Shift
        scale=0.25,            # Scale / Zoom
        fliplr=0.5,            # Horizontal flip
        erasing=0.2,           # Occlusion robustness
        auto_augment='randaugment'
    )

    print("=" * 65)
    print("  Training Completed!")
    run_dir = os.path.join(project, name)
    best_pt = os.path.join(run_dir, 'weights', 'best.pt')
    target_pt = r'c:\Users\ADMIN\Downloads\SEProject\ai-model\yolov8_food_cls.pt'
    backup_pt = r'c:\Users\ADMIN\Downloads\SEProject\ai-model\yolov8_food_cls_300ep.pt'

    if os.path.exists(best_pt):
        shutil.copy2(best_pt, target_pt)
        shutil.copy2(best_pt, backup_pt)
        print(f"  [SUCCESS] New best weights copied to: {target_pt}")

    # Generate charts
    csv_file = os.path.join(run_dir, 'results.csv')
    generate_training_plots(csv_file, r'c:\Users\ADMIN\Downloads\SEProject\ai-model')
    print("=" * 65)

if __name__ == '__main__':
    train_nutriplate_food35_model()
