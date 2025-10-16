#!/usr/bin/env python3
"""
Run predictions and save outputs in multiple formats (text, JSON, CSV)
"""

import argparse
import os
import sys
import json
from datetime import datetime
from data_fetcher import CFBDataFetcher
from preprocessor import CFBPreprocessor
from model import CFBModel


def get_current_week(year, start_date=None):
    """
    Calculate the current CFB week based on the current date
    
    Args:
        year: Season year
        start_date: Optional start date of the season
        
    Returns:
        Current week number (1-15 for regular season)
    """
    from datetime import datetime, timedelta
    
    if start_date is None:
        # CFB season typically starts the Saturday after Labor Day
        first_day = datetime(year, 9, 1)
        days_until_monday = (7 - first_day.weekday()) % 7
        labor_day = first_day + timedelta(days=days_until_monday)
        season_start = labor_day + timedelta(days=5)
        
        # However, some years have Week 0 games the Saturday before Labor Day
        week_zero_start = datetime(year, 8, 24)
        while week_zero_start.weekday() != 5:  # 5 = Saturday
            week_zero_start += timedelta(days=1)
        
        # Use week 0 start as actual season start
        season_start = week_zero_start
    else:
        season_start = start_date
    
    # Calculate weeks since season start
    current_date = datetime.now()
    days_since_start = (current_date - season_start).days
    current_week = (days_since_start // 7) + 1
    
    # Clamp to valid week range (0-15 for regular season)
    current_week = max(0, min(current_week, 15))
    
    return current_week


def save_predictions_json(predictions_data, output_file):
    """Save predictions to JSON file"""
    with open(output_file, 'w') as f:
        json.dump(predictions_data, f, indent=2)
    print(f"✓ Predictions saved to {output_file}")


def save_predictions_csv(predictions_data, output_file):
    """Save predictions to CSV file"""
    import pandas as pd
    
    # Convert to DataFrame
    df = pd.DataFrame(predictions_data['predictions'])
    df.to_csv(output_file, index=False)
    print(f"✓ Predictions saved to {output_file}")


def main():
    """Main function to run predictions and save outputs"""
    parser = argparse.ArgumentParser(
        description="Run CFB model predictions with structured outputs"
    )
    parser.add_argument(
        "--api-key",
        help="College Football Data API key (or set CFB_API_KEY env var)",
        default=os.environ.get("CFB_API_KEY")
    )
    parser.add_argument(
        "--year",
        type=int,
        default=datetime.now().year,
        help="Season year (default: current year)"
    )
    parser.add_argument(
        "--week",
        type=int,
        help="Specific week number (default: automatically determined)"
    )
    parser.add_argument(
        "--model-path",
        default="cfb_model.pkl",
        help="Path to trained model file"
    )
    parser.add_argument(
        "--train",
        action="store_true",
        help="Train a new model before making predictions"
    )
    parser.add_argument(
        "--train-year",
        type=int,
        help="Year to use for training (default: previous year)"
    )
    parser.add_argument(
        "--output-json",
        default="predictions.json",
        help="Output JSON file path"
    )
    parser.add_argument(
        "--output-csv",
        default="predictions.csv",
        help="Output CSV file path"
    )
    
    args = parser.parse_args()
    
    # Validate API key
    if not args.api_key:
        print("Error: API key required. Set CFB_API_KEY environment variable or use --api-key")
        print("Get your API key from https://collegefootballdata.com/")
        sys.exit(1)
    
    # Determine week
    if args.week:
        week = args.week
        print(f"Using specified week: {week}")
    else:
        week = get_current_week(args.year)
        print(f"Automatically determined current week: {week}")
    
    print(f"\n{'='*70}")
    print(f"CFB Model - Week {week} Predictions for {args.year} Season")
    print(f"{'='*70}\n")
    
    # Initialize components
    fetcher = CFBDataFetcher(args.api_key)
    preprocessor = CFBPreprocessor()
    model = CFBModel(model_type="random_forest")
    
    # Train model if requested
    if args.train:
        train_year = args.train_year or (args.year - 1)
        print(f"\n=== Training Model on {train_year} Season ===\n")
        
        try:
            # Fetch training data
            print("Fetching training data...")
            games = fetcher.get_games(train_year, season_type="regular")
            print(f"  ✓ Fetched {len(games)} games")
            
            team_stats = fetcher.get_team_stats(train_year)
            print(f"  ✓ Fetched stats for {len(team_stats)} teams")
            
            try:
                talent = fetcher.get_team_talent(train_year)
                print(f"  ✓ Fetched talent ratings for {len(talent)} teams")
            except Exception as e:
                print(f"  ⚠ Could not fetch talent data: {e}")
                talent = None
            
            # Prepare and train
            print("\nPreparing features...")
            features = preprocessor.prepare_game_features(games, team_stats, talent)
            X, y = preprocessor.create_training_data(features)
            
            print(f"  ✓ Training data shape: {X.shape}")
            print(f"  ✓ Target distribution: {y.sum()} home wins, {len(y) - y.sum()} away wins")
            
            print("\nTraining model...")
            metrics = model.train(X, y)
            
            print("\n=== Training Results ===")
            print(f"Training Accuracy: {metrics['train_accuracy']:.2%}")
            print(f"Test Accuracy: {metrics['test_accuracy']:.2%}")
            print(f"Cross-Validation: {metrics['cv_mean']:.2%} (±{metrics['cv_std']:.2%})")
            
            # Save model
            model.save(args.model_path)
            print(f"\n✓ Model saved to {args.model_path}")
            
        except Exception as e:
            print(f"\n✗ Error during training: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    # Load existing model if not training
    elif os.path.exists(args.model_path):
        print(f"Loading model from {args.model_path}...")
        try:
            model.load(args.model_path)
            print("✓ Model loaded successfully\n")
        except Exception as e:
            print(f"✗ Error loading model: {e}")
            print("\nTip: Train a model first using --train flag")
            sys.exit(1)
    else:
        print(f"✗ Model file not found: {args.model_path}")
        print("\nTip: Train a model first using --train flag")
        sys.exit(1)
    
    # Fetch games for prediction
    print(f"\n=== Fetching Week {week} Games ===\n")
    
    try:
        games = fetcher.get_games(args.year, week=week, season_type="regular")
        
        if len(games) == 0:
            print(f"No games found for week {week} of the {args.year} season.")
            print("\nPossible reasons:")
            print("  • Week number may be incorrect")
            print("  • Games may not be scheduled yet")
            print("  • Season may not have started")
            
            # Save empty results
            empty_results = {
                "metadata": {
                    "year": args.year,
                    "week": week,
                    "generated_at": datetime.now().isoformat(),
                    "model_path": args.model_path,
                    "games_found": 0
                },
                "predictions": []
            }
            save_predictions_json(empty_results, args.output_json)
            save_predictions_csv(empty_results, args.output_csv)
            
            sys.exit(0)
        
        print(f"✓ Found {len(games)} games for week {week}\n")
        
        # Fetch team stats for current season
        print("Fetching team statistics...")
        team_stats = fetcher.get_team_stats(args.year)
        print(f"  ✓ Fetched stats for {len(team_stats)} teams")
        
        try:
            talent = fetcher.get_team_talent(args.year)
            print(f"  ✓ Fetched talent ratings for {len(talent)} teams")
        except:
            talent = None
            print(f"  ⚠ Talent data not available for {args.year}")
        
        # Prepare features
        print("\nPreparing features for prediction...")
        features = preprocessor.prepare_game_features(games, team_stats, talent)
        X, _ = preprocessor.create_training_data(features)
        print(f"  ✓ Feature matrix shape: {X.shape}")
        
        # Make predictions
        print("\nGenerating predictions...\n")
        predictions = model.predict(X)
        probabilities = model.predict_proba(X)
        
        # Build structured output
        predictions_list = []
        
        print(f"{'='*70}")
        print(f"PREDICTIONS FOR WEEK {week} - {args.year} SEASON")
        print(f"{'='*70}\n")
        
        for i, (_, game) in enumerate(games.iterrows()):
            # Handle different column name formats
            home = game.get('home_team', game.get('homeTeam', 'Unknown'))
            away = game.get('away_team', game.get('awayTeam', 'Unknown'))
            
            # Get start date if available
            start_date = game.get('start_date', game.get('startDate', ''))
            
            # Prediction details
            pred = predictions[i]
            prob = probabilities[i]
            
            if pred == 1:
                winner = home
                winner_prob = prob[1]
            else:
                winner = away
                winner_prob = prob[0]
            
            # Build prediction entry
            prediction_entry = {
                "game_number": i + 1,
                "home_team": home,
                "away_team": away,
                "start_date": start_date,
                "predicted_winner": winner,
                "confidence": round(winner_prob * 100, 2),
                "home_win_probability": round(prob[1] * 100, 2),
                "away_win_probability": round(prob[0] * 100, 2)
            }
            predictions_list.append(prediction_entry)
            
            # Confidence bar
            bar_width = int(winner_prob * 30)
            confidence_bar = '█' * bar_width + '░' * (30 - bar_width)
            
            # Display matchup
            print(f"Game {i+1}: {away} @ {home}")
            if start_date:
                print(f"  Date: {start_date}")
            print(f"  Predicted Winner: {winner}")
            print(f"  Confidence: {confidence_bar} {winner_prob:.1%}")
            print(f"  Probability: Home {prob[1]:.1%} | Away {prob[0]:.1%}")
            print()
        
        print(f"{'='*70}")
        print(f"Generated {len(games)} predictions for week {week}")
        print(f"{'='*70}")
        
        # Save predictions to files
        output_data = {
            "metadata": {
                "year": args.year,
                "week": week,
                "generated_at": datetime.now().isoformat(),
                "model_path": args.model_path,
                "games_found": len(games),
                "model_type": model.model_type
            },
            "predictions": predictions_list
        }
        
        print(f"\n=== Saving Outputs ===\n")
        save_predictions_json(output_data, args.output_json)
        save_predictions_csv(output_data, args.output_csv)
        
        print(f"\n✓ All outputs generated successfully")
        
    except Exception as e:
        print(f"\n✗ Error making predictions: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
