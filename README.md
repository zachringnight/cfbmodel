# College Football Prediction Model

A machine learning model for predicting college football game outcomes using data from the [College Football Data API](https://collegefootballdata.com/).

## Features

- Fetches real-time college football data from the official API
- Preprocesses and engineers features from team statistics and historical data
- Trains machine learning models (Random Forest and Gradient Boosting) to predict game outcomes
- Provides game predictions with confidence scores
- Supports multiple seasons and configurable parameters

## Prerequisites

- Python 3.7 or higher
- College Football Data API key (get one at https://collegefootballdata.com/)

## Installation

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

## Usage

### Training a Model

Train a model using data from a specific season:

```bash
python main.py --api-key YOUR_API_KEY --year 2023 --train
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

## API Key

The College Football Data API requires an API key for access. You can obtain a free API key by:

1. Visiting https://collegefootballdata.com/
2. Creating an account
3. Generating an API key from your account settings

**Important**: Keep your API key secure and do not commit it to version control.

## Project Structure

```
cfbmodel/
├── data_fetcher.py    # API client for fetching data
├── preprocessor.py    # Data preprocessing and feature engineering
├── model.py           # Machine learning model definitions
├── main.py            # Main entry point for training and prediction
├── requirements.txt   # Python dependencies
└── README.md          # This file
```

## Model Features

The model uses the following features for predictions:

- **Offensive Statistics**: Total yards, passing yards, rushing yards, points scored
- **Team Talent Ratings**: Recruiting and talent composite scores
- **Differential Features**: Calculated differences between home and away team stats
- **Historical Performance**: Season-long averages and trends

## Model Performance

The model's performance varies based on the training data and season. Typical results:
- Training Accuracy: 65-75%
- Cross-Validation Accuracy: 60-70%
- Test Accuracy: 60-70%

Feature importance analysis shows that talent ratings and offensive statistics are the most predictive features.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Acknowledgments

- Data provided by [CollegeFootballData.com](https://collegefootballdata.com/)
- Built with scikit-learn, pandas, and numpy