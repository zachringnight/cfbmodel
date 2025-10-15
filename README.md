# College Football Prediction Model

A production-ready machine learning model for predicting college football game outcomes using data from the [College Football Data API](https://collegefootballdata.com/).

## Features

- 🔄 **Robust API Client** with automatic retry logic and timeout handling
- 🤖 **Machine Learning Models** (Random Forest and Gradient Boosting) for game outcome prediction
- 📊 **Feature Engineering** from team statistics, talent ratings, and historical data
- 🔍 **Comprehensive Logging** for debugging and monitoring
- ✅ **Input Validation** with detailed error messages
- 🧪 **Unit Tests** for core functionality
- ⚙️ **Configurable Parameters** via config.py
- 📈 **Confidence Scores** for each prediction

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
pip install -r requirements.txt
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

## Configuration

Modify `config.py` to customize model parameters:

- **Model Type**: Random Forest or Gradient Boosting
- **Model Hyperparameters**: n_estimators, max_depth, learning_rate, etc.
- **API Settings**: Timeout, retry attempts
- **Logging Level**: DEBUG, INFO, WARNING, ERROR

## Project Structure

```
cfbmodel/
├── data_fetcher.py       # API client with retry logic and validation
├── preprocessor.py       # Data preprocessing and feature engineering
├── model.py              # ML model definitions with logging
├── main.py               # CLI interface
├── config.py             # Configuration parameters
├── test_cfb_model.py     # Unit tests
├── example.py            # Usage examples
├── requirements.txt      # Python dependencies
├── TESTING_SUMMARY.md    # Test results and validation
└── README.md             # This file
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

## API Key

The College Football Data API requires an API key for access. You can obtain a free API key by:

1. Visiting https://collegefootballdata.com/
2. Creating an account
3. Generating an API key from your account settings

**Important**: Keep your API key secure and do not commit it to version control.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Acknowledgments

- Data provided by [CollegeFootballData.com](https://collegefootballdata.com/)
- Built with scikit-learn, pandas, and numpy