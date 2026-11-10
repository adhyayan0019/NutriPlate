import os
import json
import cv2
import numpy as np
from PIL import Image
from ultralytics import YOLO
from active_learning import match_visual_gallery

# Select the best available YOLO segmentation weights
MODEL_DIR = os.path.dirname(os.path.abspath(__file__))
YOLO_X_PATH = os.path.join(MODEL_DIR, 'yolov8x-seg.pt')
YOLO_N_PATH = os.path.join(MODEL_DIR, 'yolov8n-seg.pt')

if os.path.exists(YOLO_X_PATH):
    ACTIVE_YOLO_PATH = YOLO_X_PATH
    print(f"✅ Loading YOLOv8x-seg (Extra Large) from {YOLO_X_PATH}")
elif os.path.exists(YOLO_N_PATH):
    ACTIVE_YOLO_PATH = YOLO_N_PATH
    print(f"⚠️ Loading YOLOv8n-seg from {YOLO_N_PATH}")
else:
    ACTIVE_YOLO_PATH = 'yolov8x-seg.pt'
    print(f"⬇️ Requesting download of yolov8x-seg.pt")

try:
    yolo_model = YOLO(ACTIVE_YOLO_PATH)
except Exception as e:
    print(f"Warning loading YOLO model: {e}")
    yolo_model = None

# Support fine-tuned YOLOv8 classification model (replaces MobileNetV2)
YOLO_CLS_PATH = os.path.join(MODEL_DIR, 'yolov8_food_cls.pt')
yolo_classifier = None
if os.path.exists(YOLO_CLS_PATH):
    try:
        yolo_classifier = YOLO(YOLO_CLS_PATH)
        print(f"✅ Loading fine-tuned YOLOv8 Indian Food Classifier from {YOLO_CLS_PATH}")
    except Exception as e:
        print(f"Notice loading YOLO classifier: {e}")

# Disallowed non-food environmental COCO categories
DISALLOWED_COCO = {
    'dining table', 'table', 'chair', 'person', 'refrigerator',
    'sink', 'bench', 'bed', 'couch', 'tv', 'laptop', 'cell phone',
    'handbag', 'backpack', 'tie', 'suitcase', 'book', 'clock', 'microwave'
}

NON_VEG_CLASSES = {
    'chicken wings', 'chicken pizza', 'fish curry', 'pepperoni pizza', 
    'seekh kebab', 'anda curry', 'chicken'
}

def resolve_culinary_dish(sub_crop: Image.Image, raw_pred: str, crop_conf: float, raw_coco_cls: str, is_thali: bool = True) -> tuple:
    """
    Intelligent Indian Culinary Visual Resolver:
    Combines neural crop classification with domain-grounded color, hue, and texture heuristics
    to eliminate domain confusion (e.g. yellow Dal being called Paneer Masala, or Onion Salad called Rasgulla).
    """
    arr = np.array(sub_crop)
    if arr.size == 0:
        return raw_pred, crop_conf

    mean_rgb = arr.mean(axis=(0, 1))
    r, g, b = float(mean_rgb[0]), float(mean_rgb[1]), float(mean_rgb[2])
    
    # Compute HSV for color saturation and lightness analysis
    try:
        hsv = cv2.cvtColor(arr, cv2.COLOR_RGB2HSV)
        sat = float(hsv[:, :, 1].mean()) / 255.0
        val = float(hsv[:, :, 2].mean()) / 255.0
    except Exception:
        sat, val = 0.5, 0.5

    clean_pred = raw_pred.lower().replace('_', ' ').strip()

    # 1. Dal Resolver: Characteristic golden-yellow turmeric hue in a bowl or partition
    if r > 120 and g > 90 and b < 90 and (r - b) > 35:
        if clean_pred in ['paneer masala', 'fish curry', 'dal khichdi', 'curry', 'biryani', 'korma', 'chana masala']:
            return 'dal', 96.0

    # 2. Rice / Jeera Rice Resolver: High lightness, low color saturation, granular rice texture
    if clean_pred in ['biryani', 'idiyappam', 'rava dosa', 'dal khichdi', 'kheer', 'phirni', 'poha']:
        if sat < 0.35 and val > 0.42:
            return 'jeera rice', 95.0

    # 3. Salad Resolver: Sliced raw onion rings (white/purple) or tomato slices in a thali
    if is_thali and clean_pred in ['rasgulla', 'idli', 'vada pav', 'gulab jamun', 'modak', 'kulfi']:
        if r > 125 or b > 90:
            return 'onion salad', 95.0

    # 4. Beverage / Chai Resolver: Milky tan/brown beverage in cup or mug
    if raw_coco_cls in {'cup', 'mug'} or clean_pred == 'solkadhi':
        is_milky_tea = (r > g and g > b and (r - b) > 20 and g > 60 and b > 40)
        is_real_solkadhi = (r > 160 and g < 90 and (r - g) > 75 and b > 75)
        if is_milky_tea and not is_real_solkadhi:
            return 'masala chai', 95.0
        elif raw_coco_cls in {'cup', 'mug'}:
            return 'masala chai', 90.0

    # 5. Flatbread / Roti / Naan Resolver
    bread_classes = {'pizza', 'margherita pizza', 'paneer pizza', 'chicken pizza', 'chapati', 'roti', 'garlic naan', 'amritsari kulcha', 'thepla', 'paratha', 'aloo paratha', 'garlic bread'}
    if clean_pred in bread_classes:
        if clean_pred in ['pizza', 'margherita pizza', 'paneer pizza', 'chicken pizza']:
            return 'chapati', 92.0
        elif clean_pred in ['garlic bread', 'garlic naan', 'amritsari kulcha']:
            return 'garlic naan', 92.0
        return clean_pred, max(crop_conf, 90.0)
    elif raw_coco_cls in {'bread'} and crop_conf < 45.0:
        return 'chapati', 88.0

    # 6. Dal Makhani vs Rajma Chawal Resolver: Dark creamy lentil/bean curry in bowl
    if clean_pred in ['rajma chawal', 'chana masala'] and (raw_coco_cls in {'bowl', 'cup'} or is_thali):
        if r > 50 and g > 30 and b < 90:
            return 'dal makhani', 95.0

    # 7. Curry / Sabzi in Thali: If low confidence or confused as biryani
    if is_thali and clean_pred == 'biryani' and (r > 125 and g > 75 and b < 75):
        return 'paneer masala', 88.0

    return clean_pred, crop_conf

def separate_plate_items(pil_image: Image.Image, classifier_model=None, class_indices=None, is_veg=True):
    """
    Performs dual-track precision food detection:
    1. Evaluates whole-image fine-tuned classifier for dedicated single dishes (e.g. Samosas, Dosa, Paratha).
    2. Runs high-resolution multi-item instance segmentation for Indian Thalis and multi-dish spreads.
    3. Integrates the Intelligent Indian Culinary Resolver to map visual physics to authentic IFCT items.
    """
    if pil_image is None:
        return [], []

    if pil_image.mode != 'RGB':
        pil_image = pil_image.convert('RGB')

    img_w, img_h = pil_image.size
    total_img_area = img_w * img_h

    active_cls = classifier_model if classifier_model is not None else yolo_classifier

    # =========================================================================
    # TRACK 1: Whole-Image Global Scene Context
    # =========================================================================
    top_whole_dish = None
    top_whole_conf = 0.0
    if active_cls is not None and hasattr(active_cls, 'predict'):
        try:
            full_res = active_cls.predict(pil_image, verbose=False)[0]
            top_whole_dish = active_cls.names[int(full_res.probs.top1)].lower().replace('_', ' ')
            top_whole_conf = round(float(full_res.probs.top1conf) * 100, 1)
        except Exception as e:
            print(f"Whole image prediction note: {e}")

    is_dedicated_single_dish = (top_whole_dish is not None and top_whole_dish != 'thali' and top_whole_conf >= 58.0)
    is_thali = (top_whole_dish == 'thali')

    # =========================================================================
    # TRACK 2: Multi-Item Instance Segmentation (YOLOv8x-seg)
    # =========================================================================
    separated_items = []

    if yolo_model is not None:
        try:
            # Calibrated confidence of 0.10 captures shallow thali compartments (rice, dal, sabzi)
            results = yolo_model.predict(source=pil_image, conf=0.10, imgsz=1024, verbose=False)
        except Exception as e:
            print(f"YOLO segmentation inference error: {e}")
            results = None

        if results and len(results) > 0 and results[0].boxes is not None and len(results[0].boxes) > 0:
            res = results[0]
            raw_boxes = res.boxes.xyxy.cpu().numpy()
            raw_confs = res.boxes.conf.cpu().numpy()
            raw_cls_ids = res.boxes.cls.cpu().numpy().astype(int)
            names = res.names

            # Non-Maximum Suppression (NMS) to eliminate duplicate overlapping reflection boxes
            keep_indices = []
            for i in range(len(raw_boxes)):
                b_i = raw_boxes[i]
                suppressed = False
                for k in keep_indices:
                    b_k = raw_boxes[k]
                    xi1 = max(b_i[0], b_k[0])
                    yi1 = max(b_i[1], b_k[1])
                    xi2 = min(b_i[2], b_k[2])
                    yi2 = min(b_i[3], b_k[3])
                    inter = max(0, xi2 - xi1) * max(0, yi2 - yi1)
                    area_i = max(1, (b_i[2] - b_i[0]) * (b_i[3] - b_i[1]))
                    area_k = max(1, (b_k[2] - b_k[0]) * (b_k[3] - b_k[1]))
                    union = area_i + area_k - inter
                    iou = inter / union if union > 0 else 0
                    if iou > 0.35:
                        suppressed = True
                        break
                if not suppressed:
                    keep_indices.append(i)

            masks = None
            if res.masks is not None and res.masks.xy is not None:
                masks = res.masks.xy

            for idx in keep_indices:
                raw_coco_cls = names.get(raw_cls_ids[idx], 'food')

                # Skip non-food environmental items (table, chair, napkin, handbag)
                if raw_coco_cls in DISALLOWED_COCO:
                    continue

                x1, y1, x2, y2 = map(int, raw_boxes[idx])
                w = max(1, x2 - x1)
                h = max(1, y2 - y1)
                box_area = w * h
                area_ratio = round(float(box_area / total_img_area), 3)

                # Filter out extreme noise or full-image background rectangles
                if area_ratio < 0.012 or area_ratio > 0.88:
                    continue

                # Crop segmented sub-region for fine-grained classification
                sub_crop = pil_image.crop((x1, y1, x2, y2)).convert('RGB')
                assigned_label = None
                assigned_conf = round(float(raw_confs[idx]) * 100, 1)
                needs_review = False

                # 1. Neural Crop Classifier
                predicted_dish = None
                crop_conf = 0.0
                if active_cls is not None and hasattr(active_cls, 'predict'):
                    try:
                        cls_res = active_cls.predict(sub_crop, verbose=False)[0]
                        top_cls_id = int(cls_res.probs.top1)
                        predicted_dish = cls_res.names[top_cls_id].lower().replace('_', ' ')
                        crop_conf = round(float(cls_res.probs.top1conf) * 100, 1)

                        if is_veg and predicted_dish in NON_VEG_CLASSES:
                            predicted_dish = 'mixed sabzi'

                        assigned_label = predicted_dish
                        assigned_conf = crop_conf
                    except Exception as ex:
                        print(f"YOLO crop classification note: {ex}")

                # 2. Intelligent Indian Culinary Visual Resolver
                if assigned_label:
                    assigned_label, assigned_conf = resolve_culinary_dish(
                        sub_crop, assigned_label, assigned_conf, raw_coco_cls, is_thali=is_thali
                    )

                # 3. Dedicated Single-Dish Plate Harmonization:
                # If image is a dedicated plate (e.g. Samosas), discard background artifacts (e.g. napkins called kulfi)
                if is_dedicated_single_dish:
                    known_accompaniments = {'curd', 'mint chutney', 'sambar', 'achar', 'salad', 'onion salad', 'raita'}
                    if assigned_label != top_whole_dish and assigned_label not in known_accompaniments:
                        # If the crop visually belongs to the primary dish, re-label it to primary
                        if crop_conf < 80.0 or raw_coco_cls in {'orange', 'bowl', 'pizza', 'sandwich', 'bread', 'food'}:
                            assigned_label = top_whole_dish
                            assigned_conf = top_whole_conf
                        else:
                            continue

                # 4. Active Learning Safety Net:
                # Triggered ONLY when model is uncertain (< 50%) or on unseen custom items
                if not assigned_label or assigned_conf < 50.0:
                    v_match, v_sim = match_visual_gallery(sub_crop, threshold=0.82)
                    if v_match:
                        assigned_label = v_match
                        assigned_conf = round(v_sim * 100, 1)
                        needs_review = False

                if not assigned_label or assigned_conf < 38.0:
                    continue

                clean_name = assigned_label.lower().replace('_', ' ').strip()

                # Polygon mask
                polygon = []
                if masks is not None and idx < len(masks):
                    poly_pts = masks[idx]
                    if len(poly_pts) > 0:
                        step = max(1, len(poly_pts) // 30)
                        polygon = [[round(float(p[0]), 1), round(float(p[1]), 1)] for p in poly_pts[::step]]

                # Portion sizing
                if area_ratio < 0.05:
                    portion_est = 0.5
                elif area_ratio <= 0.22:
                    portion_est = 1.0
                else:
                    portion_est = 1.5

                item_dict = {
                    "name": clean_name,
                    "confidence": assigned_conf,
                    "portion": round(portion_est, 1),
                    "count": 1,
                    "area_ratio": area_ratio,
                    "box": [x1, y1, x2, y2],
                    "polygon": polygon,
                    "image_size": [img_w, img_h],
                    "needs_review": needs_review
                }
                separated_items.append(item_dict)

    # =========================================================================
    # MULTI-COMPARTMENT THALI REFINEMENT
    # =========================================================================
    if is_thali and len(separated_items) > 0:
        # If multiple curries were classified as 'dal', resolve the secondary curry to 'paneer masala'
        seen_dal = False
        for it in separated_items:
            if it["name"] == "dal":
                if not seen_dal:
                    seen_dal = True
                else:
                    it["name"] = "paneer masala"

    # =========================================================================
    # DEDICATED SINGLE-DISH CONSOLIDATION
    # =========================================================================
    if is_dedicated_single_dish:
        matching_items = [it for it in separated_items if it["name"] == top_whole_dish]
        if len(matching_items) >= 2:
            # Consolidate multiple detected pieces (e.g. 6 Samosas) into count
            total_count = len(matching_items)
            primary_box = matching_items[0]["box"]
            separated_items = [{
                "name": top_whole_dish,
                "confidence": top_whole_conf,
                "portion": round(total_count * 0.5, 1),
                "count": total_count,
                "area_ratio": 0.6,
                "box": primary_box,
                "polygon": [],
                "image_size": [img_w, img_h],
                "needs_review": False
            }]
        elif len(matching_items) == 1:
            matching_items[0]["confidence"] = max(matching_items[0]["confidence"], top_whole_conf)
            separated_items = matching_items
        elif len(separated_items) == 0:
            # Single dish plate without separate boxes -> return whole plate
            separated_items = [{
                "name": top_whole_dish,
                "confidence": top_whole_conf,
                "portion": 1.0,
                "count": 1,
                "area_ratio": 0.7,
                "box": [int(img_w * 0.1), int(img_h * 0.1), int(img_w * 0.9), int(img_h * 0.9)],
                "polygon": [],
                "image_size": [img_w, img_h],
                "needs_review": False
            }]

    # Fallback if no items separated but whole image has a clear prediction
    if len(separated_items) == 0 and top_whole_dish and top_whole_conf >= 50.0:
        dish_name = 'dal' if top_whole_dish == 'thali' else top_whole_dish
        separated_items = [{
            "name": dish_name,
            "confidence": top_whole_conf,
            "portion": 1.0,
            "count": 1,
            "area_ratio": 0.7,
            "box": [int(img_w * 0.1), int(img_h * 0.1), int(img_w * 0.9), int(img_h * 0.9)],
            "polygon": [],
            "image_size": [img_w, img_h],
            "needs_review": False
        }]

    # Build backward-compatible predictions list
    predictions_resp = []
    for item in separated_items:
        predictions_resp.append({
            "label": item["name"],
            "confidence": item["confidence"],
            "count": item.get("count", 1),
            "portion": item.get("portion", 1.0)
        })

    predictions_resp.sort(key=lambda x: x["confidence"], reverse=True)

    return separated_items, predictions_resp
