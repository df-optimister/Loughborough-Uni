# Tracking-Enhanced VAEP

Extending the VAEP (Valuing Actions by Estimating Probabilities) action-valuation framework with spatial context derived from StatsBomb 360 freeze-frame tracking data — built as an MSc dissertation project.

---

## The Problem

Standard VAEP values actions using only on-ball event data (pass, shot, dribble, ...), so it has no way to see defensive shape or off-ball movement. Two identical passes into the same space can have very different value depending on whether the defensive line is collapsing behind them — event data alone can't tell them apart. This project tests whether adding freeze-frame-derived spatial features closes that gap.

## Key Results

| | Score AUC | Concede AUC |
|---|---|---|
| Base model comparison (CatBoost vs. Logistic Regression / XGBoost) | 0.851 | 0.800 |
| Ablation on Euro 2020 — **with** on/off-ball tracking features | 0.8005 | 0.8326 |
| Ablation on Euro 2020 — **without** on/off-ball tracking features | 0.7998 | 0.8307 |
| World Cup 2022, true out-of-sample — **with** tracking features | 0.8468 | 0.8116 |
| World Cup 2022, true out-of-sample — **without** tracking features | 0.8430 | 0.8116 |

Tracking features give a small, consistent gain on the scoring task in both the Euro 2020 ablation and the World Cup 2022 out-of-sample transfer. On the conceding task, the Euro 2020 gain (0.8326 vs 0.8307) doesn't hold out-of-sample — both variants tie at 0.8116 on World Cup 2022. That gap between in-sample ablation and out-of-sample transfer is reported as-is rather than smoothed over; see [Limitations](#limitations) for the most likely reason.

## Player & Team Valuation (Stage 5 — World Cup 2022)

The AUC numbers above measure predictive quality; Stage 5 (`Experiment-5.ipynb`) applies the trained model to World Cup 2022 to produce the actual VAEP outputs a recruitment/analysis team would use — team and player rankings, not just a discrimination score.

**Semi-finalists, mean VAEP per match**

| Team | Offensive value | Defensive value | VAEP |
|---|---|---|---|
| Argentina (champions) | 0.357 | 0.086 | **0.443** |
| France (runners-up) | 0.053 | 0.038 | 0.091 |
| Croatia (3rd place) | -0.078 | -0.002 | -0.080 |
| Morocco (4th place) | -0.482 | -0.202 | -0.685 |

This ranks the eventual champions highest and the fourth-place finisher lowest, consistent with the tournament outcome. Morocco's negative score is worth a caveat, not a dismissal: their run was built on a low-event, deep-block defensive style that an action-level value model doesn't fully credit — which echoes the wider football-analytics discussion of Morocco 2022 as a genuine over-performance relative to underlying process, rather than a model error.

**Top 5 players by avg VAEP/match — the ranking changes with the feature set**

| Rank | ON-ONLY (on-ball tracking features) | NO-ONOFF (baseline, no tracking) |
|---|---|---|
| 1 | Lozano — 0.450 | Lozano — 0.428 |
| 2 | Musiala — 0.413 | Musiala — 0.413 |
| 3 | Gnabry — 0.394 | Gnabry — 0.404 |
| 4 | De Bruyne — 0.378 | Messi — 0.378 |
| 5 | Pulisic — 0.378 | Kostić — 0.371 |

Messi and Kostić only enter the top 5 once the on/off-ball tracking features are removed — the tracking-enhanced attribution doesn't just move the AUC by a fraction of a point, it changes who the model says was most valuable. That's the practically relevant result for a scouting/recruitment use case, not the headline metric.

**VAEP vs. xG vs. actual goals, for the ON-ONLY top 5**

| Player | VAEP/match | xG/match | Goals (tournament) |
|---|---|---|---|
| Lozano | 0.450 | 0.080 | 0 |
| Musiala | 0.413 | 0.357 | 0 |
| Gnabry | 0.394 | 0.243 | 1 |
| De Bruyne | 0.378 | 0.059 | 0 |
| Pulisic | 0.378 | 0.194 | 1 |

Lozano ranks #1 by VAEP despite scoring zero goals and posting the second-lowest xG of the five — including one player (De Bruyne) with more goals and higher xG but a lower VAEP score. Musiala's VAEP tracks his own shot threat closely; Lozano's and De Bruyne's don't — in this model, their value comes from progression and chance creation rather than direct shooting threat, which an xG-or-goals-only view would miss entirely.

**Does the tracking-enhanced ranking track real-world value better? (Transfermarkt 2023 market values, as an external sanity check)**

| Top-5 set | Players | Combined market value |
|---|---|---|
| ON-ONLY (with on-ball contribution feature) | Lozano, Musiala, Gnabry, De Bruyne, Pulisic | €292m |
| NO-ONOFF (baseline, without on-ball contribution) | Lozano, Musiala, Gnabry, Messi, Kostić | €257m |

Adding the on-ball contribution feature swaps Messi and Kostić out of the top 5 for De Bruyne and Pulisic, and the resulting top 5 carries about €35m more combined market value. This is a 5-player comparison, not a statistical test — but it's a directionally useful, independent check that the tracking-enhanced ranking leans closer to how the market independently prices these players.

## What This Project Demonstrates

- **Domain-driven feature engineering**: translating a football-specific hypothesis (defensive-line collapse, off-ball runs into space) into concrete geometric features computed from raw freeze-frame coordinates
- **A from-scratch action-valuation pipeline**: custom StatsBomb-events-to-SPADL conversion and VAEP-style gamestate features (goal-score state, speed/space deltas over the last 3 actions, polar distance/angle to goal), rather than relying solely on an existing library
- **Leakage-aware evaluation discipline**: match-level `GroupKFold` cross-validation, a strict train/tournament split, and out-of-sample testing on a full unseen tournament (World Cup 2022) rather than a random holdout
- **Structured experimentation**: feature parameter sweep → hyperparameter tuning (`RandomizedSearchCV`) → ablation analysis, each isolating one variable at a time
- **Translating model output into decision-relevant results**: team/player VAEP rankings and a VAEP-vs-xG comparison, not just an aggregate metric
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
4. Model selection, feature sweep, hyperparameter tuning,
   World Cup 2022 out-of-sample AUC + ablation             ──  Paramtest_and_Pred_result-4.ipynb
        │
        ▼
5. Apply the model to World Cup 2022: team/player VAEP
   rankings and VAEP-vs-xG reporting                        ──  Experiment-5.ipynb
```

![Pipeline Walkthrough](tracking_enhanced_vaep_pipeline_final_scroll.gif)

## Repository Structure

```
Dissertation Code/vaep_code/
  my_SPADL_Converter-1.ipynb              Stage 1 — event → action conversion
  On_Offball_Features_Merge-2.ipynb       Stage 2 — freeze-frame defensive/off-ball features
  Convert_into_Features_and_Labels-3.ipynb  Stage 3 — VAEP gamestate features + labels
  Paramtest_and_Pred_result-4.ipynb       Stage 4 — model selection, tuning, WC2022 AUC & ablation
  Experiment-5.ipynb                      Stage 5 — WC2022 team/player VAEP valuation & reporting
README.md
tracking_enhanced_vaep_pipeline_final.png
tracking_enhanced_vaep_pipeline_final_scroll.gif
```

## Data

- **Training**: Euro 2020 (StatsBomb open data)
- **Out-of-sample evaluation**: World Cup 2022 (StatsBomb open data)
- **Source**: StatsBomb event data + StatsBomb 360 freeze frames, via [`statsbombpy`](https://github.com/statsbomb/statsbombpy)

> StatsBomb 360 freeze frames don't always carry stable identifiers for every off-ball player, so off-ball contribution is best read as a team-level defensive-shape signal rather than fully attributable individual credit.

## Limitations

- **Stage 4 (`Paramtest_and_Pred_result-4.ipynb`) uses a simplified fallback feature pipeline** rather than importing directly from Stages 2–3, because the intermediate hand-off wasn't clearly documented at the time. The fallback keeps the core on/off-ball contribution features but drops two things the design called for: bonus scoring when an on/off-ball action leads to a shot or goal within the action window, and full 3-previous-action gamestate context. This is the most likely reason the tracking gain is modest and doesn't fully hold out-of-sample on the conceding task.
- **Off-ball attribution is team-level only.** StatsBomb 360 freeze frames don't reliably identify every off-ball player, so off-ball contribution couldn't be attributed to individuals — only used in team-level analysis.
- **Only 3 structural parameters were swept** (`line_gap`, `in_line_gap`, `nr_actions`). Other parameters that shape the defensive-line/collapse detection (`x_threshold`, `y_tolerance`) were held fixed rather than tuned.

## How to Reproduce

Notebooks were written for Google Colab (Drive-mounted paths) and are meant to be run in order; each stage reads the previous stage's saved output:

1. `Dissertation Code/vaep_code/my_SPADL_Converter-1.ipynb` — pulls StatsBomb events, converts to action table
2. `Dissertation Code/vaep_code/On_Offball_Features_Merge-2.ipynb` — merges 360 freeze frames, computes collapse/off-ball features
3. `Dissertation Code/vaep_code/Convert_into_Features_and_Labels-3.ipynb` — builds VAEP-style features and score/concede labels
4. `Dissertation Code/vaep_code/Paramtest_and_Pred_result-4.ipynb` — model selection, feature sweep, hyperparameter tuning, World Cup 2022 out-of-sample AUC and ablation
5. `Dissertation Code/vaep_code/Experiment-5.ipynb` — applies the model to World Cup 2022 for team/player VAEP rankings and VAEP-vs-xG reporting

If running outside Colab, swap the `/content/drive/MyDrive/...` paths in each notebook for local paths. Intermediate/output files (HDF5 feature stores, result tables) are written to those configured paths and aren't checked into this repo.

## Tech Stack

Python · Pandas · NumPy · scikit-learn · CatBoost · XGBoost · `statsbombpy` · Jupyter/Colab notebooks

## Contact

If you're hiring for football analytics, sports data science, or applied ML roles, feel free to reach out.

LinkedIn: https://www.linkedin.com/in/keunwoo-kim-78138820b/
Email: mroptimister@gmail.com
