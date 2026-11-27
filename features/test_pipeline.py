"""Contract tests for the delivery feature engineering pipeline."""

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import pytest
from sklearn.pipeline import Pipeline

from features.pipeline import INPUT_COLUMNS, add_features, build_pipeline


ROOT = Path(__file__).resolve().parents[1]
SAMPLE_PATH = ROOT / "data" / "sample_data.csv"
PREPROCESSOR_PATH = ROOT / "features" / "preprocessor.joblib"


def _two_row_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "order_timestamp": ["2024-03-23 12:00:00", "2024-03-25 21:00:00"],
            "pickup_lat": [0.0, 12.0],
            "pickup_lon": [0.0, 77.0],
            "dropoff_lat": [0.0, 13.0],
            "dropoff_lon": [1.0, 78.0],
            "weather": ["clear", "rain"],
            "traffic_level": ["low", "jam"],
            "vehicle_type": ["bike", "car"],
            "courier_rating": [4.0, 5.0],
        }
    )


def test_add_features_matches_contract_formulas_and_preserves_input() -> None:
    frame = _two_row_frame()
    frame["order_id"] = ["a", "b"]
    frame["delivery_time_minutes"] = [10.0, 20.0]
    original = frame.copy(deep=True)

    result = add_features(frame)

    expected_new_columns = {
        "distance_haversine_km",
        "distance_manhattan_km",
        "hour",
        "day_of_week",
        "is_weekend",
        "is_rush_hour",
        "traffic_level_num",
        "distance_x_traffic",
    }
    assert expected_new_columns.issubset(result.columns)
    pd.testing.assert_frame_equal(frame, original)
    pd.testing.assert_series_equal(result["order_id"], original["order_id"])
    pd.testing.assert_series_equal(
        result["delivery_time_minutes"], original["delivery_time_minutes"]
    )

    # One degree of longitude at the equator is about 111.195 km.
    assert result.loc[0, "distance_haversine_km"] == pytest.approx(111.1949266, abs=1e-5)
    assert result.loc[0, "distance_manhattan_km"] == pytest.approx(111.0)
    assert result["hour"].tolist() == [12, 21]
    assert result["day_of_week"].tolist() == [5, 0]
    assert result["is_weekend"].tolist() == [1, 0]
    assert result["is_rush_hour"].tolist() == [1, 0]
    assert result["traffic_level_num"].tolist() == [1, 4]
    np.testing.assert_allclose(
        result["distance_x_traffic"],
        result["distance_haversine_km"] * result["traffic_level_num"],
    )


def test_add_features_handles_one_row_and_reports_invalid_traffic() -> None:
    one_row = add_features(_two_row_frame().iloc[[0]])
    assert len(one_row) == 1
    assert one_row.iloc[0]["is_weekend"] == 1

    invalid = _two_row_frame().iloc[[0]].copy()
    invalid.loc[:, "traffic_level"] = "unknown"
    with pytest.raises(ValueError, match="Unknown traffic_level"):
        add_features(invalid)


def test_pipeline_is_unfitted_and_transforms_sample_data() -> None:
    sample = pd.read_csv(SAMPLE_PATH)
    x = sample[INPUT_COLUMNS]
    pipeline = build_pipeline()

    assert isinstance(pipeline, Pipeline)
    assert [name for name, _ in pipeline.steps] == ["add_features", "encode"]
    assert not hasattr(pipeline.named_steps["encode"], "transformers_")

    matrix = pipeline.fit_transform(x)
    assert matrix.shape[0] == len(x)
    assert np.issubdtype(matrix.dtype, np.number)
    assert np.isfinite(matrix).all()
    assert pipeline.transform(x.iloc[[0]]).shape == (1, matrix.shape[1])

    unseen = x.iloc[[0]].copy()
    unseen.loc[:, "weather"] = "new_weather"
    unseen.loc[:, "vehicle_type"] = "new_vehicle"
    assert np.isfinite(pipeline.transform(unseen)).all()


def test_saved_preprocessor_can_transform_sample_data() -> None:
    if not PREPROCESSOR_PATH.exists():
        pytest.skip("Run python -m features.save_preprocessor to create the artifact")

    sample = pd.read_csv(SAMPLE_PATH)
    pipeline = joblib.load(PREPROCESSOR_PATH)
    matrix = pipeline.transform(sample[INPUT_COLUMNS])

    assert matrix.shape[0] == len(sample)
    assert np.isfinite(matrix).all()
