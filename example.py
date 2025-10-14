"""
Example script demonstrating how to use the CFB model
"""

from data_fetcher import CFBDataFetcher
from preprocessor import CFBPreprocessor
from model import CFBModel

# Example 1: Initialize with your API key
API_KEY = "OvDDxP6B6eSjqOGQYXQ5H6iQ57tzKnYhGgoKmOwuV/fwlIpSp9ssZtHH4OJK7b09"
fetcher = CFBDataFetcher(API_KEY)

# Example 2: Fetch data for a season
print("Fetching 2023 season data...")
games = fetcher.get_games(year=2023, season_type="regular")
team_stats = fetcher.get_team_stats(year=2023)

# Example 3: Try to fetch talent ratings (may not always be available)
try:
    talent = fetcher.get_team_talent(year=2023)
except Exception as e:
    print(f"Talent data not available: {e}")
    talent = None

# Example 4: Prepare features for modeling
preprocessor = CFBPreprocessor()
features = preprocessor.prepare_game_features(games, team_stats, talent)
X, y = preprocessor.create_training_data(features)

print(f"\nDataset shape: {X.shape}")
print(f"Features: {list(X.columns)}")
print(f"\nTarget distribution:")
print(f"  Home wins: {(y == 1).sum()}")
print(f"  Away wins: {(y == 0).sum()}")

# Example 5: Train a model
print("\nTraining Random Forest model...")
model = CFBModel(model_type="random_forest")
metrics = model.train(X, y, test_size=0.2)

print(f"\nModel Performance:")
print(f"  Test Accuracy: {metrics['test_accuracy']:.4f}")
print(f"  CV Score: {metrics['cv_mean']:.4f} (+/- {metrics['cv_std']:.4f})")

# Example 6: Save the model
model.save("example_model.pkl")
print("\nModel saved to example_model.pkl")

# Example 7: Make predictions on new data
print("\nFetching week 10 games for prediction...")
new_games = fetcher.get_games(year=2023, week=10)
new_features = preprocessor.prepare_game_features(new_games, team_stats, talent)
X_new, _ = preprocessor.create_training_data(new_features)

predictions = model.predict(X_new)
probabilities = model.predict_proba(X_new)

print("\nPredictions for Week 10:")
for i, (_, game) in enumerate(new_games.head(5).iterrows()):
    home = game.get('home_team', 'Unknown')
    away = game.get('away_team', 'Unknown')
    winner = "Home" if predictions[i] == 1 else "Away"
    confidence = probabilities[i][predictions[i]]
    print(f"  {away} @ {home}: {winner} wins ({confidence:.1%} confidence)")
