# NutriPlate: AI Dietary Intelligence, Bioavailability & Nutrition Tracking

[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC_BY--NC_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/)
[![Institution: PCCOE Pune](https://img.shields.io/badge/Institution-PCCOE_Pune-orange.svg)](http://www.pccoepune.com/)
[![Dataset: NutriPlate-Food35](https://img.shields.io/badge/Dataset-NutriPlate--Food35-blue.svg)](https://www.kaggle.com/datasets/nutriplate/nutriplate-food35)
[![Framework: PyTorch & YOLOv8](https://img.shields.io/badge/PyTorch-CUDA_12.1-red.svg)](https://pytorch.org/)

An edge-cloud computer vision and clinical nutrition intelligence system designed for accurate, real-world Indian food detection, biochemical nutrient bioavailability estimation, and ICMR-NIN DGI 2024 dietary scoring.

---

## 🍽️ The NutriPlate-Food35 Dataset (NP-Food35)
As part of this research, we introduce **NutriPlate-Food35**, a benchmark dataset comprising **7,351 purified, high-variance raw culinary records across 35 essential Indian dietary classes**.

### Key Highlights:
1. **Solves Foundational Indian Blind Spots:** Provides native, dedicated visual class heads for everyday staples:
   * **Yellow Dal / Dal Tadka**
   * **Dal Makhani**
   * **Jeera Rice & Steamed Rice**
   * **Onion Salad (Kachumber) & Raita**
2. **Automated Watermark Purification:** 100% raw food imagery with all stock-watermarked items purged and corner stamps removed via Navier-Stokes inpainting.
3. **Synthetic Domain Randomization:** Hardened against real-world smartphone camera artifacts:
   * Gaussian lens defocus blur ($\sigma \in [1.8, 3.5]$)
   * Directional mobile camera motion-shake
   * Low-light ambient dining room luminance reduction ($0.55\text{--}0.78$)

---

## 👥 Authors & Academic Affiliation

**Department of Computer Engineering, Pimpri Chinchwad College of Engineering (PCCOE), Pune, India**

* **Adhyayan Goyal\*** (`adhyayan.goyal23@pccoepune.org`)
* **Aditya Chavan\*** (`aditya.chavan23@pccoepune.org`)
* **Likhit Chaudhary\*** (`likhit.chaudhary23@pccoepune.org`)
* **Vaishnavi Bighot\*** (`vaishnavi.bighot23@pccoepune.org`)
* **Dr. K. Rajeswari** (`kannan.rajeswari@pccoepune.org`) — *Faculty Mentor & Research Guide*

*\*Denotes equal joint co-authorship contribution.*

---

## 📦 How to Download & Use the Dataset

### Option 1: Via Kaggle (Recommended)
The full 1.38 GB dataset archive is hosted on Kaggle:
```bash
kaggle datasets download -d nutriplate/nutriplate-food35
unzip nutriplate-food35.zip
```

### Option 2: Local Regeneration
You can programmatically regenerate and augment the dataset using our automated pipeline:
```bash
python ai-model/build_new_internet_dataset.py
python ai-model/purify_dataset.py
```

---

## 🚀 Training YOLOv8 on NutriPlate-Food35 (300 Epochs)
With CUDA-enabled GPU (e.g., NVIDIA GeForce RTX 4050 6GB):
```bash
python ai-model/train_apna_khana.py
```

---

## 📜 Citation
If you utilize this repository, software, or the NutriPlate-Food35 dataset in your research, please cite:
```bibtex
@misc{goyal2026nutriplate,
  author = {Adhyayan Goyal and Aditya Chavan and Likhit Chaudhary and Vaishnavi Bighot and Dr. K. Rajeswari},
  title = {NutriPlate-Food35: A Benchmark 35-Class Robust Indian Culinary Vision Dataset with Synthetic Domain Augmentation},
  year = {2026},
  institution = {Pimpri Chinchwad College of Engineering (PCCOE), Pune},
  howpublished = {\url{https://github.com/nutriplate/nutriplate-ai}}
}
```

---

## ⚖️ License
* **Dataset:** Licensed under [Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)](datasets/new_khana_internet/LICENSE.md).
* **Software:** Proprietary research license of the authors at PCCOE Pune. See [LICENSE.md](LICENSE.md).
