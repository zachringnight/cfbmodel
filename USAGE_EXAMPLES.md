# Usage Examples for Weekly Predictions

## Example 1: Simplest Usage (Recommended for Most Users)

```bash
# Step 1: Set your API key
export CFB_API_KEY="your_api_key_from_collegefootballdata.com"

# Step 2: Run predictions for this week
python run_this_week.py
```

**What happens:**
- Automatically detects current week (Week 7 for Oct 15, 2025)
- Trains model on 2024 season data
- Fetches this week's games from API
- Generates predictions with confidence scores

**Output:**
```
======================================================================
CFB Model - Week 7 Predictions for 2025 Season
======================================================================

=== Training Model on 2024 Season ===
✓ Fetched 150 games
✓ Fetched stats for 133 teams
Training Accuracy: 65.23%
Test Accuracy: 60.15%

=== Fetching Week 7 Games ===
✓ Found 45 games for week 7

======================================================================
PREDICTIONS FOR WEEK 7 - 2025 SEASON
======================================================================

Game 1: Michigan State @ Michigan
  Predicted Winner: Michigan
  Confidence: ██████████████████████████████ 89.2%
  Probability: Home 89.2% | Away 10.8%
...
```

---

## Example 2: Test Without API Key

```bash
# No API key needed - uses synthetic data
python test_weekly_predictions.py
```

**What happens:**
- Creates synthetic training data for 2024
- Trains a Random Forest model
- Creates synthetic games for current week
- Generates predictions

**Use this to:**
- Test the system before getting an API key
- Verify installation is working
- Understand the prediction format

---

## Example 3: Use Pre-trained Model

```bash
# Step 1: Train and save a model once
export CFB_API_KEY="your_key"
python run_weekly_predictions.py --train --train-year 2024 --model-path my_model.pkl

# Step 2: Later, reuse the saved model for new predictions
python run_weekly_predictions.py --week 8 --model-path my_model.pkl
```

**Benefits:**
- Faster predictions (no retraining needed)
- Consistent predictions across weeks
- Save best-performing models

---

## Example 4: Predict Multiple Weeks

```bash
# Predict weeks 7 through 10
for week in {7..10}; do
    echo "=== Week $week ==="
    python run_weekly_predictions.py --week $week --year 2025
    echo ""
done
```

---

## Example 5: Save Predictions to File

```bash
# Save predictions to a text file
python run_weekly_predictions.py > week7_predictions.txt

# Or save to CSV (you'll need to add CSV export functionality)
python run_weekly_predictions.py --output-format csv > predictions.csv
```

---

## Example 6: Specific Week Prediction

```bash
# Predict games for a specific week
python run_weekly_predictions.py --week 10 --year 2025
```

---

## Example 7: Use Different Training Data

```bash
# Train on 2023 instead of 2024
python run_weekly_predictions.py --train --train-year 2023 --week 7
```

---

## Example 8: Interactive Shell Script

```bash
# Run the interactive menu
./run_this_week.sh
```

**What happens:**
- Presents menu with options
- Option 1: Train new model and predict
- Option 2: Use existing model
- Guides you through the process

---

## Week-by-Week Schedule (2025 Season)

The automatic week detection uses this approximate schedule:

| Date Range    | Week | Notes                |
|--------------|------|----------------------|
| Aug 30       | 0    | Week Zero games      |
| Sep 6        | 1    | Season opener        |
| Sep 13       | 2    |                      |
| Sep 20       | 3    |                      |
| Sep 27       | 4    |                      |
| Oct 4        | 5    |                      |
| Oct 11       | 6    |                      |
| **Oct 18**   | **7**| **← Current (Oct 15)** |
| Oct 25       | 8    |                      |
| Nov 1        | 9    |                      |
| Nov 8        | 10   |                      |
| Nov 15       | 11   |                      |
| Nov 22       | 12   |                      |
| Nov 29       | 13   | Rivalry week         |

---

## Command Reference

### run_this_week.py
```bash
python run_this_week.py
```
- Simplest option
- Uses defaults (current year, train on previous year)
- Requires CFB_API_KEY environment variable

### run_weekly_predictions.py
```bash
python run_weekly_predictions.py [OPTIONS]

Options:
  --api-key TEXT          API key (or use CFB_API_KEY env var)
  --year INTEGER          Season year (default: current year)
  --week INTEGER          Week number (default: auto-detected)
  --model-path TEXT       Model file path (default: cfb_model.pkl)
  --train                 Train new model
  --train-year INTEGER    Training data year (default: previous year)
  --help                  Show help message
```

### test_weekly_predictions.py
```bash
python test_weekly_predictions.py
```
- No options needed
- No API key required
- Uses synthetic data

---

## Troubleshooting

### "API key required"
**Solution:** Set the environment variable:
```bash
export CFB_API_KEY="your_key_here"
```

### "No games found for week X"
**Possible causes:**
1. Week number is too high (season only has 0-13)
2. Games not yet scheduled in API
3. Wrong year

**Solution:**
```bash
# Check what week we're in
python -c "from run_weekly_predictions import get_current_week; print(get_current_week(2025))"

# Try a different week
python run_weekly_predictions.py --week 5
```

### "Model file not found"
**Solution:** Train a model first:
```bash
python run_weekly_predictions.py --train --train-year 2024
```

### Predictions seem inaccurate
**Solutions:**
1. Train on more recent data
2. Ensure team stats are up to date
3. Check that the API has current season data

```bash
# Train on most recent complete season
python run_weekly_predictions.py --train --train-year 2024
```

---

## Tips for Best Results

1. **Train on recent data**: Use previous season for most accurate predictions
2. **Retrain periodically**: Update model as season progresses
3. **Check confidence scores**: Higher confidence = more reliable prediction
4. **Compare multiple models**: Try different training years
5. **Save good models**: Keep models that perform well

---

## Getting Help

- Detailed guide: `WEEKLY_PREDICTIONS_GUIDE.md`
- Implementation details: `THIS_WEEK_SUMMARY.md`
- General usage: `README.md`
- Command help: `python run_weekly_predictions.py --help`
