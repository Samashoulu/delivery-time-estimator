# Lead Notes — folder `lead/`

## One-time setup (Week 0)
1. Create the GitHub repo, push this scaffold to `main`.
2. Add all 12 teammates as collaborators (Settings -> Collaborators).
3. Protect `main` (Settings -> Branches): require a pull request, require 1 approval, block direct pushes.
4. Create branches: `team/data`, `team/features`, `team/modeling`, `team/deploy`.
5. Send each team: repo link, branch name, and "paste master README + CONTRACT.md + your team README into your AI, and say which team you are."
6. Rule: only the lead edits `CONTRACT.md`.

## Weekly merge order
Always merge in this order: **data -> features -> modeling -> deploy**. After each merge, tell the next team to run `git pull origin main`.

| Week | Merge checkpoint (lead) |
|---|---|
| 1 | data PR (cleaned + split CSVs), features PR (pipeline on sample data) |
| 2 | features PR (real data + preprocessor), modeling PR (baseline + RF), deploy PR (API + UI with dummy) |
| 3 | modeling PR (best model + metrics), then deploy PR (real model connected) |
| 4 | final fixes, presentation, demo rehearsal |

## Integration checklist (run after every merge)
- [ ] `pip install -r requirements.txt` works in a fresh venv
- [ ] `python -m pytest` passes for every folder
- [ ] `data/processed/` has `cleaned_data.csv`, `train.csv`, `test.csv`, no schema problems
- [ ] `python modeling/train.py` runs end to end
- [ ] `uvicorn deploy.api:app` starts and `/predict` returns a number
- [ ] `streamlit run deploy/app.py` shows a prediction
- [ ] No team edited files outside its own folder (check "Files changed" on the PR)

## PR review checklist
- [ ] Only the team's own folder changed
- [ ] `CONTRACT.md` not modified
- [ ] Column names and function signatures match the contract
- [ ] Tests pass and the author ran the code
- [ ] No large raw data or secrets committed

## Handling a contract change
1. Team opens an Issue labelled `contract-change` explaining why.
2. Lead decides, edits `CONTRACT.md`, announces in the group chat.
3. Affected teams regenerate their files with their AI (paste the new contract).
