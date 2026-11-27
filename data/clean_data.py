"""Data team: clean the raw Amazon delivery dataset into the CONTRACT.md schema.

Run from the repo root (the folder that contains README.md):

    python data/clean_data.py
    python data/clean_data.py --raw data/raw/amazon_delivery.csv

Produces:
    data/processed/cleaned_data.csv
    data/processed/train.csv
    data/processed/test.csv
"""
import argparse
import os

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

SEED = 42  # CONTRACT: random seed everywhere is 42
RAW_DEFAULT = "data/raw/amazon_delivery.csv"
OUT_DIR = "data/processed"

# ---------------------------------------------------------------------------
# DECISIONS TO CONFIRM WITH THE LEAD (write the final answer in data/README.md)
# The contract only allows these values, so the raw categories must be mapped.
# Any raw value NOT in a map below is dropped (and the count is printed).
# ---------------------------------------------------------------------------
WEATHER_MAP = {
    "sunny": "clear",
    "windy": "clear",       # DECISION: windy -> clear
    "cloudy": "cloudy",
    "fog": "fog",
    "stormy": "storm",
    "sandstorms": "storm",  # DECISION: sandstorms -> storm
    # NOTE: the raw data has no "rain", so "rain" will have zero rows.
}
TRAFFIC_MAP = {"low": "low", "medium": "medium", "high": "high", "jam": "jam"}
VEHICLE_MAP = {
    "motorcycle": "bike",   # DECISION: motorcycle -> bike
    "bicycle": "bike",
    "scooter": "scooter",
    "van": "car",           # DECISION: van -> car
}

# Rows outside these limits are removed (CONTRACT rules + one sanity filter).
MIN_MINUTES, MAX_MINUTES = 5, 180
MAX_DISTANCE_KM = 100  # DECISION: drop rows with impossible pickup->dropoff distance

RENAME = {
    "Order_ID": "order_id",
    "Store_Latitude": "pickup_lat",
    "Store_Longitude": "pickup_lon",
    "Drop_Latitude": "dropoff_lat",
    "Drop_Longitude": "dropoff_lon",
    "Weather": "weather",
    "Traffic": "traffic_level",
    "Vehicle": "vehicle_type",
    "Agent_Rating": "courier_rating",
    "Delivery_Time": "delivery_time_minutes",
}

# CONTRACT section 2: exact column order
FINAL_COLUMNS = [
    "order_id", "order_timestamp", "pickup_lat", "pickup_lon",
    "dropoff_lat", "dropoff_lon", "weather", "traffic_level",
    "vehicle_type", "courier_rating", "delivery_time_minutes",
]


def haversine_km(lat1, lon1, lat2, lon2):
    """Distance in km between two points (Earth radius 6371, as in the contract)."""
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    a = (np.sin((lat2 - lat1) / 2) ** 2
         + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2)
    return 2 * 6371 * np.arcsin(np.sqrt(a))


def log_drop(step, before, after):
    print(f"  {step:<45} dropped {before - after:>6}  (left: {after})")


def clean(raw: pd.DataFrame) -> pd.DataFrame:
    print(f"Raw rows: {len(raw)}")
    df = raw.copy()

    # 1. Build order_timestamp from Order_Date + Order_Time
    ts = pd.to_datetime(
        df["Order_Date"].astype(str).str.strip() + " " + df["Order_Time"].astype(str).str.strip(),
        errors="coerce",
    )
    df["order_timestamp"] = ts.dt.strftime("%Y-%m-%d %H:%M:%S")
    n = len(df)
    df = df[ts.notna()]
    log_drop("missing/unparseable order date or time", n, len(df))

    # 2. Rename to contract names, keep only what we need
    df = df.rename(columns=RENAME)
    df = df[[c for c in FINAL_COLUMNS if c in df.columns]].copy()

    # 3. Text columns: strip spaces, lowercase, then map to allowed contract values
    for col, mapping in [("weather", WEATHER_MAP),
                         ("traffic_level", TRAFFIC_MAP),
                         ("vehicle_type", VEHICLE_MAP)]:
        cleaned = df[col].astype(str).str.strip().str.lower()
        mapped = cleaned.map(mapping)
        unmapped = sorted(set(cleaned[mapped.isna()]))
        if unmapped:
            print(f"  {col}: values not in map (rows dropped): {unmapped}")
        df[col] = mapped
        n = len(df)
        df = df[df[col].notna()]
        log_drop(f"unmapped {col}", n, len(df))

    # 4. Numeric columns
    num_cols = ["pickup_lat", "pickup_lon", "dropoff_lat", "dropoff_lon",
                "courier_rating", "delivery_time_minutes"]
    for col in num_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    n = len(df)
    df = df.dropna(subset=num_cols)
    log_drop("missing numeric values (rating, coords, time)", n, len(df))

    # 5. Coordinates: zeros and out-of-range values are bad data
    coords = ["pickup_lat", "pickup_lon", "dropoff_lat", "dropoff_lon"]
    n = len(df)
    df = df[(df[coords] != 0).all(axis=1)]
    log_drop("zero coordinates", n, len(df))
    n = len(df)
    df = df[df["pickup_lat"].between(-90, 90) & df["dropoff_lat"].between(-90, 90)
            & df["pickup_lon"].between(-180, 180) & df["dropoff_lon"].between(-180, 180)]
    log_drop("coordinates out of range", n, len(df))

    # 6. Impossible distances
    dist = haversine_km(df["pickup_lat"], df["pickup_lon"], df["dropoff_lat"], df["dropoff_lon"])
    n = len(df)
    df = df[dist <= MAX_DISTANCE_KM]
    log_drop(f"distance over {MAX_DISTANCE_KM} km", n, len(df))

    # 7. Contract ranges
    n = len(df)
    df = df[df["courier_rating"].between(1.0, 5.0)]
    log_drop("courier_rating outside 1-5", n, len(df))
    n = len(df)
    df = df[df["delivery_time_minutes"].between(MIN_MINUTES, MAX_MINUTES)]
    log_drop(f"delivery time outside {MIN_MINUTES}-{MAX_MINUTES} min", n, len(df))

    # 8. Duplicate orders
    n = len(df)
    df = df.drop_duplicates(subset="order_id")
    log_drop("duplicate order_id", n, len(df))

    df["order_id"] = df["order_id"].astype(str)
    df = df[FINAL_COLUMNS].reset_index(drop=True)
    print(f"Clean rows: {len(df)}")
    return df


def validate(df: pd.DataFrame, name: str) -> None:
    """Check every CONTRACT rule. Raises AssertionError if something is wrong."""
    assert list(df.columns) == FINAL_COLUMNS, f"{name}: wrong columns {list(df.columns)}"
    assert df.isna().sum().sum() == 0, f"{name}: has missing values"
    assert df["order_id"].is_unique, f"{name}: order_id not unique"
    pd.to_datetime(df["order_timestamp"], format="%Y-%m-%d %H:%M:%S")  # raises if bad format
    assert df["pickup_lat"].between(-90, 90).all() and df["dropoff_lat"].between(-90, 90).all()
    assert df["pickup_lon"].between(-180, 180).all() and df["dropoff_lon"].between(-180, 180).all()
    assert df["weather"].isin(["clear", "cloudy", "rain", "fog", "storm"]).all()
    assert df["traffic_level"].isin(["low", "medium", "high", "jam"]).all()
    assert df["vehicle_type"].isin(["bike", "scooter", "car"]).all()
    assert df["courier_rating"].between(1.0, 5.0).all()
    assert df["delivery_time_minutes"].between(5, 180).all()
    for col in ["weather", "traffic_level", "vehicle_type"]:
        assert (df[col] == df[col].str.lower()).all(), f"{name}: {col} not lowercase"
    print(f"  OK  {name}: {df.shape[0]} rows, {df.shape[1]} columns")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", default=RAW_DEFAULT, help="path to the raw Kaggle CSV")
    args = parser.parse_args()

    if not os.path.exists(args.raw):
        raise SystemExit(f"Raw file not found: {args.raw}\n"
                         "Download amazon_delivery.csv from Kaggle and put it there.")

    raw = pd.read_csv(args.raw)
    df = clean(raw)

    # CONTRACT: 80/20 split, made ONCE
    train, test = train_test_split(df, test_size=0.2, random_state=SEED, shuffle=True)

    os.makedirs(OUT_DIR, exist_ok=True)
    df.to_csv(f"{OUT_DIR}/cleaned_data.csv", index=False)
    train.to_csv(f"{OUT_DIR}/train.csv", index=False)
    test.to_csv(f"{OUT_DIR}/test.csv", index=False)

    print("\nValidating against CONTRACT.md:")
    for name in ["cleaned_data", "train", "test"]:
        validate(pd.read_csv(f"{OUT_DIR}/{name}.csv", keep_default_na=False), name)

    sample = "data/sample_data.csv"
    if os.path.exists(sample):
        same = list(pd.read_csv(sample, nrows=1).columns) == FINAL_COLUMNS
        print(f"  Columns match data/sample_data.csv: {same}")

    print("\nCategory counts (put these in your EDA report):")
    for col in ["weather", "traffic_level", "vehicle_type"]:
        print(df[col].value_counts().to_string(), "\n")


if __name__ == "__main__":
    main()
