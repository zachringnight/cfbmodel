# GitHub Actions Workflows

This repository includes two GitHub Actions workflows for automated testing and model demonstrations.

## 1. CI Workflow (`ci.yml`)

**Purpose**: Automatically test the CFB model on every push and pull request

**Triggers**:
- Push to `main`, `master`, `develop`, or `copilot/**` branches
- Pull requests to `main`, `master`, or `develop`
- Manual workflow dispatch

**What it does**:
- **Multi-version Testing**: Tests on Python 3.9, 3.10, 3.11, and 3.12
- **Module Validation**: Ensures all core modules can be imported
- **Unit Tests**: Runs the complete test suite (10 tests)
- **Model Functionality**: Trains and validates the model with synthetic data
- **Dependency Caching**: Caches pip packages for faster runs

**Jobs**:
1. `test`: Runs unit tests on all Python versions
2. `model-functionality`: Tests the complete model pipeline

## 2. Model Demo Workflow (`model-demo.yml`)

**Purpose**: Demonstrate the model's capabilities with manual triggers

**Triggers**:
- Manual workflow dispatch only

**What it does**:
- **Synthetic Data Demo**: Creates realistic training data and runs the model
- **Training Pipeline**: Shows complete model training process
- **Predictions**: Makes sample predictions with confidence scores
- **API Integration**: Optionally uses real CFB API (requires secret)

**Parameters**:
- `use_synthetic_data`: Choose between synthetic or real API data (default: true)
- `year`: Season year for real API data (default: 2023)
- `week`: Week number for predictions (default: 1)

**How to run**:
1. Go to the repository's Actions tab
2. Select "Model Demo (Manual Trigger)"
3. Click "Run workflow"
4. Select options and run

**Example Output**:
```
============================================================
CFB Model Demo - Synthetic Data
============================================================

📊 Creating synthetic training data...
✓ Created 200 training samples
  Home wins: 88 (44.0%)
  Away wins: 112 (56.0%)

🤖 Training Random Forest model...

📈 Training Results:
  Train Accuracy: 98.57%
  Test Accuracy:  76.67%
  CV Mean:        77.00% (+/- 7.14%)

🎯 Making Sample Predictions...

  Strong Home vs Good Away:
    Predicted Winner: Home
    Confidence: 60.9%

  Good Home vs Strong Away:
    Predicted Winner: Away
    Confidence: 71.4%

  Balanced Matchup:
    Predicted Winner: Away
    Confidence: 54.7%

============================================================
✅ Model demo completed successfully!
============================================================
```

## Using Real API Data

To use real CFB API data in the demo workflow:

1. Add your API key as a repository secret:
   - Go to Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `CFB_API_KEY`
   - Value: Your College Football Data API key

2. Run the demo workflow with `use_synthetic_data: false`

## CI Status Badge

Add this badge to your README to show CI status:

```markdown
![CI Status](https://github.com/zachringnight/cfbmodel/actions/workflows/ci.yml/badge.svg)
```

## Workflow Files Location

- `.github/workflows/ci.yml` - Continuous Integration workflow
- `.github/workflows/model-demo.yml` - Manual demo workflow

## Benefits

✅ **Automated Testing**: Catch issues before they reach production  
✅ **Multi-version Support**: Ensure compatibility across Python versions  
✅ **Easy Demonstrations**: Show model capabilities without local setup  
✅ **Quality Assurance**: Validate changes automatically  
✅ **Documentation**: Workflow runs serve as living documentation  
