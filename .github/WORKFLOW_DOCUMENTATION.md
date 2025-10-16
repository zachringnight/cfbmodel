# GitHub Actions Workflow Documentation

## Overview

This repository includes a GitHub Actions workflow that automatically runs the CFB prediction model and generates structured outputs.

## Workflow: Run CFB Model and Generate Predictions

**File:** `.github/workflows/run-model.yml`

### Triggers

The workflow can be triggered in two ways:

1. **Scheduled (Automatic)**: Runs every Saturday at 8 AM UTC
2. **Manual Dispatch**: Can be triggered manually from the Actions tab with custom parameters

### Manual Workflow Inputs

When running the workflow manually, you can specify:

- **year**: Season year for predictions (defaults to current year)
- **week**: Week number for predictions (auto-detected if not specified)
- **train_year**: Year to use for training data (defaults to previous year)

### What the Workflow Does

1. **Checkout Repository**: Gets the latest code
2. **Set Up Python**: Installs Python 3.11 with pip caching
3. **Install Dependencies**: Installs all required packages from `requirements.txt`
4. **Run Model**: 
   - Trains a model on historical data
   - Makes predictions for the specified week
   - Generates structured outputs (JSON, CSV)
5. **Generate Summary**: Creates a markdown summary of the run
6. **Upload Artifacts**: Saves all outputs for later download

### Outputs

The workflow generates the following artifacts:

#### 1. Predictions Output (`predictions-output-{run_number}`)
Contains:
- `predictions_output.txt`: Full console output from the model run
- `summary.md`: Summary report with key information
- `exit_code.txt`: Exit status of the run

**Retention**: 30 days

#### 2. Trained Model (`trained-model-{run_number}`)
Contains:
- `cfb_model.pkl`: The trained model file (only on successful runs)

**Retention**: 90 days

#### 3. Predictions Data (`predictions-data-{run_number}`)
Contains:
- `predictions_YYYYMMDD_HHMMSS.json`: Structured predictions in JSON format
- `predictions_YYYYMMDD_HHMMSS.csv`: Predictions in CSV format

**Retention**: 30 days

### JSON Output Format

```json
{
  "metadata": {
    "year": 2025,
    "week": 8,
    "generated_at": "2025-10-16T12:00:00",
    "model_path": "cfb_model.pkl",
    "games_found": 45,
    "model_type": "random_forest"
  },
  "predictions": [
    {
      "game_number": 1,
      "home_team": "Michigan",
      "away_team": "Michigan State",
      "start_date": "2025-10-18",
      "predicted_winner": "Michigan",
      "confidence": 89.2,
      "home_win_probability": 89.2,
      "away_win_probability": 10.8
    }
  ]
}
```

### CSV Output Format

The CSV file contains the same prediction data in a tabular format:

```csv
game_number,home_team,away_team,start_date,predicted_winner,confidence,home_win_probability,away_win_probability
1,Michigan,Michigan State,2025-10-18,Michigan,89.2,89.2,10.8
```

## Required Secrets

The workflow requires one secret to be set in the repository:

- **CFB_API_KEY**: Your College Football Data API key

To set this up:
1. Go to your repository on GitHub
2. Click on "Settings" → "Secrets and variables" → "Actions"
3. Click "New repository secret"
4. Name: `CFB_API_KEY`
5. Value: Your API key from https://collegefootballdata.com/

## Running the Workflow Manually

1. Go to the "Actions" tab in the GitHub repository
2. Click on "Run CFB Model and Generate Predictions" workflow
3. Click "Run workflow" button
4. (Optional) Customize the inputs:
   - Year: e.g., `2025`
   - Week: e.g., `8` (leave blank for auto-detection)
   - Train Year: e.g., `2024` (leave blank to use previous year)
5. Click "Run workflow" to start

## Downloading Outputs

After a workflow run completes:

1. Go to the workflow run page
2. Scroll down to the "Artifacts" section
3. Download the artifacts you need:
   - **predictions-output-X**: For logs and summary
   - **trained-model-X**: For the model file
   - **predictions-data-X**: For JSON/CSV predictions

## Local Testing

You can test the workflow locally using the provided scripts:

### Test Output Generation
```bash
python test_workflow_outputs.py
```

### Run Predictions with Outputs
```bash
export CFB_API_KEY="your_api_key"
python run_predictions_with_outputs.py --train --train-year 2024 --week 8
```

This will generate:
- `predictions.json`: JSON format predictions
- `predictions.csv`: CSV format predictions
- `cfb_model.pkl`: Trained model

## Workflow Files

- `.github/workflows/run-model.yml`: Main workflow definition
- `run_predictions_with_outputs.py`: Script that generates structured outputs
- `test_workflow_outputs.py`: Test script to validate output generation

## Troubleshooting

### "No games found"
- The week number may be too high or outside the regular season (0-15)
- Games may not be scheduled yet for future weeks
- Check that the year is correct

### Workflow fails with API error
- Verify that the `CFB_API_KEY` secret is set correctly
- Check that the API key is valid and has proper permissions
- The API may be temporarily unavailable

### No artifacts uploaded
- Check the workflow logs for errors
- Ensure the model training completed successfully
- Verify that output files were created

## Integration Examples

### Download and Use Predictions in CI/CD

```yaml
- name: Download predictions
  uses: actions/download-artifact@v4
  with:
    name: predictions-data-latest

- name: Process predictions
  run: |
    cat predictions_*.json | jq '.predictions[] | select(.confidence > 75)'
```

### Schedule Different Configurations

You can create multiple workflows for different purposes:
- Weekly predictions on Saturdays
- Mid-week updates on Wednesdays
- End-of-season analysis

## Future Enhancements

Potential improvements to consider:
- Push predictions to a database or API
- Send notifications with top predictions
- Generate visualizations/charts
- Compare predictions to actual results
- Track model accuracy over time
