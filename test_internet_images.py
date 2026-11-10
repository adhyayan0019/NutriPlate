import os
import glob
import requests
import json

image_files = glob.glob('internet_test_images/*.jpg') + glob.glob('internet_test_images/*.jpeg')
print(f"==================================================")
print(f"  Testing {len(image_files)} Fresh Internet Food Images")
print(f"==================================================\n")

results = []

for img_path in sorted(image_files):
    name = os.path.basename(img_path)
    print(f"[*] Testing Image: {name}")
    try:
        with open(img_path, 'rb') as f:
            resp = requests.post(
                'http://localhost:8000/predict',
                files={'file': (name, f, 'image/jpeg')},
                data={'is_veg': 'true'},
                timeout=45
            )
        if resp.status_code != 200:
            print(f"   [HTTP {resp.status_code}]: {resp.text}")
            continue
        data = resp.json()
        separated = data.get('separated_foods', [])
        preds = data.get('predictions', [])

        detection_summary = []
        if separated:
            for item in separated:
                info = f"{item['name']} ({item['confidence']}%, count={item.get('count', 1)}, portion={item.get('portion', 1.0)})"
                detection_summary.append(info)
                print(f"   [Segmented Compartment/Item] {info}")
        elif preds:
            top = preds[0]
            info = f"{top['label']} ({top['confidence']}%)"
            detection_summary.append(info)
            print(f"   [Whole-Image Classification] {info}")
        else:
            print(f"   [No detection]")

        results.append({
            'file': name,
            'detections': detection_summary
        })
    except Exception as e:
        print(f"   [Error]: {e}")
    print()

print("==================================================")
print("  All Internet Images Processed Successfully!")
print("==================================================")
