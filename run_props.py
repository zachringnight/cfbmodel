#!/usr/bin/env python3
"""
Run CFB Props Model - Generate Actionable Betting Recommendations

This script:
1. Trains (or loads) the props prediction model
2. Fetches current week's games and betting lines
3. Makes predictions for points, totals, and spreads
4. Compares predictions to betting lines
5. Outputs actionable recommendations

Usage:
    python run_props.py --year 2024 --week 10
    python run_props.py --year 2024 --week 10 --train
    python run_props.py --year 2024 --week 10 --min-edge 3.0
"""

import argparse
import json
import os
import sys
import logging
from datetime import datetime
from typing import Optional

import pandas as pd

from props_model import CFBPropsModel, format_actionable_output
from props_preprocessor import CFBPropsPreprocessor, prepare_training_pipeline
from data_fetcher import CFBDataFetcher

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Paths
GAMES_CSV = os.path.join(os.path.dirname(__file__), 'games.csv')
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'props_model.pkl')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'props_output')


def train_props_model(games_filepath: str = GAMES_CSV,
                      min_season: int = 2015,
                      save_path: str = MODEL_PATH) -> CFBPropsModel:
    """
    Train the props model on historical data

    Args:
        games_filepath: Path to games.csv
        min_season: Minimum season year for training data
        save_path: Where to save the trained model

    Returns:
        Trained CFBPropsModel
    """
    logger.info("=" * 60)
    logger.info("TRAINING PROPS MODEL")
    logger.info("=" * 60)

    # Prepare training data
    X, y_home, y_away = prepare_training_pipeline(games_filepath, min_season)

    # Initialize and train model
    model = CFBPropsModel(model_type="random_forest")
    metrics = model.train(X, y_home, y_away)

    # Log metrics summary
    logger.info("\nTraining Metrics Summary:")
    for prop_type, m in metrics.items():
        logger.info(f"  {prop_type}:")
        logger.info(f"    Test MAE: {m['test_mae']:.2f} points")
        logger.info(f"    Test RMSE: {m['test_rmse']:.2f} points")
        logger.info(f"    R-squared: {m['test_r2']:.3f}")

    # Save model
    model.save(save_path)
    logger.info(f"\nModel saved to {save_path}")

    return model


def load_or_train_model(force_train: bool = False) -> CFBPropsModel:
    """
    Load existing model or train a new one

    Args:
        force_train: If True, always train a new model

    Returns:
        CFBPropsModel instance
    """
    model = CFBPropsModel()

    if not force_train and os.path.exists(MODEL_PATH):
        logger.info(f"Loading existing model from {MODEL_PATH}")
        model.load(MODEL_PATH)
    else:
        logger.info("Training new model...")
        model = train_props_model()

    return model


def fetch_week_data(api_key: str, year: int, week: int) -> tuple:
    """
    Fetch games and betting lines for a specific week

    Args:
        api_key: CFB Data API key
        year: Season year
        week: Week number

    Returns:
        Tuple of (games_df, lines_df)
    """
    fetcher = CFBDataFetcher(api_key)

    logger.info(f"Fetching games for {year} week {week}...")
    games_df = fetcher.get_games(year, week)

    logger.info(f"Fetching betting lines for {year} week {week}...")
    lines_df = fetcher.get_betting_lines(year, week)

    return games_df, lines_df


def prepare_prediction_features(games_df: pd.DataFrame,
                                  historical_games_path: str = GAMES_CSV) -> pd.DataFrame:
    """
    Prepare features for prediction using historical data for rolling stats

    Args:
        games_df: Current week's games
        historical_games_path: Path to historical games CSV

    Returns:
        DataFrame with prediction features
    """
    preprocessor = CFBPropsPreprocessor(lookback_games=5)

    # Load historical games for rolling stats
    historical_df = preprocessor.load_games_data(historical_games_path)

    # Calculate rolling stats from historical data
    team_stats = preprocessor.calculate_team_rolling_stats(historical_df)

    # Standardize column names in current games
    if 'homeTeam' in games_df.columns:
        games_df = games_df.rename(columns={
            'homeTeam': 'home_team',
            'awayTeam': 'away_team',
            'homePoints': 'home_points',
            'awayPoints': 'away_points',
            'startDate': 'start_date'
        })

    games_df['start_date'] = pd.to_datetime(games_df['start_date'])

    # Prepare features using historical team stats
    features_df = preprocessor.prepare_props_features(games_df, team_stats)

    return features_df


def run_props_predictions(year: int, week: int,
                          api_key: Optional[str] = None,
                          force_train: bool = False,
                          min_edge: float = 2.0,
                          output_format: str = 'all') -> dict:
    """
    Main function to run props predictions

    Args:
        year: Season year
        week: Week number
        api_key: CFB Data API key (or from env)
        force_train: Whether to force model retraining
        min_edge: Minimum edge in points to recommend
        output_format: Output format ('json', 'csv', 'text', 'all')

    Returns:
        Dictionary with predictions and recommendations
    """
    logger.info("=" * 60)
    logger.info(f"CFB PROPS PREDICTIONS - {year} Week {week}")
    logger.info("=" * 60)

    # Get API key
    if not api_key:
        api_key = os.environ.get('CFB_API_KEY')

    if not api_key:
        logger.warning("No API key provided - using historical data only")

    # Load or train model
    model = load_or_train_model(force_train)

    results = {
        'year': year,
        'week': week,
        'generated_at': datetime.now().isoformat(),
        'predictions': [],
        'recommendations': [],
        'summary': {}
    }

    try:
        if api_key:
            # Fetch current week data from API
            games_df, lines_df = fetch_week_data(api_key, year, week)

            if games_df.empty:
                logger.warning(f"No games found for {year} week {week}")
                return results

            # Prepare features
            features_df = prepare_prediction_features(games_df)

            # Process betting lines
            preprocessor = CFBPropsPreprocessor()
            processed_lines = preprocessor.process_betting_lines(lines_df)

            # Merge features with lines
            merged_df = preprocessor.merge_features_with_lines(features_df, processed_lines)

        else:
            # Use historical data for demo
            logger.info("Using historical data for demonstration...")
            preprocessor = CFBPropsPreprocessor()
            games_df = preprocessor.load_games_data(GAMES_CSV)

            # Filter to requested year/week
            games_df = games_df[(games_df['season'] == year) & (games_df['week'] == week)]

            if games_df.empty:
                logger.warning(f"No historical games found for {year} week {week}")
                return results

            features_df = prepare_prediction_features(games_df)
            merged_df = features_df.copy()
            merged_df['spread'] = None
            merged_df['over_under'] = None

        # Get feature columns for prediction
        feature_cols = [col for col in [
            'home_rolling_pts_scored', 'home_rolling_pts_allowed', 'home_rolling_margin',
            'home_rolling_win_pct', 'home_games_played',
            'away_rolling_pts_scored', 'away_rolling_pts_allowed', 'away_rolling_margin',
            'away_rolling_win_pct', 'away_games_played',
            'home_elo', 'away_elo', 'elo_diff',
            'margin_diff', 'pts_scored_diff', 'pts_allowed_diff', 'win_pct_diff',
            'expected_total', 'neutral_site', 'conference_game'
        ] if col in merged_df.columns]

        X_pred = merged_df[feature_cols].fillna(0)

        # Make predictions
        predictions = model.predict_with_confidence(X_pred)

        # Add predictions to merged df for output
        merged_df['pred_home_points'] = predictions['home_points']['prediction']
        merged_df['pred_away_points'] = predictions['away_points']['prediction']
        merged_df['pred_total'] = predictions['game_total']['prediction']
        merged_df['pred_spread'] = predictions['spread']['prediction']

        # Get actionable recommendations
        lines_for_action = merged_df[['home_team', 'away_team', 'spread', 'over_under']].copy()
        lines_for_action.index = range(len(lines_for_action))

        recommendations_df = model.get_actionable_props(
            X_pred,
            lines_for_action,
            min_edge=min_edge
        )

        # Prepare results
        for _, row in merged_df.iterrows():
            pred = {
                'home_team': row['home_team'],
                'away_team': row['away_team'],
                'pred_home_points': round(row['pred_home_points'], 1),
                'pred_away_points': round(row['pred_away_points'], 1),
                'pred_total': round(row['pred_total'], 1),
                'pred_spread': round(row['pred_spread'], 1),
                'book_spread': row.get('spread'),
                'book_total': row.get('over_under')
            }
            results['predictions'].append(pred)

        # Add recommendations
        for _, row in recommendations_df.iterrows():
            rec = row.to_dict()
            # Clean up NaN values for JSON
            rec = {k: (None if pd.isna(v) else v) for k, v in rec.items()}
            results['recommendations'].append(rec)

        # Summary
        spread_edges = recommendations_df[recommendations_df.get('spread_rec', 'NO EDGE') != 'NO EDGE']
        total_edges = recommendations_df[recommendations_df.get('total_rec', 'NO EDGE') != 'NO EDGE']

        results['summary'] = {
            'games_analyzed': len(merged_df),
            'games_with_lines': merged_df['spread'].notna().sum(),
            'spread_recommendations': len(spread_edges),
            'total_recommendations': len(total_edges),
            'min_edge_threshold': min_edge
        }

        # Save outputs
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        if output_format in ['json', 'all']:
            json_path = os.path.join(OUTPUT_DIR, f'props_{year}_week{week}_{timestamp}.json')
            with open(json_path, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            logger.info(f"JSON output saved to {json_path}")

        if output_format in ['csv', 'all']:
            csv_path = os.path.join(OUTPUT_DIR, f'props_{year}_week{week}_{timestamp}.csv')
            recommendations_df.to_csv(csv_path, index=False)
            logger.info(f"CSV output saved to {csv_path}")

        if output_format in ['text', 'all']:
            text_report = format_actionable_output(recommendations_df)
            txt_path = os.path.join(OUTPUT_DIR, f'props_{year}_week{week}_{timestamp}.txt')
            with open(txt_path, 'w') as f:
                f.write(text_report)
            logger.info(f"Text report saved to {txt_path}")

            # Also print to console
            print("\n" + text_report)

    except Exception as e:
        logger.error(f"Error running predictions: {e}")
        raise

    return results


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Run CFB Props Model for actionable betting recommendations'
    )
    parser.add_argument('--year', type=int, required=True,
                        help='Season year (e.g., 2024)')
    parser.add_argument('--week', type=int, required=True,
                        help='Week number (1-20)')
    parser.add_argument('--api-key', type=str, default=None,
                        help='CFB Data API key (or set CFB_API_KEY env var)')
    parser.add_argument('--train', action='store_true',
                        help='Force model retraining')
    parser.add_argument('--min-edge', type=float, default=2.0,
                        help='Minimum edge in points to recommend (default: 2.0)')
    parser.add_argument('--output', type=str, default='all',
                        choices=['json', 'csv', 'text', 'all'],
                        help='Output format (default: all)')

    args = parser.parse_args()

    # Validate inputs
    if args.week < 1 or args.week > 20:
        logger.error("Week must be between 1 and 20")
        sys.exit(1)

    if args.year < 2000 or args.year > 2100:
        logger.error("Year must be between 2000 and 2100")
        sys.exit(1)

    # Run predictions
    results = run_props_predictions(
        year=args.year,
        week=args.week,
        api_key=args.api_key,
        force_train=args.train,
        min_edge=args.min_edge,
        output_format=args.output
    )

    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Games analyzed: {results['summary'].get('games_analyzed', 0)}")
    print(f"Games with betting lines: {results['summary'].get('games_with_lines', 0)}")
    print(f"Spread recommendations: {results['summary'].get('spread_recommendations', 0)}")
    print(f"Total (O/U) recommendations: {results['summary'].get('total_recommendations', 0)}")
    print("=" * 60)


if __name__ == '__main__':
    main()
