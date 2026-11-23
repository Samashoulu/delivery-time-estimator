# Modeling Team (3 people) — folder `modeling/`

## Mission
Train and compare models, tune the best ones, and ship one fitted pipeline plus honest metrics.

## You own
`modeling/train.py`, `modeling/test_train.py`, `modeling/best_model.joblib`, `modeling/metrics.json`, `modeling/notes.md`

## Inputs
- `data/processed/train.csv`, `data/processed/test.csv`
- `features/pipeline.py` -> `build_pipeline()`
- Until real data exists: `data/sample_data.csv` for both train and test (just to test the code)
- Rules: `CONTRACT.md` sections 3, 4, 5

## Outputs (exact paths)
- `modeling/best_model.joblib` (full pipeline: preprocessing + model, accepts the 9 raw input columns)
- `modeling/metrics.json` (format in `CONTRACT.md` section 5)

## Files to generate
| File | Contents |
|---|---|
| `modeling/train.py` | `def load_data(path: str) -> tuple[pd.DataFrame, pd.Series]` (drops `order_id`, splits target), `def build_models() -> dict` (`ridge`, `random_forest`, `xgboost`, `lightgbm`, all `random_state=42`), `def tune(name, pipeline, X, y)` (RandomizedSearchCV, CV on train only), `def evaluate(pipeline, X, y) -> dict` (MAE, RMSE), `def main()` with argparse `--train`, `--test`. Each model is `Pipeline([("prep", build_pipeline()), ("model", est)])`. Saves `best_model.joblib` (lowest test MAE) and `metrics.json`. |
| `modeling/test_train.py` | pytest: runs `main` on `sample_data.csv`, both output files exist, `metrics.json` has all 4 models with `mae` and `rmse`, loaded model predicts for a 1-row DataFrame. |
| `modeling/notes.md` | Results table, which model won and why, tuning ranges (for slides). |

## Tasks
- **Week 1:** Ridge baseline on `sample_data.csv`, `evaluate()` working.
- **Week 2:** real `train.csv`/`test.csv`: baseline + Random Forest.
- **Week 3:** XGBoost + LightGBM, tuning, save `best_model.joblib` and `metrics.json`, tell deploy it is ready.
- **Week 4:** results slides.

## Before upstream is ready
Use `data/sample_data.csv`. If `features/pipeline.py` is not merged yet, use a temporary stub outside the repo and do not commit it.

## Definition of done and PR checklist
- [ ] 4 models trained and listed in `metrics.json`
- [ ] Best model beats Ridge on MAE
- [ ] Tuning used cross-validation on train only; test used once for final scores
- [ ] `best_model.joblib` predicts from a raw 9-column DataFrame
- [ ] pytest passes
- [ ] Only files inside `modeling/` changed

## Do / Don't
- DO report MAE (primary) and RMSE (secondary).
- DO set `random_state=42`.
- DON'T tune on `test.csv`.
- DON'T write your own feature code; use `build_pipeline()`.
- DON'T change the schema or touch other folders.

## AI PROMPT (copy everything below)
```
I am on the modeling team. Read the master README, CONTRACT.md, and this README. Generate all the files for my team, following the contract exactly, with comments, and tell me what to run to test it. Ask me before changing anything in CONTRACT.md.
```
