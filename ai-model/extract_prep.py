import tarfile
import os
import shutil
import glob
from sklearn.model_selection import train_test_split

DATASET_ARCHIVE = '../dataset (1).tar.gz'
DATASET_DIR = '../dataset'

def extract_archive():
    """Extracts the tar.gz archive if it exists."""
    raw_dir = os.path.join(DATASET_DIR, 'raw')
    if os.path.exists(raw_dir) and len(os.listdir(raw_dir)) > 0:
        print(f"Directory {raw_dir} already exists and is not empty. Skipping extraction step to save time.")
        return True
        
    if not os.path.exists(DATASET_ARCHIVE):
        print(f"Error: {DATASET_ARCHIVE} not found.")
        print("Please ensure your dataset is placed at the root level of the project.")
        return False
        
    print(f"Extracting {DATASET_ARCHIVE} (This may take a while for 6.9GB)...")
    with tarfile.open(DATASET_ARCHIVE, 'r:gz') as tar:
        # Extract to a temp 'raw' directory inside dataset
        tar.extractall(path=os.path.join(DATASET_DIR, 'raw'))
    print("Extraction complete.")
    return True

def organize_dataset():
    """
    Organizes the extracted raw dataset into Train, Validation, and Test folders.
    Assumes extracting creates a structure like: dataset/raw/class_name/image.jpg
    """
    raw_dir = os.path.join(DATASET_DIR, 'raw')
    if not os.path.exists(raw_dir):
        print("Raw extracted directory not found. Please check extraction process.")
        return
        
    # Check if the extracted data is nested (like inside a 'khana' folder)
    subdirs = [d for d in os.listdir(raw_dir) if os.path.isdir(os.path.join(raw_dir, d))]
    if len(subdirs) == 1:
        raw_dir = os.path.join(raw_dir, subdirs[0])
        print(f"Nested folder detected. Setting raw directory to {raw_dir}")
        
    classes = [d for d in os.listdir(raw_dir) if os.path.isdir(os.path.join(raw_dir, d))]
    
    # Create target directories
    for split in ['train', 'validation', 'test']:
        for cls in classes:
            os.makedirs(os.path.join(DATASET_DIR, split, cls), exist_ok=True)
            
    print(f"Found {len(classes)} classes. Beginning train/test/val split...")

    for cls in classes:
        cls_dir = os.path.join(raw_dir, cls)
        # Grab all files in the directory
        images = glob.glob(os.path.join(cls_dir, '*'))
        
        # Avoid non-images (macOS metadata files or directories)
        images = [img for img in images if not os.path.basename(img).startswith('._') and os.path.isfile(img)]

        # Splitting logic: 80% Train, 10% Val, 10% Test
        if len(images) < 3:
            print(f"Warning: Not enough images in {cls} to split.")
            continue
            
        train_imgs, temp_imgs = train_test_split(images, test_size=0.2, random_state=42)
        val_imgs, test_imgs = train_test_split(temp_imgs, test_size=0.5, random_state=42)

        # Move files
        def copy_files(file_list, split_dest):
            for img_path in file_list:
                file_name = os.path.basename(img_path)
                # Keras requires known extensions to load datasets from directory
                if not '.' in file_name:
                    file_name += '.jpg'
                dest = os.path.join(DATASET_DIR, split_dest, cls, file_name)
                shutil.copy2(img_path, dest)
                
        copy_files(train_imgs, 'train')
        copy_files(val_imgs, 'validation')
        copy_files(test_imgs, 'test')
        
    print("Dataset organized into train, validation, and test folders successfully.")
    
    # Note: Keras ImageDataGenerator or tf.keras.utils.image_dataset_from_directory 
    # handles resizing (224x224) and normalization efficiently during training or inference.
    # No need to pre-resize files on disk, preserving original quality if needed later.

if __name__ == "__main__":
    os.makedirs(DATASET_DIR, exist_ok=True)
    if extract_archive():
        organize_dataset()
        print("Preprocessing step complete. You may now run train.py")
