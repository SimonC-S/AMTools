# -*- coding: utf-8 -*-
"""
Created on Thu Nov 13 13:47:02 2025
 
@author: JarodFisher
"""
 
# -*- coding: utf-8 -*-
"""
GLOBAL Underpanel Pocket Optimizer
Finds ONE rearcuboid_length (130–160 mm) that works for ALL panel sizes
Minimizes TOTAL waste → ideally ZERO
"""
 
import numpy as np
from icecream import ic
# -------------------------------------------------
# Parameters
# -------------------------------------------------
panel_lengths_in = np.arange(14, 33)          # 14 to 32 inches → 19 sizes
pocket_lengths = np.arange(55, 65)            # 58–62 mm
perimeter_offsets = np.arange(3, 13)          # 6–12 mm
sewing_width = 1                              # mm between pockets
rearcuboid_candidates = np.arange(140, 161)   # 130–160 mm → 31 options
 
# -------------------------------------------------
# Function: Compute total waste for a fixed rearcuboid_length
# -------------------------------------------------
def compute_total_waste(rear):
    total_waste = 0.0
    n_out=0
    for length_in in panel_lengths_in:
        kodra_mm = 25.4 * (length_in - 0.5)
        best_waste = np.inf
 
        for pkt_len in pocket_lengths:
            for offset in perimeter_offsets:
                fixed = rear + 2 * offset
                available = kodra_mm - fixed
                if available <= 0:
                    continue
                max_n = int((available + sewing_width) // (pkt_len + sewing_width))
                for n in range(max_n, 0, -1):
                    used = n * pkt_len + (n - 1) * sewing_width
                    waste = available - used
                    if waste >= 0 and waste < best_waste:
                        best_waste = waste
                        n_out=n
                        if waste == 0:
                            break
                if best_waste == 0:
                    break
            if best_waste == 0:
                break
        total_waste += best_waste
        ic(n_out,max_n)
    return total_waste
 
# -------------------------------------------------
# Find BEST global rearcuboid_length
# -------------------------------------------------
print("Searching for optimal global rearcuboid_length (130–160 mm)...")
best_rear = None
min_total_waste = np.inf

waste_per_rear = []

for rear in rearcuboid_candidates:
    waste = compute_total_waste(rear)
    waste_per_rear.append((rear, waste))
    if waste < min_total_waste:
        min_total_waste = waste
        best_rear = rear
    print(f"  Rear = {rear:3d} mm → Total Waste = {waste:6.1f} mm")
 
# -------------------------------------------------
# Final Results with BEST rearcuboid
# -------------------------------------------------
print("\n" + "="*85)
print(f"OPTIMAL GLOBAL REARCUBOID LENGTH = {best_rear} mm")
print(f"MINIMUM TOTAL WASTE = {min_total_waste:.1f} mm across all 19 panels")
print("="*85)
 
# Now run full optimization with best_rear
results = []
for length_in in panel_lengths_in:
    kodra_mm = 25.4 * (length_in - 0.5)
    best_n = 0
    best_waste = np.inf
    best_pocket = None
    best_offset = None
 
    for pkt_len in pocket_lengths:
        for offset in perimeter_offsets:
            fixed = best_rear + 2 * offset
            available = kodra_mm - fixed
            if available <= 0:
                continue
            max_n = int((available + sewing_width) // (pkt_len + sewing_width))
            for n in range(max_n, 0, -1):
                used = n * pkt_len + (n - 1) * sewing_width
                waste = available - used
                if waste >= 0 and waste < best_waste:
                    best_n = n
                    best_waste = waste
                    best_pocket = pkt_len
                    best_offset = offset
                    if waste == 0:
                        break
                if best_waste == 0:
                    break
            if best_waste == 0:
                break
        if best_waste == 0:
            break

    results.append({
        'Panel': length_in,
        'Kodra_mm': kodra_mm,
        'Pockets': best_n,
        'Waste_mm': best_waste,
        'Pkt_Len': best_pocket,
        'Offset': best_offset,
        'Rear': best_rear
    })
 
# Print table
print(f"{'Panel':<6} {'Pockets':<8} {'Waste':<8} {'PktLen':<7} {'Offset':<7} {'Rear':<6} {'Kodra':<8}")
print("-" * 70)
for r in results:
    print(f"{r['Panel']:<6} {r['Pockets']:<8} {r['Waste_mm']:<8.1f} "
          f"{r['Pkt_Len']:<7} {r['Offset']:<7} {r['Rear']:<6} {r['Kodra_mm']:<8.1f}")
 
# -------------------------------------------------
# Save to CSV
# -------------------------------------------------
import pandas as pd
df = pd.DataFrame(results)
df.to_csv("global_optimal_layout.csv", index=False)
print(f"\nResults saved to 'global_optimal_layout.csv'")
 
# -------------------------------------------------
# Plot: Clean X-Axis (14–32, step 1, no dp)
# -------------------------------------------------
import matplotlib.pyplot as plt
 
pockets = [r['Pockets'] for r in results]
waste = [r['Waste_mm'] for r in results]
 
plt.figure(figsize=(12, 5))
 
# Pockets
plt.subplot(1, 2, 1)
plt.plot(panel_lengths_in, pockets, 'o-', color='tab:blue', markersize=6)
plt.title(f"Max Pockets (Rear = {best_rear} mm)", fontsize=12)
plt.xlabel("Cushion Length (inches)")
plt.ylabel("Pockets")
plt.grid(True, alpha=0.3)
plt.xticks(np.arange(14, 33, 1))
plt.gca().xaxis.set_major_formatter(plt.FormatStrFormatter('%d'))
 
# Waste
plt.subplot(1, 2, 2)
plt.plot(panel_lengths_in, waste, 's-', color='tab:red', markersize=6)
plt.title(f"Waste (Total = {min_total_waste:.1f} mm)", fontsize=12)
plt.xlabel("Cushion Length (inches)")
plt.ylabel("Waste (mm)")
plt.grid(True, alpha=0.3)
plt.xticks(np.arange(14, 33, 1))
plt.gca().xaxis.set_major_formatter(plt.FormatStrFormatter('%d'))
 
plt.tight_layout()
plt.show()
 
# -------------------------------------------------
# Summary
# -------------------------------------------------
zero_waste_panels = sum(1 for r in results if r['Waste_mm'] == 0)
print(f"\nZERO WASTE IN {zero_waste_panels}/19 PANELS")
if zero_waste_panels == 19:
    print("PERFECT GLOBAL FIT ACHIEVED!")