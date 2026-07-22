# CFB Model

![CI Status](https://github.com/zachringnight/cfbmodel/actions/workflows/ci.yml/badge.svg)
![Weekly Predictions](https://img.shields.io/github/actions/workflow/status/zachringnight/cfbmodel/run-model.yml?label=Weekly%20Predictions)

A machine learning pipeline for predicting college football game outcomes,
player/team props, and betting profitability, built on data from the
[College Football Data (CFBD) API](https://collegefootballdata.com/). It
trains and runs automatically every week via GitHub Actions.

## What's Here

- **Game winner predictions** — a Random Forest / Gradient Boosting
  classifier trained on historical game results, team stats, and talent
  ratings (`main.py`, `model.py`, `data_fetcher.py`, `preprocessor.py`)
- **Props predictions** — regression models for team points, game totals,
  and spreads, with actionable edge-vs-line comparisons
  (`props_model.py`, `props_preprocessor.py`, `run_props.py`)
- **Profit modeling** — an enhanced feature/training pipeline aimed at
  betting profitability rather than raw accuracy
  (`profit_model.py`, `train_profit_model.py`)
- **CFBD-ratings picks generator** — a lighter, no-training-required picks
  tool that scores each week's games from CFBD's own betting lines and
  ELO/SP+/FPI/SRS ratings (`weekly_picks_cfbd.py`) — see
  [WEEKLY_PICKS_GUIDE.md](WEEKLY_PICKS_GUIDE.md)
- **Automated weekly runs** — a scheduled GitHub Actions workflow that
  trains and generates predictions every Saturday, with results uploaded as
  artifacts (`.github/workflows/run-model.yml`)
- **Jupyter notebooks** (`01_...ipynb` through `12_...ipynb`) covering
  rankings, matchup prediction, drive efficiency, opponent adjustments, SRS,
  and other exploratory analysis built on the same underlying CFBD data

## Prerequisites

- Python 3.9+
- A College Football Data API key — get one free at
  [collegefootballdata.com](https://collegefootballdata.com/key)

## Installation

```bash
git clone https://github.com/zachringnight/cfbmodel.git
cd cfbmodel
pip install -r requirements.txt
```

Or install as a package (adds a `cfbmodel` console command backed by `main.py`):

```bash
pip install -e .
```

## API Key Setup

Most scripts read the API key from the `CFB_API_KEY` environment variable
(`weekly_picks_cfbd.py` also accepts the upstream `CFBD_API_KEY` name):

```bash
cp .env.example .env      # then edit .env and add your key
export CFB_API_KEY="your_api_key_here"
```

Never hardcode API keys in source, config, or workflow files — see
[.github/SECURITY.md](.github/SECURITY.md) for the full guidance on secrets
handling, key rotation, and what to do if a key is ever exposed.

## Usage

### Automated Weekly Runs (GitHub Actions)

The model runs on its own every Saturday at 8 AM UTC via
[`.github/workflows/run-model.yml`](.github/workflows/run-model.yml), training
on the prior season and generating predictions (JSON + CSV) for the current
week as downloadable workflow artifacts. It can also be triggered manually
from the Actions tab with custom `year`/`week`/`train_year` parameters.

**Setup:**
1. Add your key as a repository secret named `CFB_API_KEY` (Settings →
   Secrets and variables → Actions → New repository secret)
2. The workflow runs automatically from then on; or trigger it manually from
   the Actions tab, optionally supplying a one-off `api_key` input instead of
   using the secret (the input is never stored or logged)

Full details on triggers, inputs, outputs, and artifact retention are in
[.github/WORKFLOW_DOCUMENTATION.md](.github/WORKFLOW_DOCUMENTATION.md) and
[.github/WORKFLOWS.md](.github/WORKFLOWS.md) (workflow internals) /
[.github/WORKFLOW_ARCHITECTURE.md](.github/WORKFLOW_ARCHITECTURE.md)
(architecture overview).

### Quick Start: Weekly Predictions Locally

```bash
export CFB_API_KEY="YOUR_API_KEY"

# Simplest: auto-detects the current week and trains on last season
python run_this_week.py

# Or with explicit control over year/week/output format
python run_weekly_predictions.py --train --train-year 2024
python run_predictions_with_outputs.py --train --train-year 2024   # + JSON/CSV outputs
```

See [WEEKLY_PREDICTIONS_GUIDE.md](WEEKLY_PREDICTIONS_GUIDE.md) and
[USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) for more scenarios and sample output.

### Training and Predicting Directly

```bash
# Train a model on a given season
python main.py --api-key YOUR_API_KEY --year 2023 --train

# Predict a specific week with an existing model
python main.py --api-key YOUR_API_KEY --year 2024 --predict --week 5

# Train and predict in one command
python main.py --api-key YOUR_API_KEY --year 2023 --train --predict --week 10
```

### Props and Profit Models

```bash
# Train (or load) the props model and get actionable recommendations
python run_props.py --year 2024 --week 10
python run_props.py --year 2024 --week 10 --train
python run_props.py --year 2024 --week 10 --min-edge 3.0

# Train the profit-focused model
python train_profit_model.py --data-path training_data.csv
```

### CFBD-Ratings Picks Generator

An independent, no-training-required picks source based on CFBD's own
ratings/lines feeds — see [WEEKLY_PICKS_GUIDE.md](WEEKLY_PICKS_GUIDE.md) for
the full guide:

```bash
export CFBD_API_KEY="YOUR_API_KEY"   # or CFB_API_KEY

python weekly_picks_cfbd.py --year 2024 --week 10
python weekly_picks_cfbd.py --year 2024 --week 10 --conference SEC
python weekly_picks_cfbd.py --year 2024 --week 10 --min-confidence HIGH
```

## Testing

```bash
python -m pytest -v
```

Covers model initialization/training, input validation, prediction
functionality, data preprocessing, props/profit model behavior, and the
weekly-predictions/workflow helper scripts.

Continuous integration ([.github/workflows/ci.yml](.github/workflows/ci.yml))
runs this suite on every push and pull request across Python 3.9–3.12.

## Configuration

Model type, hyperparameters, API timeout/retry behavior, valid year/week
ranges, and logging level are all set in [config.py](config.py).

## Project Structure

```
cfbmodel/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml                    # CI: tests on every push/PR
│   │   ├── run-model.yml             # Scheduled + manual weekly run
│   │   └── model-demo.yml            # Manual demo workflow
│   ├── SECURITY.md                   # API key / secrets handling
│   ├── WORKFLOW_DOCUMENTATION.md     # run-model.yml reference
│   ├── WORKFLOWS.md                  # ci.yml + model-demo.yml reference
│   └── WORKFLOW_ARCHITECTURE.md      # Workflow architecture overview
├── data_fetcher.py                   # CFBD API client (retries, timeouts, validation)
├── preprocessor.py                   # Feature engineering for game predictions
├── model.py                          # Game-winner ML models
├── main.py                           # CLI: train / predict game winners
├── run_weekly_predictions.py         # Auto-detects current week, trains + predicts
├── run_predictions_with_outputs.py   # Same, plus structured JSON/CSV outputs
├── run_this_week.py                  # One-command wrapper around the above
├── props_model.py                    # Regression models for points/totals/spreads
├── props_preprocessor.py             # Feature engineering for props models
├── run_props.py                      # CLI: train / predict props with edge filtering
├── profit_model.py                   # Profit-focused feature/training pipeline
├── train_profit_model.py             # CLI: train the profit model
├── weekly_picks_cfbd.py              # CFBD-ratings-based picks generator (no training)
├── config.py                         # Model/API/logging configuration
├── test_*.py                         # Unit tests (pytest)
├── requirements.txt                  # Python dependencies
├── WEEKLY_PREDICTIONS_GUIDE.md       # Guide: game-winner weekly predictions
├── WEEKLY_PICKS_GUIDE.md             # Guide: weekly_picks_cfbd.py
├── USAGE_EXAMPLES.md                 # Worked examples and sample output
├── IMPROVEMENTS.md                   # History of production-readiness improvements
└── README.md                         # This file
```

## Model Performance

Typical results on 2023 season data (game-winner model):
- Training Accuracy: 63–65%
- Test Accuracy: 59–60%
- Cross-Validation Accuracy: ~59% (±1.6%)

Top predictive features: yardage differential, then home/away offensive
total, passing, and rushing yards. Props and profit models track separate
MAE/RMSE/R² metrics reported by their own training runs — see
[IMPROVEMENTS.md](IMPROVEMENTS.md) for details on how each pipeline evolved.

## License

See [LICENSE](LICENSE).
