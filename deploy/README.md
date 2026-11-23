# Deploy Team (3 people) — folder `deploy/`

## Mission
Wrap the winning model in an API, build a clean web app, and prepare the final presentation and demo.

## You own
`deploy/api.py`, `deploy/app.py`, `deploy/dummy_model.py`, `deploy/test_api.py`, `deploy/presentation/`

## Inputs
- `modeling/best_model.joblib` and `modeling/metrics.json` (Week 3)
- The 9 input columns from `CONTRACT.md` sections 2 and 6
- Until the real model exists: `deploy/dummy_model.py` builds a tiny pipeline from `data/sample_data.csv` using `features.pipeline.build_pipeline` and Ridge. Use that.

## Outputs (exact paths)
- `deploy/api.py`, `deploy/app.py`
- `deploy/presentation/` (slide outline, demo script)

## Files to generate
| File | Contents |
|---|---|
| `deploy/api.py` | FastAPI `app`. Pydantic `PredictRequest` with the 9 input fields (allowed category values from the contract). Loads `modeling/best_model.joblib` once at startup (falls back to `deploy/dummy_model.joblib` if missing). `GET /health` -> `{"status":"ok"}`. `POST /predict` -> `{"estimated_minutes": float}` rounded to 1 decimal. Clear 422/500 errors. Must work when run from repo root. |
| `deploy/app.py` | Streamlit UI: pickup/dropoff lat/lon (or map picker), date/time, weather, traffic, vehicle, courier rating. Button calls `POST http://localhost:8000/predict`, shows the ETA. Sidebar shows metrics from `metrics.json`. |
| `deploy/dummy_model.py` | Builds and saves the temporary dummy model for early testing. |
| `deploy/test_api.py` | pytest with FastAPI `TestClient`: `/health` works, valid request returns a number, invalid weather is rejected. |
| `deploy/presentation/outline.md` | Slide outline for the whole project (2-3 slides per team) and a 5-minute live demo script. |

## Tasks
- **Week 1:** UI wireframe + API skeleton with dummy predictions.
- **Week 2:** Pydantic validation, tests with the dummy model.
- **Week 3:** switch to the real `best_model.joblib`, connect UI to API.
- **Week 4:** presentation, demo script, full rehearsal. Prepare a fallback screenshot/video in case the live demo fails.

## Run (from repo root)
```bash
uvicorn deploy.api:app --reload      # terminal 1
streamlit run deploy/app.py          # terminal 2
python -m pytest deploy/test_api.py
```

## Definition of done and PR checklist
- [ ] `/health` and `/predict` work with the real model
- [ ] Invalid input returns a clear error
- [ ] UI shows a prediction and the model metrics
- [ ] pytest passes
- [ ] Presentation outline + demo script ready
- [ ] Only files inside `deploy/` changed

## Do / Don't
- DO use only `best_model.joblib` and the 9 input columns.
- DO match the allowed category values exactly.
- DON'T re-implement feature engineering (the model pipeline already does it).
- DON'T change the schema or touch other folders.

## AI PROMPT (copy everything below)
```
I am on the deploy team. Read the master README, CONTRACT.md, and this README. Generate all the files for my team, following the contract exactly, with comments, and tell me what to run to test it. Ask me before changing anything in CONTRACT.md.
```
