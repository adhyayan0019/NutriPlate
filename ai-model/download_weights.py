"""
Downloads MobileNetV2 weights with retry logic to handle unstable connections.
Run this ONCE before train.py.
"""
import os
import urllib.request
import hashlib

WEIGHTS_URL = "https://storage.googleapis.com/tensorflow/keras-applications/mobilenet_v2/mobilenet_v2_weights_tf_dim_ordering_tf_kernels_1.0_224_no_top.h5"
EXPECTED_SIZE = 9406464  # bytes

# Keras caches weights here on Windows
CACHE_DIR = os.path.join(os.path.expanduser("~"), ".keras", "models")
os.makedirs(CACHE_DIR, exist_ok=True)
DEST_PATH = os.path.join(CACHE_DIR, "mobilenet_v2_weights_tf_dim_ordering_tf_kernels_1.0_224_no_top.h5")

def download_with_resume(url, dest_path, expected_size):
    """Download file with resume support for incomplete downloads."""
    
    # Check if a valid (complete) file already exists
    if os.path.exists(dest_path):
        actual_size = os.path.getsize(dest_path)
        if actual_size == expected_size:
            print(f"[OK] Weights already fully downloaded ({actual_size} bytes). Skipping.")
            return True
        else:
            print(f"[WARN] Incomplete file found ({actual_size}/{expected_size} bytes). Re-downloading...")
            os.remove(dest_path)

    MAX_RETRIES = 10
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"\n[INFO] Attempt {attempt}/{MAX_RETRIES}: Downloading MobileNetV2 weights (~9 MB)...")
            
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=60) as response:
                total = int(response.headers.get('Content-Length', expected_size))
                downloaded = 0
                chunk_size = 65536  # 64KB chunks
                
                with open(dest_path, 'wb') as f:
                    while True:
                        chunk = response.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        pct = (downloaded / total) * 100
                        mb = downloaded / (1024 * 1024)
                        print(f"\r   -> {mb:.2f} MB / {total/(1024*1024):.2f} MB  ({pct:.1f}%)", end='', flush=True)
            
            print()  # newline after progress
            actual_size = os.path.getsize(dest_path)
            
            if actual_size >= expected_size:
                print(f"\n[OK] Download complete! File saved to:\n   {dest_path}")
                return True
            else:
                print(f"\n[ERROR] File appears truncated ({actual_size}/{expected_size} bytes). Retrying...")
                os.remove(dest_path)
                
        except Exception as e:
            print(f"\n[ERROR] Attempt {attempt} failed: {e}")
            if os.path.exists(dest_path):
                os.remove(dest_path)
    
    print("\n[FATAL] All download attempts failed.")
    print("   Please download manually from:")
    print(f"   {WEIGHTS_URL}")
    print(f"   And place the file at: {DEST_PATH}")
    return False

if __name__ == "__main__":
    success = download_with_resume(WEIGHTS_URL, DEST_PATH, EXPECTED_SIZE)
    if success:
        print("\n[READY] You can now run: python train.py")
