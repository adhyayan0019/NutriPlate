import os
import random
import shutil
import json
import csv
import numpy as np

def compute_allocation(orig_counts, target_total=50000, power=0.6):
    """
    Computes an optimal target image count per class using power-law scaling (N^power).
    - Preserves rare/minority classes (close to 100% retention).
    - Smoothly dampens majority classes so they don't overpower the dataset.
    - Ensures total sum equals exactly target_total.
    - Yields a realistic, varied distribution ('some are less, some are more').
    """
    orig_arr = np.array(orig_counts)
    low, high = 0.1, 1000.0
    for _ in range(100):
        mid = (low + high) / 2
        alloc = np.minimum(orig_arr, np.round(mid * (orig_arr ** power)).astype(int))
        if alloc.sum() < target_total:
            low = mid
        else:
            high = mid
    alloc = np.minimum(orig_arr, np.round(mid * (orig_arr ** power)).astype(int))
    diff = target_total - alloc.sum()
    if diff != 0:
        # distribute remainder across the largest classes
        sorted_indices = np.argsort(orig_arr)[::-1]
        for i in range(abs(diff)):
            idx = sorted_indices[i % len(sorted_indices)]
            if diff > 0 and alloc[idx] < orig_arr[idx]:
                alloc[idx] += 1
            elif diff < 0 and alloc[idx] > 1:
                alloc[idx] -= 1
    return alloc

def reduce_dataset():
    khana_dir = r'c:\Users\ADMIN\Downloads\SEProject\khana'
    khana_archive_dir = r'c:\Users\ADMIN\Downloads\SEProject\khana_archive_unused'
    
    yolo_dir = r'c:\Users\ADMIN\Downloads\SEProject\ai-model\khana_full_yolo'
    yolo_archive_dir = r'c:\Users\ADMIN\Downloads\SEProject\ai-model\khana_full_yolo_archive_unused'
    
    print("=" * 70)
    print("DATASET REDUCTION PIPELINE: 131,818 -> 50,000 IMAGES")
    print("=" * 70)
    print(f"Source Dataset:  {khana_dir}")
    print(f"Archive Folder:  {khana_archive_dir}")
    print(f"YOLO Dataset:    {yolo_dir}")
    print(f"Target Total:    50,000 images across 80 classes")
    print("=" * 70)
    
    classes = sorted([d for d in os.listdir(khana_dir) if os.path.isdir(os.path.join(khana_dir, d))])
    print(f"Found {len(classes)} classes.")
    
    class_files = {}
    orig_counts = []
    for c in classes:
        cls_path = os.path.join(khana_dir, c)
        files = sorted([f for f in os.listdir(cls_path) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))])
        class_files[c] = files
        orig_counts.append(len(files))
        
    total_orig = sum(orig_counts)
    print(f"Total current images in khana: {total_orig}")
    
    # Calculate allocations
    allocations = compute_allocation(orig_counts, target_total=50000, power=0.6)
    alloc_map = {c: int(alloc) for c, alloc in zip(classes, allocations)}
    
    print(f"Computed allocations: min={allocations.min()}, median={np.median(allocations):.1f}, max={allocations.max()}, total={allocations.sum()}")
    print("-" * 70)
    
    # Process khana dataset
    os.makedirs(khana_archive_dir, exist_ok=True)
    summary_data = []
    
    total_kept = 0
    total_archived = 0
    
    all_archived_files_set = set() # (class, filename)
    
    for idx, c in enumerate(classes):
        target_n = alloc_map[c]
        files = class_files[c]
        orig_n = len(files)
        
        # Deterministic shuffle with seed for reproducibility
        random.seed(42 + idx)
        shuffled = list(files)
        random.shuffle(shuffled)
        
        keep_set = set(shuffled[:target_n])
        archive_list = shuffled[target_n:]
        
        cls_archive_dir = os.path.join(khana_archive_dir, c)
        if archive_list:
            os.makedirs(cls_archive_dir, exist_ok=True)
            
        cls_src_dir = os.path.join(khana_dir, c)
        for fname in archive_list:
            src_fp = os.path.join(cls_src_dir, fname)
            dst_fp = os.path.join(cls_archive_dir, fname)
            os.rename(src_fp, dst_fp)
            all_archived_files_set.add((c, fname))
            
        total_kept += len(keep_set)
        total_archived += len(archive_list)
        pct = (target_n / orig_n) * 100
        
        summary_data.append({
            'class': c,
            'original_count': orig_n,
            'new_count': target_n,
            'archived_count': len(archive_list),
            'retention_pct': round(pct, 2)
        })
        
    print(f"Successfully reduced 'khana':")
    print(f"  Images Kept:     {total_kept}")
    print(f"  Images Archived: {total_archived}")
    print(f"  Sum Check:       {total_kept + total_archived} == {total_orig}")
    print("-" * 70)
    
    # If khana_full_yolo exists, also sync it
    if os.path.exists(yolo_dir):
        print(f"Syncing YOLO dataset at: {yolo_dir}")
        os.makedirs(yolo_archive_dir, exist_ok=True)
        yolo_archived = 0
        yolo_kept = 0
        
        for split in ['train', 'val']:
            split_dir = os.path.join(yolo_dir, split)
            split_archive_dir = os.path.join(yolo_archive_dir, split)
            if not os.path.exists(split_dir):
                continue
            for c in classes:
                cls_yolo_dir = os.path.join(split_dir, c)
                if not os.path.exists(cls_yolo_dir):
                    continue
                cls_yolo_archive = os.path.join(split_archive_dir, c)
                
                yolo_imgs = [f for f in os.listdir(cls_yolo_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
                for img_name in yolo_imgs:
                    if (c, img_name) in all_archived_files_set:
                        os.makedirs(cls_yolo_archive, exist_ok=True)
                        os.rename(
                            os.path.join(cls_yolo_dir, img_name),
                            os.path.join(cls_yolo_archive, img_name)
                        )
                        yolo_archived += 1
                    else:
                        yolo_kept += 1
                        
        # Remove old YOLO label cache files if present
        for cache_f in ['train.cache', 'val.cache']:
            cp = os.path.join(yolo_dir, cache_f)
            if os.path.exists(cp):
                os.remove(cp)
                print(f"Removed outdated cache: {cache_f}")
                
        print(f"YOLO dataset synced:")
        print(f"  YOLO Images Kept:     {yolo_kept}")
        print(f"  YOLO Images Archived: {yolo_archived}")
        print("-" * 70)
        
    # Save CSV and JSON reports
    csv_report_path = r'c:\Users\ADMIN\Downloads\SEProject\dataset_reduction_summary.csv'
    with open(csv_report_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['class', 'original_count', 'new_count', 'archived_count', 'retention_pct'])
        writer.writeheader()
        writer.writerows(summary_data)
        
    json_report_path = r'c:\Users\ADMIN\Downloads\SEProject\dataset_reduction_summary.json'
    with open(json_report_path, 'w', encoding='utf-8') as f:
        json.dump({
            'total_original': total_orig,
            'total_target': total_kept,
            'total_archived': total_archived,
            'classes_count': len(classes),
            'min_class_count': int(allocations.min()),
            'max_class_count': int(allocations.max()),
            'median_class_count': float(np.median(allocations)),
            'classes': summary_data
        }, f, indent=2)
        
    print(f"Saved CSV Report:  {csv_report_path}")
    print(f"Saved JSON Report: {json_report_path}")
    print("=" * 70)
    print("REDUCTION PIPELINE COMPLETED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == '__main__':
    reduce_dataset()
