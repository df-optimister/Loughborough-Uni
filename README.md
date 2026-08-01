# Tracking-Enhanced VAEP

Extending the VAEP (Valuing Actions by Estimating Probabilities) action-valuation framework with spatial context derived from StatsBomb 360 freeze-frame tracking data — built as an MSc dissertation project.

---

## The Problem

Standard VAEP values actions using only on-ball event data (pass, shot, dribble, ...), so it has no way to see defensive shape or off-ball movement. Two identical passes into the same space can have very different value depending on whether the defensive line is collapsing behind them — event data alone can't tell them apart. This project tests whether adding freeze-frame-derived spatial features closes that gap.

## Key Results

| | Score AUC | Concede AUC |
|---|---|---|
| Model selection (best config) | 0.866 | 0.842 |
| World Cup 2022 (full tracking model) | 0.8005 | 0.8326 |
| World Cup 2022 (without on/off features) | 0.7998 | 0.8307 |

Tracking-derived spatial features give a small but consistent AUC gain on both tasks when transferred out-of-sample to an unseen tournament. The gain is modest, not transformative — reported here as-is rather than oversold.

## What This Project Demonstrates

- **Domain-driven feature engineering**: translating a football-specific hypothesis (defensive-line collapse, off-ball runs into space) into concrete geometric features computed from raw freeze-frame coordinates
- **A from-scratch action-valuation pipeline**: custom StatsBomb-events-to-SPADL conversion and VAEP-style gamestate features (goal-score state, speed/space deltas over the last 3 actions, polar distance/angle to goal), rather than relying solely on an existing library
- **Leakage-aware evaluation discipline**: match-level `GroupKFold` cross-validation, a strict train/tournament split, and out-of-sample testing on a full unseen tournament (World Cup 2022) rather than a random holdout
- **Structured experimentation**: feature parameter sweep → hyperparameter tuning (`RandomizedSearchCV`) → ablation analysis, each isolating one variable at a time
- **Independent applied-ML research**: scoped, built, and evaluated solo as a dissertation project, from raw event data to a tournament-transfer result

## Pipeline

```
StatsBomb events (Euro 2020 + World Cup 2022, via statsbombpy)
        │
        ▼
1. Custom SPADL-style action conversion  ──  my_SPADL_Converter-1.ipynb
        │
        ▼
2. Merge StatsBomb 360 freeze frames, derive
   defensive-line-gap / collapse / off-ball
   contribution features                  ──  On_Offball_Features_Merge-2.ipynb
        │
        ▼
3. VAEP-style gamestate features + score/concede labels
   (goalscore diff, space delta, speed, time delta, ...) ── Convert_into_Features_and_Labels-3.ipynb
        │
        ▼
4. Model selection, feature sweep, hyperparameter tuning
   (CatBoost / XGBoost, GroupKFold, RandomizedSearchCV)  ──  Paramtest_and_Pred_result-4.ipynb
        │
        ▼
5. World Cup 2022 out-of-sample evaluation + ablation    ──  Experiment-5.ipynb
```

![Pipeline Walkthrough](tracking_enhanced_vaep_pipeline_final_scroll.gif)

## Repository Structure

```
Dissertation Code/vaep_code/
  my_SPADL_Converter-1.ipynb              Stage 1 — event → action conversion
  On_Offball_Features_Merge-2.ipynb       Stage 2 — freeze-frame defensive/off-ball features
  Convert_into_Features_and_Labels-3.ipynb  Stage 3 — VAEP gamestate features + labels
  Paramtest_and_Pred_result-4.ipynb       Stage 4 — model selection & tuning
  Experiment-5.ipynb                      Stage 5 — out-of-sample evaluation & ablation
README.md
tracking_enhanced_vaep_pipeline_final.png
tracking_enhanced_vaep_pipeline_final_scroll.gif
```

## Data

- **Training**: Euro 2020 (StatsBomb open data)
- **Out-of-sample evaluation**: World Cup 2022 (StatsBomb open data)
- **Source**: StatsBomb event data + StatsBomb 360 freeze frames, via [`statsbombpy`](https://github.com/statsbomb/statsbombpy)

> StatsBomb 360 freeze frames don't always carry stable identifiers for every off-ball player, so off-ball contribution is best read as a team-level defensive-shape signal rather than fully attributable individual credit.

## How to Reproduce

Notebooks were written for Google Colab (Drive-mounted paths) and are meant to be run in order; each stage reads the previous stage's saved output:

1. `Dissertation Code/vaep_code/my_SPADL_Converter-1.ipynb` — pulls StatsBomb events, converts to action table
2. `Dissertation Code/vaep_code/On_Offball_Features_Merge-2.ipynb` — merges 360 freeze frames, computes collapse/off-ball features
3. `Dissertation Code/vaep_code/Convert_into_Features_and_Labels-3.ipynb` — builds VAEP-style features and score/concede labels
4. `Dissertation Code/vaep_code/Paramtest_and_Pred_result-4.ipynb` — model selection, feature sweep, hyperparameter tuning
5. `Dissertation Code/vaep_code/Experiment-5.ipynb` — World Cup 2022 evaluation and ablation

If running outside Colab, swap the `/content/drive/MyDrive/...` paths in each notebook for local paths. Intermediate/output files (HDF5 feature stores, result tables) are written to those configured paths and aren't checked into this repo.

## Tech Stack

Python · Pandas · NumPy · scikit-learn · CatBoost · XGBoost · `statsbombpy` · Jupyter/Colab notebooks

## Contact

If you're hiring for football analytics, sports data science, or applied ML roles, feel free to reach out.

LinkedIn: https://www.linkedin.com/in/keunwoo-kim-78138820b/
Email: mroptimister@gmail.com
