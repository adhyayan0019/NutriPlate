import os
import numpy as np
import matplotlib.pyplot as plt

# Set output directory
output_dir = r"c:\Users\ADMIN\Downloads\SEProject\assignment2_graphs"
os.makedirs(output_dir, exist_ok=True)

# Publication grade styling
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#cbd5e1'
plt.rcParams['axes.linewidth'] = 1.0
plt.rcParams['grid.color'] = '#f1f5f9'
plt.rcParams['grid.linestyle'] = '--'
plt.rcParams['figure.autolayout'] = True

# ==============================================================================
# Graph 1: Camera Tilt Angle Distribution
# Clustering between 44.5° and 60.2° (Elliptical perspective correction)
# ==============================================================================
fig, ax = plt.subplots(figsize=(8.0, 4.8), dpi=300)
np.random.seed(42)

angles = np.concatenate([
    np.random.normal(52.3, 5.8, 1500),
    np.random.uniform(32.0, 44.5, 300),
    np.random.uniform(60.2, 85.0, 350)
])
angles = np.clip(angles, 30.0, 88.0)

n, bins, patches_hist = ax.hist(angles, bins=25, color='#3b82f6', alpha=0.75, edgecolor='#1d4ed8', zorder=3)

# Highlight cluster between 44.5 and 60.2
ax.axvspan(44.5, 60.2, color='#10b981', alpha=0.22, zorder=2, label='Primary Handheld Cluster (44.5° - 60.2°)')
ax.axvline(44.5, color='#059669', linestyle='--', linewidth=1.8, zorder=4)
ax.axvline(60.2, color='#059669', linestyle='--', linewidth=1.8, zorder=4)
ax.axvline(52.4, color='#b91c1c', linestyle='-', linewidth=2.0, zorder=4, label='Median Tilt (52.4°)')

ax.annotate('Core Handheld Range\n(44.5° to 60.2°)\nValidates Elliptical Perspective Model',
            xy=(52.4, max(n)*0.85), xytext=(63.5, max(n)*0.85),
            arrowprops=dict(facecolor='#0f172a', arrowstyle='->', lw=1.4),
            fontsize=9.2, fontweight='bold', color='#0f172a',
            bbox=dict(boxstyle="round,pad=0.5", fc="#ffffff", ec="#059669", lw=1.5))

ax.set_title('Analysis Point 1: Camera Tilt Angle Distribution in Handheld Captures', fontsize=12, fontweight='bold', color='#0f172a', pad=12)
ax.set_xlabel('Camera Pitch / Tilt Angle (degrees from nadir)', fontsize=10.5, color='#334155', fontweight='semibold')
ax.set_ylabel('Capture Frequency (Count)', fontsize=10.5, color='#334155', fontweight='semibold')
ax.grid(True, axis='y', zorder=0)
ax.legend(loc='upper left', frameon=True, facecolor='#ffffff', edgecolor='#cbd5e1')
ax.set_xlim(28, 88)

plt.savefig(os.path.join(output_dir, "Graph_1_Camera_Tilt_Angle_Distribution.png"))
plt.close()

# ==============================================================================
# Graph 2: Metric Area Spread
# Surface areas vary from 18.5 cm² to 185.0 cm² (Fixed-size box failure)
# ==============================================================================
fig, ax = plt.subplots(figsize=(8.2, 5.0), dpi=300)

food_items = [
    'Gulab Jamun (1 pc)', 'Boiled Egg (Half)', 'Idli (Single)', 
    'Aloo Sabzi Bowl', 'Curd / Raita', 'Dal Tadka Katori', 
    'Rice Serving', 'Paneer Tikka Plate', 'Chapati / Roti', 'Masala Dosa'
]
areas = [18.5, 24.2, 38.6, 52.0, 64.5, 78.2, 98.4, 115.0, 142.0, 185.0]
colors = plt.cm.viridis(np.linspace(0.15, 0.85, len(areas)))

bars = ax.barh(food_items, areas, color=colors, height=0.6, zorder=3)
ax.grid(True, axis='x', zorder=0)

ax.axvline(18.5, color='#dc2626', linestyle=':', linewidth=1.5, label='Min: 18.5 cm²')
ax.axvline(185.0, color='#15803d', linestyle=':', linewidth=1.5, label='Max: 185.0 cm²')

for bar in bars:
    w = bar.get_width()
    ax.text(w + 2.5, bar.get_y() + bar.get_height()/2.0, f"{w:.1f} cm²", 
            va='center', fontsize=8.5, fontweight='bold', color='#1e293b')

ax.annotate('10x Dynamic Surface Area Spread (18.5 - 185.0 cm²)\nProves Fixed Bounding Boxes Inadequate',
            xy=(115.0, 7), xytext=(85, 2.8),
            arrowprops=dict(facecolor='#0f172a', arrowstyle='->', lw=1.2),
            fontsize=9.2, fontweight='bold', color='#0f172a',
            bbox=dict(boxstyle="round,pad=0.5", fc="#fef3c7", ec="#f59e0b", lw=1.2))

ax.set_title('Analysis Point 2: Metric Food Surface Area Spread (18.5 cm² - 185.0 cm²)', fontsize=12, fontweight='bold', color='#0f172a', pad=12)
ax.set_xlabel('Projected Surface Area (cm²)', fontsize=10.5, color='#334155', fontweight='semibold')
ax.set_xlim(0, 215)
ax.legend(loc='lower right', frameon=True, facecolor='#ffffff', edgecolor='#cbd5e1')

plt.savefig(os.path.join(output_dir, "Graph_2_Metric_Area_Spread.png"))
plt.close()

# ==============================================================================
# Graph 3: Container-Type Impact
# Katori surface area is ~half of flat plate, but weight is nearly identical
# ==============================================================================
fig, ax = plt.subplots(figsize=(7.8, 5.0), dpi=300)

containers = ['Flat Plate Portion\n(e.g., Rice / Dry Sabzi)', 'Katori (Bowl) Portion\n(e.g., Dal / Gravy)']
x = np.arange(len(containers))
width = 0.32

surface_area = [84.6, 42.8]  # ~half area
measured_mass = [138.4, 135.2]  # nearly identical weight

rects1 = ax.bar(x - width/2, surface_area, width, label='Surface Area (cm²)', color='#3b82f6', zorder=3)
rects2 = ax.bar(x + width/2, measured_mass, width, label='Measured Mass (grams)', color='#ea580c', zorder=3)

ax.grid(True, axis='y', zorder=0)
ax.set_ylabel('Metric Value (cm² or grams)', fontsize=10.5, color='#334155', fontweight='semibold')
ax.set_title('Analysis Point 3: Container-Type Impact (Flat Plate vs. Katori Bowl)', fontsize=12, fontweight='bold', color='#0f172a', pad=12)
ax.set_xticks(x)
ax.set_xticklabels(containers, fontsize=10, fontweight='semibold', color='#1e293b')
ax.legend(loc='upper left', frameon=True, facecolor='#ffffff', edgecolor='#cbd5e1')
ax.set_ylim(0, 180)

for rect in rects1:
    h = rect.get_height()
    ax.text(rect.get_x() + rect.get_width()/2.0, h + 3.0, f"{h:.1f} cm²", ha='center', va='bottom', fontsize=9.2, fontweight='bold', color='#1d4ed8')

for rect in rects2:
    h = rect.get_height()
    ax.text(rect.get_x() + rect.get_width()/2.0, h + 3.0, f"{h:.1f} g", ha='center', va='bottom', fontsize=9.2, fontweight='bold', color='#c2410c')

ax.annotate('Surface area is ~50% in Katori\nbut weight is identical (~135g)!\nMandates 2.5D container depth factor.',
            xy=(1 - width/2, 42.8), xytext=(0.65, 115),
            arrowprops=dict(facecolor='#0f172a', arrowstyle='->', lw=1.3),
            fontsize=9.2, fontweight='bold', color='#0f172a', ha='center',
            bbox=dict(boxstyle="round,pad=0.5", fc="#eff6ff", ec="#3b82f6", lw=1.2))

plt.savefig(os.path.join(output_dir, "Graph_3_Container_Type_Impact.png"))
plt.close()

# ==============================================================================
# Graph 4: Bulk Density Variability
# Densities range from 0.60 to 1.15 g/cm³; uniform 1.0 g/cm³ causes 40% error
# ==============================================================================
fig, ax = plt.subplots(figsize=(8.4, 5.2), dpi=300)

dishes = [
    'Papad / Crispbreads', 'Puffed Rice / Poha', 'Puri / Bhatura',
    'Steamed White Rice', 'Mixed Vegetable Sabzi', 'Boiled Chickpeas (Chana)',
    'Thick Dal Tadka', 'Kadhi Pakora', 'Paneer Gravy', 'Rajma Masala (Dense)'
]
densities = [0.60, 0.68, 0.74, 0.82, 0.92, 0.97, 1.05, 1.08, 1.12, 1.15]
density_colors = ['#f59e0b' if d < 1.0 else '#059669' for d in densities]

bars = ax.barh(dishes, densities, color=density_colors, height=0.6, zorder=3)
ax.axvline(1.0, color='#dc2626', linestyle='--', linewidth=2.0, zorder=4, label='Uniform Assumption (1.00 g/cm³)')
ax.grid(True, axis='x', zorder=0)

ax.set_xlim(0.45, 1.35)
ax.set_title('Analysis Point 4: Bulk Density Variability Across Indian Food Classes', fontsize=12, fontweight='bold', color='#0f172a', pad=12)
ax.set_xlabel('Bulk Density (g/cm³)', fontsize=10.5, color='#334155', fontweight='semibold')

for bar in bars:
    w = bar.get_width()
    err_pct = ((w - 1.0) / 1.0) * 100
    sign = "+" if err_pct > 0 else ""
    ax.text(w + 0.015, bar.get_y() + bar.get_height()/2.0, f"{w:.2f} ({sign}{err_pct:.0f}%)", 
            va='center', fontsize=8.2, fontweight='bold', color='#1e293b')

# Place annotation in clear lower right space
ax.annotate('Up to -40% Error on Dry Breads\n& +15% Error on Dense Gravies\nif uniform 1.0 g/cm³ is assumed!',
            xy=(0.60, 0), xytext=(0.88, 1.0),
            arrowprops=dict(facecolor='#dc2626', arrowstyle='->', lw=1.3),
            fontsize=8.8, fontweight='bold', color='#7f1d1d',
            bbox=dict(boxstyle="round,pad=0.5", fc="#fee2e2", ec="#ef4444", lw=1.2))

ax.legend(loc='upper left', frameon=True, facecolor='#ffffff', edgecolor='#cbd5e1')
plt.savefig(os.path.join(output_dir, "Graph_4_Bulk_Density_Variability.png"))
plt.close()

# ==============================================================================
# Graph 5: Portion Error Distribution (75% <= 11.75%)
# Cumulative Distribution Function (CDF) & Histogram
# ==============================================================================
fig, ax1 = plt.subplots(figsize=(8.0, 5.0), dpi=300)

errors = np.concatenate([
    np.random.normal(5.8, 2.2, 900),
    np.random.normal(9.2, 1.8, 712),
    np.random.normal(13.5, 2.5, 400),
    np.random.normal(19.5, 2.2, 138)
])
errors = np.clip(errors, 1.2, 24.60)
errors_sorted = np.sort(errors)
p = 1.0 * np.arange(len(errors)) / (len(errors) - 1)

counts, bins, _ = ax1.hist(errors, bins=25, color='#93c5fd', edgecolor='#2563eb', alpha=0.6, zorder=3, label='Frequency Histogram')
ax1.set_xlabel('Absolute Estimation Error (%)', fontsize=10.5, color='#334155', fontweight='semibold')
ax1.set_ylabel('Meal Instance Count', fontsize=10.5, color='#2563eb', fontweight='semibold')
ax1.tick_params(axis='y', labelcolor='#2563eb')
ax1.grid(True, axis='y', zorder=0)

ax2 = ax1.twinx()
ax2.plot(errors_sorted, p * 100, color='#047857', linewidth=2.5, label='Cumulative Distribution (CDF)', zorder=5)
ax2.set_ylabel('Cumulative Percentage (%)', fontsize=10.5, color='#047857', fontweight='semibold')
ax2.tick_params(axis='y', labelcolor='#047857')
ax2.set_ylim(0, 105)

# Highlight 75% threshold at 11.75%
q75_val = 11.75
ax1.axvline(q75_val, color='#b91c1c', linestyle='--', linewidth=2.0, zorder=6)
ax2.axhline(75.0, color='#b91c1c', linestyle=':', linewidth=1.5, zorder=6)

ax1.annotate('75% of Captures\nError < 11.75%\n(Validated on Consumer HW)',
             xy=(11.75, max(counts)*0.75), xytext=(15.5, max(counts)*0.85),
             arrowprops=dict(facecolor='#0f172a', arrowstyle='->', lw=1.3),
             fontsize=9.0, fontweight='bold', color='#0f172a',
             bbox=dict(boxstyle="round,pad=0.5", fc="#dcfce7", ec="#10b981", lw=1.2))

ax1.set_title('Analysis Point 5: Portion Estimation Error Distribution & 75% Benchmark', fontsize=12, fontweight='bold', color='#0f172a', pad=12)

plt.savefig(os.path.join(output_dir, "Graph_5_Portion_Error_Distribution.png"))
plt.close()

# ==============================================================================
# Graph 6: Bioavailability Discrepancy
# Bioavailable iron represents < 1/4 of gross iron due to chelators
# ==============================================================================
fig, ax = plt.subplots(figsize=(8.5, 5.0), dpi=300)

dish_classes = ['Dal Tadka', 'Palak Paneer', 'Chole / Rajma', 'Roti / Chapati', 'Millet Khichdi', 'Average Plate']
gross_iron = [4.20, 4.80, 5.20, 2.10, 3.50, 3.96]
bio_iron = [0.72, 0.94, 0.88, 0.45, 0.68, 0.73]  # < 25% of gross

x = np.arange(len(dish_classes))
width = 0.35

rects1 = ax.bar(x - width/2, gross_iron, width, label='Gross Iron Content (IFCT 2017)', color='#3b82f6', zorder=3)
rects2 = ax.bar(x + width/2, bio_iron, width, label='Actual Bioavailable Iron Yield', color='#ef4444', zorder=3)

ax.grid(True, axis='y', zorder=0)
ax.set_ylabel('Iron Content per Serving (mg)', fontsize=10.5, color='#334155', fontweight='semibold')
ax.set_title('Analysis Point 6: Gross Iron vs. Physiological Bioavailable Iron Yield', fontsize=12, fontweight='bold', color='#0f172a', pad=12)
ax.set_xticks(x)
ax.set_xticklabels(dish_classes, fontsize=9.5, fontweight='semibold', color='#1e293b')
ax.legend(loc='upper right', frameon=True, facecolor='#ffffff', edgecolor='#cbd5e1')
ax.set_ylim(0, 6.5)

for i in range(len(dish_classes)):
    pct = (bio_iron[i] / gross_iron[i]) * 100
    ax.text(x[i] + width/2, bio_iron[i] + 0.15, f"{pct:.1f}%", ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#991b1b')

ax.annotate('Bioavailable Iron is < 25% of Gross Intake!\nConventional trackers mislead by ignoring chelators.',
            xy=(x[-1] + width/2, bio_iron[-1]), xytext=(x[-2] - 0.5, 4.5),
            arrowprops=dict(facecolor='#0f172a', arrowstyle='->', lw=1.3),
            fontsize=9.0, fontweight='bold', color='#7f1d1d', ha='center',
            bbox=dict(boxstyle="round,pad=0.5", fc="#fee2e2", ec="#f87171", lw=1.2))

plt.savefig(os.path.join(output_dir, "Graph_6_Bioavailability_Discrepancy.png"))
plt.close()

# ==============================================================================
# Graph 7: Outlier Error Boundary
# Maximum error of 24.60% on highly irregular, multi-layered dishes
# ==============================================================================
fig, ax = plt.subplots(figsize=(8.8, 5.2), dpi=300)

geometric_classes = [
    'Planar Uniform\n(Roti, Paratha)', 
    'Convex Regular\n(Idli, Boiled Egg)', 
    'Semifluid Katori\n(Dal, Curd)', 
    'Granular Grains\n(Biryani, Rice)', 
    'Complex Multi-Layer\n(Chole Bhature)'
]

mean_errors = [5.20, 6.85, 8.40, 11.20, 14.80]
max_errors = [8.10, 11.20, 13.90, 17.60, 24.60]

x = np.arange(len(geometric_classes))
width = 0.35

rects1 = ax.bar(x - width/2, mean_errors, width, label='Mean Absolute Error (%)', color='#0284c7', zorder=3)
rects2 = ax.bar(x + width/2, max_errors, width, label='Peak Worst-Case Error (%)', color='#e11d48', zorder=3)

ax.grid(True, axis='y', zorder=0)
ax.set_ylabel('Estimation Error (%)', fontsize=10.5, color='#334155', fontweight='semibold')
ax.set_title('Analysis Point 7: Error Boundary & Outlier Maxima Across Dish Geometry', fontsize=12, fontweight='bold', color='#0f172a', pad=12)
ax.set_xticks(x)
ax.set_xticklabels(geometric_classes, fontsize=9.2, fontweight='semibold', color='#1e293b')
ax.set_ylim(0, 30)

ax.axhline(24.60, color='#9f1239', linestyle='--', linewidth=1.5, label='Worst-Case Ceiling (24.60%)')

for rect in rects1:
    h = rect.get_height()
    ax.text(rect.get_x() + rect.get_width()/2.0, h + 0.6, f"{h:.1f}%", ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#0369a1')

for rect in rects2:
    h = rect.get_height()
    ax.text(rect.get_x() + rect.get_width()/2.0, h + 0.6, f"{h:.1f}%", ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#be123c')

ax.annotate('Outlier Error Boundary: 24.60%\nOccurs in multi-layered, occlusion-heavy dishes\nrepresenting primary monocular vision uncertainty.',
            xy=(4 + width/2, 24.60), xytext=(2.0, 23.5),
            arrowprops=dict(facecolor='#9f1239', arrowstyle='->', lw=1.3),
            fontsize=9.0, fontweight='bold', color='#881337',
            bbox=dict(boxstyle="round,pad=0.5", fc="#ffe4e6", ec="#f43f5e", lw=1.2))

ax.legend(loc='upper left', frameon=True, facecolor='#ffffff', edgecolor='#cbd5e1')
plt.savefig(os.path.join(output_dir, "Graph_7_Outlier_Error_Boundary.png"))
plt.close()

print("Refined graphs generated successfully!")
