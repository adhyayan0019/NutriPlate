import os
import sys
import re
import random
import urllib.request
import urllib.parse
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image, ImageFilter, ImageEnhance

# Force UTF-8 stdout to avoid Windows cp1252 encoding issues
sys.stdout.reconfigure(encoding='utf-8')

# Target Categories with diverse realistic search terms
FOOD_CATEGORIES = {
    'dal': [
        'dal tadka yellow dal bowl',
        'dhaba style yellow dal fry',
        'toor dal fry indian food plate'
    ],
    'dal makhani': [
        'dal makhani punjabi bowl',
        'creamy dal makhani restaurant food'
    ],
    'jeera rice': [
        'jeera rice bowl indian food',
        'cumin seeds jeera rice plate'
    ],
    'steamed rice': [
        'white steamed rice bowl indian food',
        'boiled basmati rice plate'
    ],
    'onion salad': [
        'onion salad kachumber sliced onions',
        'indian onion cucumber salad plate'
    ],
    'raita': [
        'boondi raita curd bowl indian',
        'cucumber raita yogurt bowl'
    ],
    'chapati': [
        'roti chapati phulka on plate',
        'home cooked soft chapati'
    ],
    'aloo paratha': [
        'aloo paratha with butter curd',
        'punjabi aloo paratha on plate'
    ],
    'garlic naan': [
        'garlic naan bread tandoori',
        'butter garlic naan indian food'
    ],
    'paneer masala': [
        'paneer butter masala bowl curry',
        'shahi paneer gravy restaurant'
    ],
    'palak paneer': [
        'palak paneer spinach curry bowl',
        'punjabi palak paneer gravy'
    ],
    'paneer tikka': [
        'tandoori paneer tikka plate',
        'paneer tikka restaurant starter'
    ],
    'aloo gobi': [
        'aloo gobi sabzi dry curry bowl',
        'punjabi aloo gobhi dish'
    ],
    'aloo mutter': [
        'aloo matar sabzi curry bowl',
        'potato peas aloo mutter gravy'
    ],
    'bhindi masala': [
        'bhindi masala okra fry bowl',
        'crispy bhindi fry indian sabzi'
    ],
    'chana masala': [
        'chana masala chickpea curry bowl',
        'punjabi chole chana masala'
    ],
    'chole bhature': [
        'chole bhature plate punjabi',
        'delhi chole bhature street food'
    ],
    'rajma chawal': [
        'rajma chawal bowl red kidney beans',
        'punjabi rajma gravy rice'
    ],
    'biryani': [
        'hyderabadi dum biryani plate',
        'chicken biryani indian restaurant'
    ],
    'butter chicken': [
        'butter chicken murgh makhani bowl',
        'chicken tikka masala gravy'
    ],
    'samosa': [
        'crispy samosa street food plate',
        'hot aloo samosa with chutney'
    ],
    'pav bhaji': [
        'mumbai pav bhaji plate with butter',
        'street style pav bhaji dish'
    ],
    'masala dosa': [
        'masala dosa with sambar chutney',
        'crispy south indian masala dosa'
    ],
    'idli': [
        'idli sambar south indian breakfast',
        'steamed idli plate with coconut chutney'
    ],
    'medu vada': [
        'medu vada sambar chutney plate',
        'crispy south indian vadai'
    ],
    'vada pav': [
        'mumbai vada pav street food',
        'batata vada pav green chutney'
    ],
    'dhokla': [
        'khaman dhokla gujarati yellow',
        'spongy besan dhokla plate'
    ],
    'pani puri': [
        'pani puri golgappa street food',
        'puchka plate with spiced water'
    ],
    'poha': [
        'kanda poha batata poha breakfast',
        'indori poha plate with sev'
    ],
    'gulab jamun': [
        'gulab jamun in sugar syrup bowl',
        'hot sweet gulab jamun plate'
    ],
    'jalebi': [
        'crispy orange jalebi sweet plate',
        'rabri jalebi indian dessert'
    ],
    'rasgulla': [
        'bengali white rasgulla in syrup',
        'soft spongy rasgulla bowl'
    ],
    'kheer': [
        'rice kheer payasam dessert bowl',
        'sweet kheer with dry fruits'
    ],
    'gajar ka halwa': [
        'gajar ka halwa carrot dessert bowl',
        'punjabi gajar halwa plate'
    ],
    'thali': [
        'indian vegetarian thali meal plate',
        'north indian thali variety bowls'
    ]
}

OUTPUT_BASE = r'c:\Users\ADMIN\Downloads\SEProject\datasets\new_khana_internet'
TRAIN_DIR = os.path.join(OUTPUT_BASE, 'train')
VAL_DIR = os.path.join(OUTPUT_BASE, 'val')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
}

def fetch_image_urls(query, max_count=50):
    urls = []
    for first in [0, 35, 70]:
        url = f'https://www.bing.com/images/async?q={urllib.parse.quote(query)}&first={first}&count=35&mmasync=1'
        req = urllib.request.Request(url, headers=HEADERS)
        try:
            with urllib.request.urlopen(req, timeout=8) as resp:
                html = resp.read().decode('utf-8', errors='ignore')
                found = re.findall(r'murl&quot;:&quot;(http[^&]+)&quot;', html)
                for u in found:
                    if u.startswith('http') and not u.endswith('.svg') and u not in urls:
                        urls.append(u)
        except Exception:
            pass
        if len(urls) >= max_count:
            break
    return urls[:max_count]

def is_valid_image(img):
    if img.width < 180 or img.height < 180:
        return False
    # Filter extreme aspect ratios (banners or ribbons)
    ratio = img.width / img.height
    if ratio < 0.45 or ratio > 2.2:
        return False
    # Check if image is blank / solid color
    extrema = img.convert('L').getextrema()
    if extrema[1] - extrema[0] < 30:
        return False
    return True

def apply_blur_and_robustness_augmentations(base_img):
    """
    Generates 3 synthetic real-world robustness variants:
    1. Gaussian / Defocus Blur (camera out of focus)
    2. Motion Blur (hand shake)
    3. Low-Light Dim Lighting (dim restaurant / shadows)
    """
    variants = []

    # 1. Gaussian Blur (Dhundli photo)
    radius = random.uniform(1.8, 3.5)
    blurred = base_img.filter(ImageFilter.GaussianBlur(radius=radius))
    variants.append(('gblur', blurred))

    # 2. Low-Light / Dark Shadow
    enhancer = ImageEnhance.Brightness(base_img)
    dimmed = enhancer.enhance(random.uniform(0.55, 0.78))
    # Add slight contrast change
    dimmed = ImageEnhance.Contrast(dimmed).enhance(random.uniform(1.1, 1.35))
    variants.append(('dim', dimmed))

    # 3. Soft Lens Defocus with Color Jitter (Haldi reflection)
    defocused = base_img.filter(ImageFilter.BoxBlur(radius=1.5))
    color_jitter = ImageEnhance.Color(defocused).enhance(random.uniform(0.8, 1.3))
    variants.append(('jitter', color_jitter))

    return variants

def download_and_process(category, url, idx):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=7) as resp:
            data = resp.read()
        
        img = Image.open(BytesIO(data)).convert('RGB')
        if not is_valid_image(img):
            return None

        # Determine train vs val split (80% train, 20% val)
        is_val = (random.random() < 0.20)
        target_dir = os.path.join(VAL_DIR if is_val else TRAIN_DIR, category)
        os.makedirs(target_dir, exist_ok=True)

        base_filename = f"{category}_{idx:04d}_orig.jpg"
        base_path = os.path.join(target_dir, base_filename)
        img.save(base_path, 'JPEG', quality=88)

        saved_count = 1

        # Only augment training set to keep validation set strictly realistic
        if not is_val:
            aug_variants = apply_blur_and_robustness_augmentations(img)
            for aug_name, aug_img in aug_variants:
                aug_filename = f"{category}_{idx:04d}_{aug_name}.jpg"
                aug_path = os.path.join(target_dir, aug_filename)
                aug_img.save(aug_path, 'JPEG', quality=85)
                saved_count += 1

        return saved_count
    except Exception:
        return None

def build_category_dataset(category, search_queries, target_base_images=40):
    print(f"\n[+] Processing Category: '{category}'")
    all_urls = []
    for q in search_queries:
        urls = fetch_image_urls(q, max_count=35)
        for u in urls:
            if u not in all_urls:
                all_urls.append(u)
        if len(all_urls) >= target_base_images * 2:
            break

    print(f"    Found {len(all_urls)} candidate image URLs from internet.")
    success_base = 0
    total_images_saved = 0

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(download_and_process, category, url, i): url for i, url in enumerate(all_urls)}
        for fut in as_completed(futures):
            res = fut.result()
            if res:
                success_base += 1
                total_images_saved += res
                if success_base >= target_base_images:
                    break

    print(f"    [DONE] '{category}': {success_base} base images -> {total_images_saved} total images with blur augmentations.")
    return total_images_saved

def main():
    print("=" * 65)
    print("  APNA KHANA INTERNET DATASET BUILDER")
    print(f"  Target Categories: {len(FOOD_CATEGORIES)}")
    print(f"  Output Base:       {OUTPUT_BASE}")
    print("  Includes:          Real-world scraping + Synthetic Blur Robustness")
    print("=" * 65)

    os.makedirs(TRAIN_DIR, exist_ok=True)
    os.makedirs(VAL_DIR, exist_ok=True)

    total_dataset_size = 0
    for idx, (cat, queries) in enumerate(FOOD_CATEGORIES.items(), 1):
        print(f"\n--- Progress: [{idx}/{len(FOOD_CATEGORIES)}] ---")
        count = build_category_dataset(cat, queries, target_base_images=35)
        total_dataset_size += count

    print("\n" + "=" * 65)
    print("  DATASET GENERATION COMPLETE!")
    print(f"  Total Generated Images: {total_dataset_size}")
    print(f"  Dataset Directory:      {OUTPUT_BASE}")
    print("=" * 65)

if __name__ == '__main__':
    main()
