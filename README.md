# 🏈 College Football Data Starter Pack

Welcome to the **CollegeFootballData.com Starter Pack** — a curated bundle of structured college football data, custom advanced metrics, and real-world Jupyter notebooks to help you build models, explore trends, and launch your own analytics projects faster.

---

## 📦 What’s Included

- ✅ **Historical Data**  
  - Game results (1869–present)  
  - Play-by-play, drives, season stats (2003–present)  
  - Advanced team-level metrics (EPA, success rate, explosiveness, etc.)

- ✅ **12 Jupyter Notebooks**  
  - Code walkthroughs for ranking, predictions, dashboards, and more

- ✅ **PDF Guides**  
  - Full data dictionary  
  - Overview of included notebooks

- ✅ **Metadata**  
  - Teams, conferences, venues

---

## 🧠 Who It's For

This pack is designed for:

- Data scientists & analysts  
- CFB modelers and pick’em competitors  
- Academic researchers  
- Hobbyists and fans who love working with real data

---

## 📚 Folder Structure
📂 data
  📂 advanced_game_stats/
  📂 advanced_season_stats/
  📂 drives/
  📂 game_stats/
  📂 plays/
  📂 season_stats/
  📄 conferences.csv
  📄 games.csv
  📄 teams.csv
📄 00_data_dictionary.ipynb
📄 01_intro_to_data.ipynb
📄 02_build_simple_rankings.ipynb
📄 03_metrics_comparison.ipynb
📄 04_team_similarity.ipynb
📄 05_matchup_predictor.ipynb
📄 06_custom_rankings_by_metric.ipynb
📄 07_drive_efficiency.ipynb
📄 08_offense_vs_defense_comparison.ipynb
📄 09_opponent_adjustments.ipynb
📄 10_srs_adjusted_metrics.ipynb
📄 11_metric_distribution_explorer.ipynb
📄 CFBD Starter Pack - Data Files Guide.pdf
📄 CFBD Starter Pack - Notebooks Guide.pdf
📄 headers.md
📄 12_efficiency_dashboards.ipynb
📄 LICENSE.txt
📄 README.md

---

## ⚙️ Requirements

To run the Jupyter notebooks, install:

A production-ready machine learning model for predicting college football game outcomes using data from the [College Football Data API](https://collegefootballdata.com/).

![CI Status](https://github.com/zachringnight/cfbmodel/actions/workflows/ci.yml/badge.svg)

## Features

- 🔄 **Robust API Client** with automatic retry logic and timeout handling
- 🤖 **Machine Learning Models** (Random Forest and Gradient Boosting) for game outcome prediction
- 📊 **Feature Engineering** from team statistics, talent ratings, and historical data
- 🔍 **Comprehensive Logging** for debugging and monitoring
- ✅ **Input Validation** with detailed error messages
- 🧪 **Unit Tests** for core functionality
- ⚙️ **Configurable Parameters** via config.py
- 📈 **Confidence Scores** for each prediction
- 🚀 **CI/CD Pipeline** with automated testing on multiple Python versions

## Prerequisites

- Python 3.7 or higher
- College Football Data API key (get one at https://collegefootballdata.com/)

## Installation

### Option 1: Direct Installation

1. Clone this repository:
```bash
git clone https://github.com/zachringnight/cfbmodel.git
cd cfbmodel
```

2. Install required dependencies:
```bash
pip install pandas numpy matplotlib seaborn scikit-learn jupyter
```

3. Set up your API key (optional - can also pass via command line):
```bash
cp .env.example .env
# Edit .env and add your API key
```

### Option 2: Package Installation

Install as a Python package:
```bash
git clone https://github.com/zachringnight/cfbmodel.git
cd cfbmodel
pip install -e .
```

This will install the package in development mode and make the `cfbmodel` command available in your terminal.

## Usage

The model can be used either by running the main script directly or through the installed package.

### 🚀 Quick Start: Weekly Predictions (NEW!)

Run predictions for the current week's games with automatic week detection:

```bash
# Set your API key
export CFB_API_KEY="YOUR_API_KEY"

# Run predictions for this week (automatically detected)
python run_weekly_predictions.py --train --train-year 2024
```

For detailed instructions, see [WEEKLY_PREDICTIONS_GUIDE.md](WEEKLY_PREDICTIONS_GUIDE.md).

### Training a Model

Train a model using data from a specific season:

```bash
# Using the script directly
python main.py --api-key YOUR_API_KEY --year 2023 --train

# Or if installed as a package
cfbmodel --api-key YOUR_API_KEY --year 2023 --train

# Or with executable permission
./main.py --api-key YOUR_API_KEY --year 2023 --train
```

This will:
- Fetch game data, team statistics, and talent ratings for the specified year
- Prepare features for machine learning
- Train a Random Forest classifier
- Display training metrics and feature importance
- Save the trained model to `cfb_model.pkl`

### Making Predictions

Make predictions for games in a specific week:

```bash
python main.py --api-key YOUR_API_KEY --year 2024 --predict --week 5
```

This will:
- Load the trained model
- Fetch upcoming games for the specified week
- Generate predictions with confidence scores
- Display results for each matchup

### Combined Training and Prediction

You can train and predict in one command:

```bash
python main.py --api-key YOUR_API_KEY --year 2023 --train --predict --week 10
```

## Testing

Run the unit tests to validate the installation:

```bash
python -m pytest test_cfb_model.py -v
```

All 10 tests should pass, covering:
- Model initialization and training
- Input validation and error handling
- Prediction functionality
- Data preprocessing

## Continuous Integration

This project includes a GitHub Actions CI workflow that automatically tests the model on every push and pull request.

The CI workflow:
- **Tests on Multiple Python Versions**: Runs tests on Python 3.9, 3.10, 3.11, and 3.12
- **Validates Module Imports**: Ensures all core modules can be imported
- **Tests Model Functionality**: Trains and validates the model with synthetic data
- **Runs Unit Tests**: Executes the full test suite automatically

### Workflow Triggers
- Push to `main`, `master`, `develop`, or any `copilot/**` branch
- Pull requests to `main`, `master`, or `develop`
- Manual workflow dispatch

### View Workflow Status
Check the [Actions tab](../../actions) in the GitHub repository to see the status of the CI workflow.

### Manual Model Demo
A manual workflow (`model-demo.yml`) is also available for demonstrating the model:
- Can be triggered manually from the Actions tab
- Option to use synthetic test data or real API data
- Shows complete model training and prediction pipeline
- Useful for demonstrations and validating model functionality

To run the demo:
1. Go to the [Actions tab](../../actions)
2. Select "Model Demo (Manual Trigger)"
3. Click "Run workflow"
4. Choose synthetic or real data (real data requires CFB_API_KEY secret)

## Configuration

Modify `config.py` to customize model parameters:

- **Model Type**: Random Forest or Gradient Boosting
- **Model Hyperparameters**: n_estimators, max_depth, learning_rate, etc.
- **API Settings**: Timeout, retry attempts
- **Logging Level**: DEBUG, INFO, WARNING, ERROR

## Project Structure

```
cfbmodel/
├── .github/
│   └── workflows/
│       ├── ci.yml                 # CI workflow for automated testing
│       └── model-demo.yml         # Manual demo workflow
├── data_fetcher.py                # API client with retry logic and validation
├── preprocessor.py                # Data preprocessing and feature engineering
├── model.py                       # ML model definitions with logging
├── main.py                        # CLI interface
├── run_weekly_predictions.py      # NEW: Automatic weekly predictions script
├── test_weekly_predictions.py     # NEW: Test script for weekly predictions
├── config.py                      # Configuration parameters
├── test_cfb_model.py              # Unit tests
├── example.py                     # Usage examples
├── requirements.txt               # Python dependencies
├── TESTING_SUMMARY.md             # Test results and validation
├── WEEKLY_PREDICTIONS_GUIDE.md    # NEW: Guide for weekly predictions
└── README.md                      # This file
```

## Improvements in This Version

### Robustness
- ✅ Automatic retry logic for API requests
- ✅ Request timeout handling
- ✅ Comprehensive input validation
- ✅ Detailed error messages

### Observability
- ✅ Structured logging throughout the codebase
- ✅ Training progress tracking
- ✅ API call monitoring

### Code Quality
- ✅ Type hints for better IDE support
- ✅ Docstrings with parameter descriptions
- ✅ Unit tests with pytest
- ✅ Configuration file for easy customization

### Error Handling
- ✅ Validates API keys before use
- ✅ Checks data frame emptiness
- ✅ Validates year and week ranges
- ✅ Handles missing files gracefully

## Model Features

The model uses the following features for predictions:

- **Offensive Statistics**: Total yards, passing yards, rushing yards
- **Team Talent Ratings**: Recruiting and talent composite scores
- **Differential Features**: Calculated differences between home and away team stats
- **Historical Performance**: Season-long averages and trends

## Model Performance

Typical results on 2023 season data:
- **Training Accuracy**: 63-65%
- **Test Accuracy**: 59-60%
- **Cross-Validation Accuracy**: 59% (±1.6%)

**Feature Importance Analysis:**
1. yards_diff (28%) - Most predictive feature
2. home_off_total_yards (15%)
3. away_off_total_yards (14%)
4. home_off_passing_yards (12%)
5. home_off_rushing_yards (12%)

---

## 🚀 Getting Started
1. Extract the ZIP package
2. Open the folder in Jupyter Lab, Jupyter Notebook, or VS Code
3. Start with `01_intro_to_data.ipynb`
4. Explore and modify notebooks for your own analysis.

---

## 📜 License & Terms of Use
This Starter Pack is provided for personal, non-commercial use only by the original purchaser or Patreon subscriber.

By downloading or using this product, you agree to the following:
* ✅ You may use the data, code, and examples for personal projects, academic research, or internal use.
* 🚫 You may not redistribute, resell, republish, or repackage this content — in whole or in part — without written permission.
* 🚫 You may not share access to the ZIP file, notebooks, or datasets publicly or with teams.
* 🧠 Attribution is appreciated but not required.

If you're interested in licensing this pack for organizational use, educational programs, or media coverage, [please contact me](mailto:admin@collegefootballdata.com).

---

## 📬 Contact
For questions, feedback, or support:
🏠 CollegeFootballData.com
💌 Email: admin@collegefootballdata.com
🧵 Twitter / X: @CFB_Data
🌐 Bluesky: @collegefootballdata.com

---

Thanks for supporting independent sports data!