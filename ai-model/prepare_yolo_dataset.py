import os
import shutil
import random

def prepare_yolo_cls_dataset(
    source_dir=r'c:\Users\ADMIN\Downloads\SEProject\khana',
    dest_dir=r'c:\Users\ADMIN\Downloads\SEProject\ai-model\yolo_dataset',
    max_images_per_class=100,  # 80 classes x 100 = 8,000 images (80% train, 20% val as in paper)
    train_split=0.8
):
    print("=" * 60)
    print("Preparing YOLOv8 Classification Dataset for 80 Indian Food Classes")
    print(f"Source: {source_dir}")
    print(f"Destination: {dest_dir}")
    print(f"Sample limit per class: {max_images_per_class} images")
    print("=" * 60)

    train_dir = os.path.join(dest_dir, 'train')
    val_dir = os.path.join(dest_dir, 'val')

    os.makedirs(train_dir, exist_ok=True)
    os.makedirs(val_dir, exist_ok=True)

    classes = sorted([d for d in os.listdir(source_dir) if os.path.isdir(os.path.join(source_dir, d))])
    print(f"Found {len(classes)} classes.")

    total_train = 0
    total_val = 0

    for idx, cls_name in enumerate(classes):
        cls_src = os.path.join(source_dir, cls_name)
        cls_train = os.path.join(train_dir, cls_name)
        cls_val = os.path.join(val_dir, cls_name)

        os.makedirs(cls_train, exist_ok=True)
        os.makedirs(cls_val, exist_ok=True)

        images = [f for f in os.listdir(cls_src) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        if not images:
            continue

        random.seed(42)
        random.shuffle(images)
        selected_images = images[:max_images_per_class]

        split_idx = int(len(selected_images) * train_split)
        train_imgs = selected_images[:split_idx]
        val_imgs = selected_images[split_idx:]

        for img in train_imgs:
            src_f = os.path.join(cls_src, img)
            dst_f = os.path.join(cls_train, img)
            if not os.path.exists(dst_f):
                shutil.copy2(src_f, dst_f)

        for img in val_imgs:
            src_f = os.path.join(cls_src, img)
            dst_f = os.path.join(cls_val, img)
            if not os.path.exists(dst_f):
                shutil.copy2(src_f, dst_f)

        total_train += len(train_imgs)
        total_val += len(val_imgs)

        if (idx + 1) % 10 == 0 or (idx + 1) == len(classes):
            print(f"Processed {idx + 1}/{len(classes)} classes... ({cls_name})")

    print("=" * 60)
    print(f"Dataset preparation complete!")
    print(f"Total Training Images:   {total_train} (~{round(total_train/(total_train+total_val)*100)}%)")
    print(f"Total Validation Images: {total_val} (~{round(total_val/(total_train+total_val)*100)}%)")
    print(f"Total Dataset Size:      {total_train + total_val} images")
    print("=" * 60)

if __name__ == '__main__':
    prepare_yolo_cls_dataset()
