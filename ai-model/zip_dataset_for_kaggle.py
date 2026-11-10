import os
import zipfile
import time

def zip_dataset():
    src_dir = r'c:\Users\ADMIN\Downloads\SEProject\datasets\new_khana_internet'
    out_zip = r'c:\Users\ADMIN\Downloads\SEProject\NutriPlate-Food35.zip'

    print("=" * 60)
    print("  CREATING PURE KAGGLE IMAGE DATASET ARCHIVE")
    print("  (Only pure train/ and val/ images, zero metadata/cache files)")
    print(f"  Source: {src_dir}")
    print(f"  Output: {out_zip}")
    print("=" * 60)

    valid_exts = {'.jpg', '.jpeg', '.png', '.webp', '.bmp'}
    target_dirs = ['train', 'val']

    files_to_zip = []
    for tdir in target_dirs:
        dir_path = os.path.join(src_dir, tdir)
        if not os.path.exists(dir_path):
            continue
        for root, _, files in os.walk(dir_path):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in valid_exts:
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, src_dir)
                    files_to_zip.append((full_path, rel_path))

    t0 = time.time()
    total_files = len(files_to_zip)
    print(f"Found {total_files} pure image files to package.")
    processed = 0

    with zipfile.ZipFile(out_zip, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
        for full_path, rel_path in files_to_zip:
            zipf.write(full_path, arcname=rel_path)
            processed += 1
            if processed % 1000 == 0 or processed == total_files:
                print(f"Zipped {processed}/{total_files} images... ({time.time() - t0:.1f}s)")

    zip_size_mb = os.path.getsize(out_zip) / (1024 * 1024)
    print("=" * 60)
    print(f"  SUCCESS! Pure Kaggle Dataset Zip Created: {out_zip}")
    print(f"  Total Images: {processed}")
    print(f"  Final Size: {zip_size_mb:.2f} MB ({zip_size_mb / 1024:.2f} GB)")
    print(f"  Elapsed Time: {time.time() - t0:.1f}s")
    print("=" * 60)

if __name__ == '__main__':
    zip_dataset()
