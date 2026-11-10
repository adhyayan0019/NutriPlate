import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PIL import Image
from food_segmenter import separate_plate_items

test_images = [
    'uploads/1792146752859.jpg',  # Thali
    'uploads/1792146223543.jpg',  # Samosas
    'uploads/1792141808515.jpg',  # Aloo Paratha
]

for p in test_images:
    full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), p)
    if not os.path.exists(full_path):
        continue
    img = Image.open(full_path)
    items, preds = separate_plate_items(img)
    print(f"\n==========================================")
    print(f"IMAGE: {p} -> {len(items)} items separated")
    print(f"==========================================")
    for it in items:
        print(f"  * {it['name'].upper()}: {it['confidence']}% | count: {it.get('count', 1)} | portion: {it.get('portion', 1.0)} | box: {it.get('box')}")
