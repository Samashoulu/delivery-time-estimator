# Data Team (3 people) — folder `data/`

## Mission
Find a real delivery dataset, clean it, map it to the canonical schema in `CONTRACT.md`, explore it, and create the fixed train/test split.

## You own
`data/raw/`, `data/processed/`, `data/notebooks/`, `data/clean_data.py`, `data/make_split.py`, `data/validate.py`, `data/eda_report.md`

## Inputs
- A real dataset you choose (e.g. a Kaggle food-delivery / delivery-time dataset with coordinates, timestamp, weather, traffic, vehicle, rating). Put the original file in `data/raw/`.
- Schema from `CONTRACT.md` section 2.

## Outputs (exact paths)
- `data/processed/cleaned_data.csv`
- `data/processed/train.csv` and `data/processed/test.csv` (80/20, `random_state=42`)
- `data/eda_report.md` and `data/notebooks/eda.ipynb`

## Files to generate
| File | Purpose |
|---|---|
| `data/clean_data.py` | `def clean(raw_path: str) -> pd.DataFrame` maps raw columns to the schema, fixes types, lowercases text, maps categories, removes impossible values (times outside 5-180, bad coordinates, rating outside 1-5), handles missing values, drops duplicates. Its `__main__` writes `cleaned_data.csv`. |
| `data/make_split.py` | `def make_split(cleaned_path: str, out_dir: str) -> None` 80/20 split, `random_state=42`, writes `train.csv` and `test.csv`. |
| `data/validate.py` | `def validate(df: pd.DataFrame) -> list[str]` returns a list of schema problems (empty list = OK). Run on all 3 CSVs. |
| `data/notebooks/eda.ipynb` | Charts: target distribution, time vs distance, time vs traffic/weather/vehicle, time by hour, correlation heatmap. |
| `data/eda_report.md` | 1 page: dataset source, cleaning decisions, top findings. |

## Tasks
- **Week 1:** choose dataset (tell the lead the name + columns), write `clean_data.py`, run it, make the split, run `validate.py`, PR to `main`. **The split must be done in Week 1.**
- **Week 2:** finish EDA notebook and report, fix issues other teams report. Do NOT regenerate the split.
- **Week 3:** support teams, answer data questions.
- **Week 4:** EDA slides for the presentation.

## Before your data is ready
Work on `data/sample_data.csv` (already in the repo, same schema). Other teams use it too.

## Definition of done and PR checklist
- [ ] `validate.py` returns no problems for all 3 CSVs
- [ ] Column names, dtypes and category values match `CONTRACT.md`
- [ ] No missing values; `delivery_time_minutes` between 5 and 180
- [ ] Split used `random_state=42` and was committed once
- [ ] `eda_report.md` written
- [ ] Only files inside `data/` changed

## Do / Don't
- DO map the real dataset onto the contract schema.
- DO tell the lead if a column is missing instead of inventing data.
- DON'T rename columns, add/remove schema columns, or change category values.
- DON'T change the split after Week 1.
- DON'T touch other folders.

## AI PROMPT (copy everything below)
```
I am on the data team. Read the master README, CONTRACT.md, and this README. Generate all the files for my team, following the contract exactly, with comments, and tell me what to run to test it. Ask me before changing anything in CONTRACT.md.
My dataset is: [paste dataset name, its column names, and 5 sample rows here]
```
