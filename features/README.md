# Features Team (3 people) — folder `features/`

## Mission
Turn raw delivery rows into model-ready features, packaged as one scikit-learn pipeline.

## You own
`features/pipeline.py`, `features/save_preprocessor.py`, `features/preprocessor.joblib`, `features/test_pipeline.py`, `features/notes.md`

## Inputs
- `data/processed/train.csv` (real, from the data team)
- Until it exists: `data/sample_data.csv` (same schema)
- Schema and feature definitions: `CONTRACT.md` sections 2 and 4

## Outputs (exact paths)
- `features/pipeline.py`
- `features/preprocessor.joblib` (pipeline fitted on train inputs)

## Files to generate
| File | Contents |
|---|---|
| `features/pipeline.py` | `def add_features(df: pd.DataFrame) -> pd.DataFrame` and `def build_pipeline() -> sklearn.pipeline.Pipeline`. Follow `CONTRACT.md` section 4 EXACTLY (column names, formulas, rush-hour hours, traffic mapping, scaler/one-hot choices). Also an `INPUT_COLUMNS` list of the 9 input columns. |
| `features/test_pipeline.py` | pytest: output has all 8 new columns, no NaNs, input df not modified, works on a 1-row df, works with or without target/order_id, `build_pipeline().fit_transform` runs on `sample_data.csv`. |
| `features/save_preprocessor.py` | Loads `train.csv`, drops `order_id` and target, fits `build_pipeline()`, saves `features/preprocessor.joblib`. |
| `features/notes.md` | Short explanation of each feature and why it helps (for slides). |

## Tasks
- **Week 1:** write `add_features` and `build_pipeline`, test on `sample_data.csv`, PR.
- **Week 2:** run on real `train.csv`, run `save_preprocessor.py`, fix bugs, PR.
- **Week 3:** support modeling with bug fixes. New features only if the lead approves (it changes the contract).
- **Week 4:** feature slides.

## Before real data is ready
Use `data/sample_data.csv`. Test: `python -m pytest features/test_pipeline.py` (from repo root).

## Definition of done and PR checklist
- [ ] Feature names and formulas match `CONTRACT.md` exactly
- [ ] `build_pipeline()` returns an UNFITTED `Pipeline` with steps `add_features` and `encode`
- [ ] Works on a raw DataFrame of the 9 input columns, including a 1-row DataFrame
- [ ] Unseen categories do not crash (`handle_unknown="ignore"`)
- [ ] pytest passes; `preprocessor.joblib` saved
- [ ] Only files inside `features/` changed

## Do / Don't
- DO keep `add_features` pure (return a copy).
- DO use `random_state=42` wherever randomness appears.
- DON'T fit anything on test data.
- DON'T change feature names or the contract without the lead.
- DON'T touch other folders.

## AI PROMPT (copy everything below)
```
I am on the features team. Read the master README, CONTRACT.md, and this README. Generate all the files for my team, following the contract exactly, with comments, and tell me what to run to test it. Ask me before changing anything in CONTRACT.md.
```
