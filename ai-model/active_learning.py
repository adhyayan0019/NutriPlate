import os
import json
import hashlib
from typing import Dict, List, Optional, Tuple
from PIL import Image

MEMORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'feedback_dataset', 'active_learning_memory.json')
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'feedback_dataset', 'active_learning_log.json')
GALLERY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'feedback_dataset', 'active_learning_gallery.pt')

_visual_extractor = None
_visual_transform = None

def get_visual_extractor():
    """Initializes PyTorch MobileNetV3 feature extractor for Few-Shot visual similarity."""
    global _visual_extractor, _visual_transform
    if _visual_extractor is None:
        try:
            import torch
            import torchvision.models as models
            import torchvision.transforms as T
            m = models.mobilenet_v3_small(weights='DEFAULT')
            m.classifier = torch.nn.Identity()
            m.eval()
            _visual_extractor = m
            _visual_transform = T.Compose([
                T.Resize((224, 224)),
                T.ToTensor(),
                T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])
            print("[Active Learning] Loaded Few-Shot MobileNetV3 Visual Embedding Engine")
        except Exception as e:
            print(f"Notice initializing visual extractor: {e}")
    return _visual_extractor, _visual_transform

def load_visual_gallery() -> List[dict]:
    """Loads saved visual embeddings gallery from disk."""
    if not os.path.exists(GALLERY_FILE):
        return []
    try:
        import torch
        return torch.load(GALLERY_FILE, map_location='cpu', weights_only=False)
    except Exception:
        return []

def save_visual_gallery(gallery: List[dict]):
    """Persists visual embeddings gallery to disk."""
    import torch
    os.makedirs(os.path.dirname(GALLERY_FILE), exist_ok=True)
    try:
        torch.save(gallery, GALLERY_FILE)
    except Exception as e:
        print(f"Notice saving visual gallery: {e}")

def add_to_visual_gallery(dish_name: str, pil_crop: Image.Image):
    """
    Learns and saves a 576-dim visual feature embedding for a human-verified dish crop.
    This enables cross-image few-shot generalization for unseen dishes like Masala Chai.
    """
    if pil_crop is None or not dish_name:
        return
    clean_name = dish_name.lower().replace('_', ' ').strip()
    extractor, transform = get_visual_extractor()
    if extractor is None or transform is None:
        return
    try:
        import torch
        import torch.nn.functional as F
        if pil_crop.mode != 'RGB':
            pil_crop = pil_crop.convert('RGB')
        t = transform(pil_crop).unsqueeze(0)
        with torch.no_grad():
            emb = F.normalize(extractor(t), p=2, dim=1).squeeze(0).cpu()
        
        gallery = load_visual_gallery()
        if len(gallery) > 300:
            gallery = gallery[-250:]
        gallery.append({"label": clean_name, "emb": emb})
        save_visual_gallery(gallery)
        print(f"[Active Learning] Learned visual feature embedding for: [{clean_name}] (Gallery size: {len(gallery)})")
    except Exception as e:
        print(f"Error adding to visual gallery: {e}")

def match_visual_gallery(pil_crop: Image.Image, threshold: float = 0.76) -> Tuple[Optional[str], float]:
    """
    Compares a food crop against the learned visual gallery using cosine similarity.
    Returns (matched_dish_name, similarity_score) if score >= threshold.
    """
    if pil_crop is None:
        return None, 0.0
    extractor, transform = get_visual_extractor()
    if extractor is None or transform is None:
        return None, 0.0
    gallery = load_visual_gallery()
    if not gallery:
        return None, 0.0
    try:
        import torch
        import torch.nn.functional as F
        if pil_crop.mode != 'RGB':
            pil_crop = pil_crop.convert('RGB')
        t = transform(pil_crop).unsqueeze(0)
        with torch.no_grad():
            emb = F.normalize(extractor(t), p=2, dim=1).squeeze(0).cpu()
        
        best_label = None
        best_sim = 0.0
        for item in gallery:
            sim = F.cosine_similarity(emb.unsqueeze(0), item["emb"].unsqueeze(0)).item()
            if sim > best_sim:
                best_sim = sim
                best_label = item["label"]
        
        if best_sim >= threshold and best_label:
            return best_label, best_sim
    except Exception as e:
        print(f"Visual gallery match error: {e}")
    return None, 0.0

def compute_hash(image_bytes: bytes) -> str:
    """Computes MD5 hash of image bytes for exact-match content recognition."""
    return hashlib.md5(image_bytes).hexdigest()

def load_memory() -> Dict[str, dict]:
    """Loads active learning memory mappings from disk."""
    if not os.path.exists(MEMORY_FILE):
        return {}
    try:
        with open(MEMORY_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return {}

def save_memory(memory: Dict[str, dict]):
    """Persists active learning memory to disk."""
    os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
    with open(MEMORY_FILE, 'w') as f:
        json.dump(memory, f, indent=2)

def sync_from_log_if_needed():
    """Builds initial memory index from existing active_learning_log.json if empty."""
    memory = load_memory()
    if memory:
        return memory

    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, 'r') as f:
                logs = json.load(f)
            for entry in logs:
                orig = entry.get('original_prediction', '').lower().strip()
                corr = entry.get('human_corrected_label', '').lower().strip()
                img_path = entry.get('image_path', '')
                base_name = os.path.basename(img_path) if img_path else ''

                if orig and corr:
                    # Index by basename and full path
                    for key in [base_name, img_path]:
                        if key:
                            if key not in memory:
                                memory[key] = {"corrections": {}}
                            memory[key]["corrections"][orig] = corr
            
            # Also associate known uploads with their MD5 hash if file exists
            uploads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'uploads')
            for base_name in list(memory.keys()):
                target_file = os.path.join(uploads_dir, base_name)
                if os.path.exists(target_file):
                    try:
                        with open(target_file, 'rb') as f:
                            file_hash = compute_hash(f.read())
                        memory[file_hash] = memory[base_name]
                    except Exception:
                        pass

            save_memory(memory)
        except Exception as e:
            print(f"Active learning sync error: {e}")

    return memory

def record_feedback(original_label: str, corrected_label: str, image_path: str = "", image_bytes: Optional[bytes] = None):
    """
    Saves human correction into active learning memory indexed by content hash and filename.
    """
    memory = load_memory()
    orig = original_label.lower().replace('_', ' ').strip()
    corr = corrected_label.lower().replace('_', ' ').strip()

    keys_to_index = []
    if image_bytes:
        keys_to_index.append(compute_hash(image_bytes))
    if image_path:
        keys_to_index.append(image_path)
        keys_to_index.append(os.path.basename(image_path))

    for key in keys_to_index:
        if not key:
            continue
        if key not in memory:
            memory[key] = {"corrections": {}}
        memory[key]["corrections"][orig] = corr

    save_memory(memory)

def record_verified_plate(image_path: str = "", image_bytes: Optional[bytes] = None, foods: Optional[List[dict]] = None):
    """
    Saves user-annotated or user-verified foods (including custom drawn boxes and portions)
    into the active learning cache for this image.
    """
    if not foods or not isinstance(foods, list):
        return
    memory = load_memory()
    keys_to_index = []
    if image_bytes:
        keys_to_index.append(compute_hash(image_bytes))
    if image_path:
        keys_to_index.append(image_path)
        keys_to_index.append(os.path.basename(image_path))

    # Also check if image exists in uploads directory to get its hash
    uploads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'uploads')
    if image_path:
        target_file = os.path.join(uploads_dir, os.path.basename(image_path))
        if os.path.exists(target_file):
            try:
                with open(target_file, 'rb') as f:
                    keys_to_index.append(compute_hash(f.read()))
            except Exception:
                pass

    clean_items = []
    for f in foods:
        name = f.get("name", "").lower().replace('_', ' ').strip()
        if not name:
            continue
        clean_items.append({
            "name": name,
            "portion": float(f.get("portion", 1.0)),
            "count": int(f.get("count", 1)),
            "confidence": 100.0,
            "box": f.get("box"),
            "image_size": f.get("imageSize") or f.get("image_size"),
            "needs_review": False,
            "human_verified": True
        })

    for key in set(keys_to_index):
        if not key:
            continue
        if key not in memory:
            memory[key] = {"corrections": {}, "plate_items": []}
        memory[key]["plate_items"] = clean_items

    save_memory(memory)

    # Harvest Few-Shot visual feature embeddings for all verified food crops
    if image_path:
        target_file = os.path.join(uploads_dir, os.path.basename(image_path))
        if os.path.exists(target_file):
            try:
                base_img = Image.open(target_file).convert('RGB')
                for f in foods:
                    fname = f.get("name", "").lower().replace('_', ' ').strip()
                    orig = f.get("originalPrediction", "").lower().replace('_', ' ').strip()
                    fbox = f.get("box")
                    # Only add to visual gallery if it was a user correction or custom/user-drawn item.
                    # Do NOT pollute the few-shot gallery with standard items the model already knows!
                    is_user_taught = (orig and orig != fname) or f.get("user_drawn") or f.get("is_custom") or f.get("needs_review")
                    if is_user_taught and fname and fbox and len(fbox) == 4:
                        bx1, by1, bx2, by2 = map(int, fbox)
                        if bx2 > bx1 and by2 > by1:
                            crop = base_img.crop((bx1, by1, bx2, by2))
                            add_to_visual_gallery(fname, crop)
            except Exception as ex:
                print(f"Active learning visual crop harvesting notice: {ex}")

def apply_active_learning(
    separated_items: List[dict], 
    predictions: List[dict], 
    image_bytes: Optional[bytes] = None, 
    image_path: str = ""
) -> Tuple[List[dict], List[dict], bool]:
    """
    Inspects image memory cache. If this image or its crops have human corrections,
    overrides the raw model predictions with the human-verified labels.
    """
    memory = sync_from_log_if_needed()
    if not memory:
        return separated_items, predictions, False

    candidate_keys = []
    if image_bytes:
        candidate_keys.append(compute_hash(image_bytes))
    if image_path:
        candidate_keys.append(image_path)
        candidate_keys.append(os.path.basename(image_path))

    # 1. Check if user previously verified this entire plate with specific items/boxes
    for key in candidate_keys:
        if key in memory and "plate_items" in memory[key] and len(memory[key]["plate_items"]) > 0:
            saved_items = memory[key]["plate_items"]
            predictions_list = [
                {"label": it["name"], "confidence": 100.0, "count": it.get("count", 1), "portion": it.get("portion", 1.0)}
                for it in saved_items
            ]
            return saved_items, predictions_list, True

    corrections_map = {}
    for key in candidate_keys:
        if key in memory and "corrections" in memory[key]:
            corrections_map.update(memory[key]["corrections"])

    if not corrections_map:
        return separated_items, predictions, False

    modified = False

    # Apply overrides to separated plate items
    for item in separated_items:
        raw_name = item.get("name", "").lower().replace('_', ' ').strip()
        orig_pred = item.get("originalPrediction", raw_name).lower().replace('_', ' ').strip()

        # Check direct match
        target_override = corrections_map.get(raw_name) or corrections_map.get(orig_pred)
        if target_override:
            item["originalPrediction"] = raw_name
            item["name"] = target_override
            item["confidence"] = 99.0
            item["needsReview"] = False
            item["human_verified"] = True
            modified = True

    # Apply overrides to predictions list
    for p in predictions:
        p_label = p.get("label", "").lower().replace('_', ' ').strip()
        target_override = corrections_map.get(p_label)
        if target_override:
            p["original_label"] = p_label
            p["label"] = target_override
            p["confidence"] = 99.0
            p["human_verified"] = True
            modified = True

    return separated_items, predictions, modified
