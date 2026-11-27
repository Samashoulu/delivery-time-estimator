"""Fit and save the feature preprocessor using training inputs only."""

from pathlib import Path

import joblib
import pandas as pd

from features.pipeline import INPUT_COLUMNS, build_pipeline


ROOT = Path(__file__).resolve().parents[1]
TRAIN_PATH = ROOT / "data" / "processed" / "train.csv"
SAMPLE_PATH = ROOT / "data" / "sample_data.csv"
OUTPUT_PATH = ROOT / "features" / "preprocessor.joblib"


def main() -> None:
    """Fit on train.csv, falling back to the contract sample before it exists."""
    input_path = TRAIN_PATH if TRAIN_PATH.exists() else SAMPLE_PATH
    if not input_path.exists():
        raise FileNotFoundError(f"No training data found at {TRAIN_PATH} or {SAMPLE_PATH}")

    data = pd.read_csv(input_path)
    missing = [column for column in INPUT_COLUMNS if column not in data.columns]
    if missing:
        raise ValueError(f"Training data is missing required columns: {missing}")

    preprocessor = build_pipeline()
    preprocessor.fit(data[INPUT_COLUMNS])
    joblib.dump(preprocessor, OUTPUT_PATH)
    print(f"Fitted on {input_path.relative_to(ROOT)} and saved {OUTPUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
