# CONTRACT.md — Rules every team must follow

**Owner: Project Lead only.** Nobody else edits this file. If you need a change, open a GitHub Issue labelled `contract-change`. The lead approves, edits, and tells everyone.

If your AI wants to change anything here, **stop and ask the lead.**

---

## 1. Environment
- Python **3.11**
- Random seed everywhere: **42**
- Library versions: see `requirements.txt` (do not upgrade or add libraries without telling the lead)
- **Always run code from the repo root** (the folder containing README.md). Imports look like `from features.pipeline import build_pipeline`.
- Naming: `snake_case` for columns, functions, files. Branches: `team/<name>`.

## 2. Canonical dataset schema
Every dataset handed between teams uses EXACTLY these column names.

| Column | Type | Rules |
|---|---|---|
| `order_id` | str | unique, identifier only, never used as a feature |
| `order_timestamp` | str | format `YYYY-MM-DD HH:MM:SS` (parse with `pd.to_datetime`) |
| `pickup_lat` | float | -90 to 90 |
| `pickup_lon` | float | -180 to 180 |
| `dropoff_lat` | float | -90 to 90 |
| `dropoff_lon` | float | -180 to 180 |
| `weather` | str | one of: `clear`, `cloudy`, `rain`, `fog`, `storm` |
| `traffic_level` | str | one of: `low`, `medium`, `high`, `jam` |
| `vehicle_type` | str | one of: `bike`, `scooter`, `car` |
| `courier_rating` | float | 1.0 to 5.0 |
| `delivery_time_minutes` | float | **TARGET.** Between 5 and 180 |

- All text values are **lowercase**.
- `cleaned_data.csv`, `train.csv`, `test.csv` have **no missing values**.
- The 9 **input columns** (everything except `order_id` and the target) are:
  `order_timestamp, pickup_lat, pickup_lon, dropoff_lat, dropoff_lon, weather, traffic_level, vehicle_type, courier_rating`
- The data team maps the real dataset columns/categories onto these names (e.g. "Heavy" traffic -> `high`). If the real dataset lacks a column, the data team tells the lead BEFORE inventing values.
- `data/sample_data.csv` is a small fake file in this exact schema so every team can start in Week 1.

## 3. File handoffs (exact paths)
| File | Made by | Used by |
|---|---|---|
| `data/processed/cleaned_data.csv` | data | features, modeling |
| `data/processed/train.csv` | data | features, modeling |
| `data/processed/test.csv` | data | modeling |
| `features/pipeline.py` | features | modeling, deploy (indirectly) |
| `features/preprocessor.joblib` | features | modeling (optional) |
| `modeling/train.py` | modeling | everyone |
| `modeling/best_model.joblib` | modeling | deploy |
| `modeling/metrics.json` | modeling | deploy, presentation |
| `deploy/api.py`, `deploy/app.py` | deploy | final demo |

**Split rule:** 80% train / 20% test, `train_test_split(test_size=0.2, random_state=42, shuffle=True)`. Made ONCE by the data team. Never regenerated after Week 1 ends. `train.csv` and `test.csv` have the same columns as `cleaned_data.csv`.

## 4. Features team interface — `features/pipeline.py`

```python
def add_features(df: pd.DataFrame) -> pd.DataFrame: ...
def build_pipeline() -> sklearn.pipeline.Pipeline: ...
```

**`add_features(df)`**
- Input: DataFrame with the 9 input columns (target and `order_id` may or may not be present; ignore them).
- Returns a **copy** with these EXTRA columns added (original columns kept):

| New column | Definition |
|---|---|
| `distance_haversine_km` | Haversine distance pickup->dropoff in km (Earth radius 6371) |
| `distance_manhattan_km` | `abs(dlat)*111.0 + abs(dlon)*111.0*cos(radians(mean_lat))` |
| `hour` | hour of `order_timestamp` (0-23) |
| `day_of_week` | 0=Monday ... 6=Sunday |
| `is_weekend` | 1 if Saturday/Sunday else 0 |
| `is_rush_hour` | 1 if hour in {12, 13, 18, 19, 20} else 0 |
| `traffic_level_num` | low=1, medium=2, high=3, jam=4 |
| `distance_x_traffic` | `distance_haversine_km * traffic_level_num` |

**`build_pipeline()`** returns an **unfitted** sklearn `Pipeline` with two steps:
1. `"add_features"`: `FunctionTransformer(add_features)`
2. `"encode"`: `ColumnTransformer` with
   - `StandardScaler` on: `courier_rating, distance_haversine_km, distance_manhattan_km, distance_x_traffic, traffic_level_num, hour, day_of_week`
   - passthrough on: `is_weekend, is_rush_hour`
   - `OneHotEncoder(handle_unknown="ignore", sparse_output=False)` on: `weather, vehicle_type`
   - `remainder="drop"` (drops raw lat/lon, timestamp, order_id, target)

The pipeline accepts a **raw DataFrame with the 9 input columns** and outputs a numeric matrix. That is why deploy never has to redo feature engineering.

`features/preprocessor.joblib` = `build_pipeline()` fitted on the input columns of `train.csv`.

## 5. Modeling team interface — `modeling/train.py`
- Run: `python modeling/train.py` (optional args `--train PATH --test PATH`, defaults `data/processed/train.csv` and `data/processed/test.csv`).
- Models compared: `ridge` (baseline), `random_forest`, `xgboost`, `lightgbm`.
- Each model = `Pipeline([("prep", build_pipeline()), ("model", estimator)])`, trained on **train.csv only**. Tuning uses cross-validation on train only. **test.csv is used only for the final scores.**
- Target = `delivery_time_minutes`. Drop `order_id` and the target before fitting.
- Saves `modeling/best_model.joblib`: the full fitted pipeline of the model with the lowest test **MAE**. Accepts a DataFrame of the 9 input columns, returns minutes.
- Saves `modeling/metrics.json`:
```json
{
  "metric_for_selection": "mae",
  "best_model": "xgboost",
  "models": {
    "ridge": {"mae": 0.0, "rmse": 0.0},
    "random_forest": {"mae": 0.0, "rmse": 0.0},
    "xgboost": {"mae": 0.0, "rmse": 0.0},
    "lightgbm": {"mae": 0.0, "rmse": 0.0}
  }
}
```
- Unpickling needs `features.pipeline` importable, so run from repo root.

## 6. Deploy team interface
- Uses ONLY `modeling/best_model.joblib` and the 9 input columns. No feature code of its own.
- `deploy/api.py` (FastAPI):
  - `GET /health` -> `{"status": "ok"}`
  - `POST /predict` with JSON body = the 9 input columns (`order_timestamp` as string), returns `{"estimated_minutes": <float rounded to 1 decimal>}`
- `deploy/app.py` (Streamlit): form for the 9 inputs, calls `POST http://localhost:8000/predict`, shows the ETA.
- Run API: `uvicorn deploy.api:app --reload` (from repo root). Run UI: `streamlit run deploy/app.py`.

## 7. Folder ownership
| Folder | Owner | Everyone else |
|---|---|---|
| `data/` | data | read only |
| `features/` | features | read only |
| `modeling/` | modeling | read only |
| `deploy/` | deploy | read only |
| `lead/`, root files | lead | read only |
