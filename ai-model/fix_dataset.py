import os
from PIL import Image

# Path to your dataset (khana folder is outside ai-model)
DATASET_PATH = "../khana"

fixed = 0
skipped = 0

for root, dirs, files in os.walk(DATASET_PATH):
    for file in files:
        path = os.path.join(root, file)

        try:
            # Try opening file as image
            with Image.open(path) as img:
                rgb_img = img.convert('RGB')

                # Create new filename with .jpg
                new_path = path + ".jpg"

                rgb_img.save(new_path, "JPEG")

                # Delete old file
                os.remove(path)

                fixed += 1

        except Exception as e:
            skipped += 1

print("====================================")
print(f"✅ Fixed images: {fixed}")
print(f"⚠️ Skipped files: {skipped}")
print("====================================")