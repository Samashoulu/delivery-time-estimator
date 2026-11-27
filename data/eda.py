"""Data team: make EDA plots from data/processed/cleaned_data.csv.

Run from the repo root AFTER clean_data.py:

    python data/eda.py

Plots are saved in data/eda/. Under each plot in your report, write one
sentence saying what it shows.
"""
import os

import matplotlib
matplotlib.use("Agg")  # save to files, no window needed
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

OUT = "data/eda"
os.makedirs(OUT, exist_ok=True)

df = pd.read_csv("data/processed/cleaned_data.csv")
ts = pd.to_datetime(df["order_timestamp"])
df["hour"] = ts.dt.hour

# 1. Target distribution
plt.figure(figsize=(7, 4))
df["delivery_time_minutes"].hist(bins=50)
plt.xlabel("Delivery time (minutes)")
plt.ylabel("Number of orders")
plt.title("Distribution of delivery time")
plt.tight_layout()
plt.savefig(f"{OUT}/01_delivery_time_distribution.png")
plt.close()

# 2-4. Delivery time by category
order = {
    "traffic_level": ["low", "medium", "high", "jam"],
    "weather": sorted(df["weather"].unique()),
    "vehicle_type": sorted(df["vehicle_type"].unique()),
}
for i, (col, levels) in enumerate(order.items(), start=2):
    means = df.groupby(col)["delivery_time_minutes"].mean().reindex(levels)
    plt.figure(figsize=(6, 4))
    means.plot(kind="bar")
    plt.ylabel("Average delivery time (min)")
    plt.title(f"Average delivery time by {col}")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(f"{OUT}/0{i}_time_by_{col}.png")
    plt.close()

# 5. Delivery time by hour of day
plt.figure(figsize=(7, 4))
df.groupby("hour")["delivery_time_minutes"].mean().plot(marker="o")
plt.xlabel("Hour of day")
plt.ylabel("Average delivery time (min)")
plt.title("Average delivery time by hour")
plt.tight_layout()
plt.savefig(f"{OUT}/05_time_by_hour.png")
plt.close()

# 6. Correlation heatmap (numeric columns + distance)
lat1, lon1, lat2, lon2 = [np.radians(df[c]) for c in
                          ["pickup_lat", "pickup_lon", "dropoff_lat", "dropoff_lon"]]
a = np.sin((lat2 - lat1) / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2
df["distance_km"] = 2 * 6371 * np.arcsin(np.sqrt(a))
num = df[["courier_rating", "distance_km", "hour", "delivery_time_minutes"]]
corr = num.corr()
plt.figure(figsize=(5.5, 4.5))
plt.imshow(corr, vmin=-1, vmax=1, cmap="coolwarm")
plt.colorbar()
plt.xticks(range(len(corr)), corr.columns, rotation=45, ha="right")
plt.yticks(range(len(corr)), corr.columns)
for i in range(len(corr)):
    for j in range(len(corr)):
        plt.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center", fontsize=8)
plt.title("Correlation heatmap")
plt.tight_layout()
plt.savefig(f"{OUT}/06_correlation_heatmap.png")
plt.close()

print("Summary of delivery_time_minutes:")
print(df["delivery_time_minutes"].describe().round(1).to_string())
print(f"\nSaved 6 plots in {OUT}/")
