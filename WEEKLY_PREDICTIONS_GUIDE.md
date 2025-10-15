# Weekly Predictions Guide

This guide explains how to run predictions for the current week's college football games.

## Quick Start

### Option 1: Use the existing script with automatic week detection

```bash
# Set your API key
export CFB_API_KEY="your_api_key_here"

# Run predictions for the current week (automatically detected)
python run_weekly_predictions.py --train --train-year 2024
```

This will:
1. Automatically determine the current week based on today's date
2. Train a model on 2024 season data (if `--train` is specified)
3. Fetch games for the current week of 2025
4. Generate predictions with confidence scores

### Option 2: Specify a particular week

```bash
# Run predictions for a specific week
python run_weekly_predictions.py --week 8 --year 2025
```

### Option 3: Use a pre-trained model

```bash
# First, train and save a model
python run_weekly_predictions.py --train --train-year 2024 --model-path my_model.pkl

# Later, use the saved model for predictions
python run_weekly_predictions.py --week 8 --model-path my_model.pkl
```

## Command-Line Options

- `--api-key`: Your College Football Data API key (or set `CFB_API_KEY` environment variable)
- `--year`: Season year for predictions (default: current year)
- `--week`: Specific week number (default: automatically calculated)
- `--model-path`: Path to save/load the model (default: `cfb_model.pkl`)
- `--train`: Train a new model before making predictions
- `--train-year`: Year to use for training data (default: previous year)

## How Week Detection Works

The script automatically calculates the current week by:
1. Finding the start of the CFB season (typically last Saturday of August)
2. Calculating the number of weeks since the season started
3. Returning the appropriate week number (0-15 for regular season)

For the 2025 season starting around August 30, 2025:
- Week 0: Aug 30
- Week 1: Sep 6
- Week 2: Sep 13
- Week 7: Oct 18
- Week 8: Oct 25

As of October 15, 2025, we are in **Week 7** of the season.

## Example Output

```
======================================================================
CFB Model - Week 7 Predictions for 2025 Season
======================================================================

=== Fetching Week 7 Games ===

✓ Found 45 games for week 7

Fetching team statistics...
  ✓ Fetched stats for 133 teams
  ✓ Fetched talent ratings for 133 teams

Preparing features for prediction...
  ✓ Feature matrix shape: (45, 13)

Generating predictions...

======================================================================
PREDICTIONS FOR WEEK 7 - 2025 SEASON
======================================================================

Game 1: Michigan State @ Michigan
  Date: 2025-10-18
  Predicted Winner: Michigan
  Confidence: ██████████████████████████████ 89.2%
  Probability: Home 89.2% | Away 10.8%

Game 2: Texas A&M @ Alabama
  Date: 2025-10-18
  Predicted Winner: Alabama
  Confidence: ████████████████████████░░░░░░ 76.5%
  Probability: Home 76.5% | Away 23.5%

...
```

## Using with Different Model Types

The script uses Random Forest by default, but you can modify the `CFBModel` initialization in the script to use different model types:

```python
# In run_weekly_predictions.py, change:
model = CFBModel(model_type="random_forest")

# To:
model = CFBModel(model_type="gradient_boosting")
```

## Getting an API Key

1. Visit [https://collegefootballdata.com/](https://collegefootballdata.com/)
2. Create a free account
3. Generate an API key from your account settings
4. Set it as an environment variable: `export CFB_API_KEY="your_key"`

## Troubleshooting

### "No games found for week X"
- The week number may be too high or too low
- Games may not be scheduled yet for future weeks
- Check that you're using the correct year

### "Model file not found"
- Train a model first using the `--train` flag
- Or specify the correct path with `--model-path`

### "API key required"
- Set the `CFB_API_KEY` environment variable
- Or use the `--api-key` command-line option

## Integration with Existing Code

This script integrates with the existing CFB model codebase:
- Uses `data_fetcher.py` to fetch game data from the API
- Uses `preprocessor.py` to prepare features
- Uses `model.py` for machine learning predictions
- Compatible with all existing model types and configurations

## Advanced Usage

### Running for Multiple Weeks

```bash
# Predict multiple weeks in sequence
for week in {7..10}; do
    echo "=== Week $week ==="
    python run_weekly_predictions.py --week $week --year 2025
    echo ""
done
```

### Saving Predictions to File

```bash
# Save predictions to a text file
python run_weekly_predictions.py --week 7 > week7_predictions.txt
```

### Using in a Cron Job

```bash
# Run predictions every Saturday morning at 8 AM
0 8 * * 6 cd /path/to/cfbmodel && python run_weekly_predictions.py
```
