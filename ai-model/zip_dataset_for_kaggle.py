import os
import zipfile
import time

def zip_dataset():
    src_dir = r'c:\Users\ADMIN\Downloads\SEProject\datasets\new_khana_internet'
    out_zip = r'c:\Users\ADMIN\Downloads\SEProject\NutriPlate-Food35.zip'

    print("=" * 60)
    print("  CREATING KAGGLE UPLOAD ZIP ARCHIVE")
    print(f"  Source: {src_dir}")
    print(f"  Output: {out_zip}")
    print("=" * 60)

    t0 = time.time()
    total_files = sum(len(files) for _, _, files in os.walk(src_dir))
    processed = 0

    with zipfile.ZipFile(out_zip, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
        for root, dirs, files in os.walk(src_dir):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, src_dir)
                zipf.write(full_path, arcname=rel_path)
                processed += 1
                if processed % 1000 == 0 or processed == total_files:
                    print(f"Zipped {processed}/{total_files} files... ({time.time() - t0:.1f}s)")

    zip_size_mb = os.path.getsize(out_zip) / (1024 * 1024)
    print("=" * 60)
    print(f"  SUCCESS! Zip Archive Created: {out_zip}")
    print(f"  Final Size: {zip_size_mb:.2f} MB ({zip_size_mb / 1024:.2f} GB)")
    print(f"  Elapsed Time: {time.time() - t0:.1f}s")
    print("=" * 60)

if __name__ == '__main__':
    zip_dataset()
