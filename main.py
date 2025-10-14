"""
Main entry point for the CFB model
"""

import argparse
import os
from data_fetcher import CFBDataFetcher
from preprocessor import CFBPreprocessor
from model import CFBModel


def main():
    """Main function to run the CFB model"""
    parser = argparse.ArgumentParser(description="College Football Prediction Model")
    parser.add_argument("--api-key", required=True, help="College Football Data API key")
    parser.add_argument("--year", type=int, required=True, help="Season year")
    parser.add_argument("--train", action="store_true", help="Train the model")
    parser.add_argument("--predict", action="store_true", help="Make predictions")
    parser.add_argument("--week", type=int, help="Week number for predictions")
    parser.add_argument("--model-path", default="cfb_model.pkl", help="Path to save/load model")
    
    args = parser.parse_args()
    
    # Initialize components
    print(f"Initializing CFB Model for {args.year} season...")
    fetcher = CFBDataFetcher(args.api_key)
    preprocessor = CFBPreprocessor()
    model = CFBModel(model_type="random_forest")
    
    if args.train:
        print("\n=== Training Model ===")
        
        # Fetch training data
        print("Fetching games data...")
        games = fetcher.get_games(args.year, season_type="regular")
        print(f"Fetched {len(games)} games")
        
        print("Fetching team statistics...")
        team_stats = fetcher.get_team_stats(args.year)
        print(f"Fetched stats for {len(team_stats)} teams")
        
        # Try to get talent data (may not be available for all years)
        try:
            print("Fetching team talent ratings...")
            talent = fetcher.get_team_talent(args.year)
            print(f"Fetched talent ratings for {len(talent)} teams")
        except Exception as e:
            print(f"Could not fetch talent data: {e}")
            talent = None
        
        # Prepare features
        print("\nPreparing features...")
        features = preprocessor.prepare_game_features(games, team_stats, talent)
        X, y = preprocessor.create_training_data(features)
        
        print(f"Training data shape: {X.shape}")
        print(f"Target distribution: {y.value_counts().to_dict()}")
        
        # Train model
        print("\nTraining model...")
        metrics = model.train(X, y)
        
        # Print results
        print("\n=== Training Results ===")
        print(f"Training Accuracy: {metrics['train_accuracy']:.4f}")
        print(f"Test Accuracy: {metrics['test_accuracy']:.4f}")
        print(f"Cross-Validation Mean: {metrics['cv_mean']:.4f} (+/- {metrics['cv_std']:.4f})")
        
        print("\nTop 5 Feature Importances:")
        sorted_features = sorted(metrics['feature_importance'].items(), 
                                key=lambda x: x[1], reverse=True)
        for feat, imp in sorted_features[:5]:
            print(f"  {feat}: {imp:.4f}")
        
        print("\nClassification Report:")
        print(metrics['classification_report'])
        
        # Save model
        model.save(args.model_path)
        print(f"\nModel saved to {args.model_path}")
    
    if args.predict:
        print("\n=== Making Predictions ===")
        
        if not os.path.exists(args.model_path):
            print(f"Error: Model file {args.model_path} not found. Train a model first.")
            return
        
        # Load model
        model.load(args.model_path)
        print(f"Model loaded from {args.model_path}")
        
        # Fetch data for predictions
        week = args.week if args.week else None
        print(f"Fetching games for week {week}...")
        games = fetcher.get_games(args.year, week=week, season_type="regular")
        
        if len(games) == 0:
            print("No games found for the specified criteria.")
            return
        
        print(f"Found {len(games)} games")
        
        print("Fetching team statistics...")
        team_stats = fetcher.get_team_stats(args.year)
        
        try:
            talent = fetcher.get_team_talent(args.year)
        except:
            talent = None
        
        # Prepare features
        features = preprocessor.prepare_game_features(games, team_stats, talent)
        X, _ = preprocessor.create_training_data(features)
        
        # Make predictions
        predictions = model.predict(X)
        probabilities = model.predict_proba(X)
        
        # Display predictions
        print("\n=== Predictions ===")
        for i, (_, game) in enumerate(games.iterrows()):
            home = game.get('home_team', 'Unknown')
            away = game.get('away_team', 'Unknown')
            pred = "Home Win" if predictions[i] == 1 else "Away Win"
            prob = probabilities[i][predictions[i]]
            
            print(f"{away} @ {home}")
            print(f"  Prediction: {pred} (Confidence: {prob:.2%})")
            print()


if __name__ == "__main__":
    main()
