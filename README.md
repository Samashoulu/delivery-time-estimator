# Delivery Time Estimator (ETA Regression)

A 13-person group project. We predict how many minutes a delivery will take, using machine learning.

## 1. Goal and success metric
Predict `delivery_time_minutes` from pickup/dropoff location, order time, weather, traffic, vehicle type and courier rating.
- **Primary metric: MAE** (average error in minutes)
- **Secondary metric: RMSE** (punishes big misses)
- Success = a tuned tree model beats the Ridge baseline on MAE on `test.csv`, and a working web app serves live predictions.

## 2. Teams and folders
| Team | People | Folder | Mission |
|---|---|---|---|
| lead | 1 | `lead/` + root files | repo, PR reviews, integration, deadlines |
| data | 3 | `data/` | pick dataset, clean, EDA, fixed train/test split |
| features | 3 | `features/` | feature engineering pipeline |
| modeling | 3 | `modeling/` | baseline, XGBoost/LightGBM, tuning, evaluation |
| deploy | 3 | `deploy/` | FastAPI backend, Streamlit UI, final presentation |

You only edit **your own folder**.

## 3. The pipeline
```
data  ->  features  ->  modeling  ->  deploy
```
| Team | Receives | Produces |
|---|---|---|
| data | raw dataset (Kaggle etc.) | `data/processed/cleaned_data.csv`, `train.csv`, `test.csv` |
| features | `train.csv` (or `data/sample_data.csv` early) | `features/pipeline.py`, `features/preprocessor.joblib` |
| modeling | `train.csv`, `test.csv`, `features/pipeline.py` | `modeling/train.py`, `best_model.joblib`, `metrics.json` |
| deploy | `modeling/best_model.joblib`, `metrics.json` | `deploy/api.py`, `deploy/app.py`, presentation |

Exact schemas, file paths and function signatures are in **`CONTRACT.md`**. It is the single source of truth.

## 4. How to use this repo with an AI
1. Open your AI (Claude, ChatGPT, etc.).
2. Paste **this README**, then **`CONTRACT.md`**, then **your team README** (e.g. `features/README.md`).
3. Say: **"We are the [data / features / modeling / deploy] team."**
4. The AI generates ONLY your team's files, following `CONTRACT.md` exactly. Each team README ends with a ready-made AI PROMPT you can copy.
5. Put the files in your folder, run the test commands the AI gives you, then open a PR.
6. If the AI wants to change the contract, **stop and ask the lead.**

## 5. Git rules
- **Never push directly to `main`.**
- One branch per team: `team/data`, `team/features`, `team/modeling`, `team/deploy`.
- Only edit files inside your own folder.
- Open a Pull Request into `main`. The **lead reviews and merges**.
- Pull the latest `main` before you start each day: `git pull origin main`.
- Setup: `git clone <repo-url>` then `git checkout team/<yourteam>` (lead creates the branches).

```bash
python3.11 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 6. Timeline (4 weeks)
| Week | data | features | modeling | deploy |
|---|---|---|---|---|
| 1 | Choose dataset, clean it, map to schema, EDA, make `cleaned_data/train/test.csv` | Build `add_features` + `build_pipeline` on `sample_data.csv` | Baseline Ridge on `sample_data.csv` | UI wireframe + API skeleton with dummy values |
| 2 | Finish EDA report, fix data issues found | Test on real `train.csv`, save `preprocessor.joblib` | Real baseline + Random Forest on `train.csv` | Pydantic input model, API tested with a dummy model |
| 3 | Support other teams, data questions | Bug fixes, extra features only if lead approves | XGBoost + LightGBM, tuning, `best_model.joblib`, `metrics.json` | Connect real `best_model.joblib` to API and UI |
| 4 | EDA slides | Feature slides | Results slides | Final demo, presentation, rehearsal |

## 7. Definition of done (whole project)
- [ ] `cleaned_data.csv`, `train.csv`, `test.csv` exist and match the contract
- [ ] `features/pipeline.py` works on raw input rows
- [ ] `modeling/best_model.joblib` beats the Ridge baseline on MAE
- [ ] `metrics.json` shows MAE and RMSE for all 4 models
- [ ] `POST /predict` returns an ETA for a valid request
- [ ] Streamlit app shows live predictions
- [ ] Every folder has a working README and every PR was merged by the lead
- [ ] Presentation with a live demo rehearsed
