"""Feature engineering and preprocessing for delivery ETA models."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, StandardScaler


INPUT_COLUMNS = [
    "order_timestamp",
    "pickup_lat",
    "pickup_lon",
    "dropoff_lat",
    "dropoff_lon",
    "weather",
    "traffic_level",
    "vehicle_type",
    "courier_rating",
]

TRAFFIC_LEVELS = {"low": 1, "medium": 2, "high": 3, "jam": 4}
EARTH_RADIUS_KM = 6371


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of ``df`` with the eight contract features appended.

    ``order_id`` and ``delivery_time_minutes`` may be present in ``df``; they
    are preserved here and excluded later by the preprocessing column selector.
    """
    missing = [column for column in INPUT_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(f"Missing required input columns: {missing}")

    result = df.copy()
    pickup_lat = pd.to_numeric(result["pickup_lat"], errors="raise").to_numpy(dtype=float)
    pickup_lon = pd.to_numeric(result["pickup_lon"], errors="raise").to_numpy(dtype=float)
    dropoff_lat = pd.to_numeric(result["dropoff_lat"], errors="raise").to_numpy(dtype=float)
    dropoff_lon = pd.to_numeric(result["dropoff_lon"], errors="raise").to_numpy(dtype=float)

    lat1 = np.radians(pickup_lat)
    lon1 = np.radians(pickup_lon)
    lat2 = np.radians(dropoff_lat)
    lon2 = np.radians(dropoff_lon)
    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1
    haversine_a = (
        np.sin(delta_lat / 2) ** 2
        + np.cos(lat1) * np.cos(lat2) * np.sin(delta_lon / 2) ** 2
    )
    # Floating-point rounding can put a theoretically valid value just above 1.
    haversine_a = np.clip(haversine_a, 0.0, 1.0)
    distance_haversine = 2 * EARTH_RADIUS_KM * np.arcsin(np.sqrt(haversine_a))

    mean_lat = (pickup_lat + dropoff_lat) / 2
    result["distance_haversine_km"] = distance_haversine
    result["distance_manhattan_km"] = (
        np.abs(dropoff_lat - pickup_lat) * 111.0
        + np.abs(dropoff_lon - pickup_lon) * 111.0 * np.cos(np.radians(mean_lat))
    )

    timestamp = pd.to_datetime(result["order_timestamp"], errors="raise")
    result["hour"] = timestamp.dt.hour
    result["day_of_week"] = timestamp.dt.day_of_week
    result["is_weekend"] = timestamp.dt.day_of_week.isin([5, 6]).astype("int8")
    result["is_rush_hour"] = timestamp.dt.hour.isin([12, 13, 18, 19, 20]).astype("int8")

    traffic_num = result["traffic_level"].map(TRAFFIC_LEVELS)
    if traffic_num.isna().any():
        unknown = sorted(result.loc[traffic_num.isna(), "traffic_level"].astype(str).unique())
        raise ValueError(f"Unknown traffic_level values: {unknown}")
    result["traffic_level_num"] = traffic_num.astype("int8")
    result["distance_x_traffic"] = result["distance_haversine_km"] * result["traffic_level_num"]
    return result


def build_pipeline() -> Pipeline:
    """Build the unfitted feature and encoding pipeline from CONTRACT.md."""
    encode = ColumnTransformer(
        transformers=[
            (
                "scale",
                StandardScaler(),
                [
                    "courier_rating",
                    "distance_haversine_km",
                    "distance_manhattan_km",
                    "distance_x_traffic",
                    "traffic_level_num",
                    "hour",
                    "day_of_week",
                ],
            ),
            ("binary", "passthrough", ["is_weekend", "is_rush_hour"]),
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                ["weather", "vehicle_type"],
            ),
        ],
        remainder="drop",
    )
    return Pipeline(
        steps=[
            ("add_features", FunctionTransformer(add_features)),
            ("encode", encode),
        ]
    )
