#!/usr/bin/env python3
"""
End-to-End Demo: CFB Model Working Example
Demonstrates the complete workflow without requiring an API key
"""

import pandas as pd
import numpy as np
from model import CFBModel
from preprocessor import CFBPreprocessor

print("="*70)
print("CFB MODEL - END-TO-END DEMONSTRATION")
print("="*70)
print("\nThis demo shows the complete workflow of the CFB model using synthetic data.")
print("In production, this data would come from the College Football Data API.\n")

# Step 1: Create synthetic game data
print("STEP 1: Creating synthetic game data (simulates API response)")
print("-" * 70)

np.random.seed(42)
n_games = 100

# Create realistic team names
teams = [
    'Alabama', 'Georgia', 'Ohio State', 'Michigan', 'Clemson', 'Oklahoma',
    'Texas', 'Notre Dame', 'LSU', 'Florida', 'Penn State', 'Oregon',
    'USC', 'Miami', 'Tennessee', 'Auburn', 'Texas A&M', 'Wisconsin'
]

# Generate random games
games = []
for i in range(n_games):
    home_team = np.random.choice(teams)
    away_team = np.random.choice([t for t in teams if t != home_team])
    
    # Home team advantage + talent determines score
    home_yards = np.random.randint(300, 500)
    away_yards = np.random.randint(300, 500)
    
    # Points roughly correlate with yards
    home_points = max(0, int(home_yards / 10 + np.random.normal(0, 7)))
    away_points = max(0, int(away_yards / 10 + np.random.normal(0, 7)))
    
    games.append({
        'id': i,
        'homeTeam': home_team,
        'awayTeam': away_team,
        'homePoints': home_points,
        'awayPoints': away_points,
    })

games_df = pd.DataFrame(games)
print(f"✅ Created {len(games_df)} synthetic games")
print(f"   Sample: {games_df.iloc[0]['awayTeam']} @ {games_df.iloc[0]['homeTeam']}")
print(f"   Score: {games_df.iloc[0]['awayPoints']}-{games_df.iloc[0]['homePoints']}")

# Step 2: Create synthetic team statistics
print("\nSTEP 2: Creating synthetic team statistics")
print("-" * 70)

stats = []
for team in teams:
    # Each team has offensive stats
    total_yards = np.random.randint(350, 450)
    passing_yards = int(total_yards * np.random.uniform(0.55, 0.70))
    rushing_yards = total_yards - passing_yards
    
    stats.extend([
        {'team': team, 'statName': 'totalYards', 'statValue': total_yards},
        {'team': team, 'statName': 'passingYards', 'statValue': passing_yards},
        {'team': team, 'statName': 'rushingYards', 'statValue': rushing_yards},
    ])

stats_df = pd.DataFrame(stats)
print(f"✅ Created statistics for {len(teams)} teams")
print(f"   Total stat records: {len(stats_df)}")

# Step 3: Create synthetic talent data
print("\nSTEP 3: Creating synthetic talent ratings")
print("-" * 70)

talent = []
for team in teams:
    # Top teams have higher talent
    if team in ['Alabama', 'Georgia', 'Ohio State']:
        rating = np.random.uniform(85, 95)
    elif team in ['Michigan', 'Clemson', 'Oklahoma', 'Texas']:
        rating = np.random.uniform(75, 85)
    else:
        rating = np.random.uniform(65, 75)
    
    talent.append({'school': team, 'talent': rating})

talent_df = pd.DataFrame(talent)
print(f"✅ Created talent ratings for {len(teams)} teams")
print(f"   Top team: {talent_df.nlargest(1, 'talent').iloc[0]['school']} "
      f"(rating: {talent_df.nlargest(1, 'talent').iloc[0]['talent']:.1f})")

# Step 4: Preprocess data
print("\nSTEP 4: Preprocessing and feature engineering")
print("-" * 70)

preprocessor = CFBPreprocessor()
features = preprocessor.prepare_game_features(games_df, stats_df, talent_df)
X, y = preprocessor.create_training_data(features)

print(f"✅ Created feature matrix: {X.shape}")
print(f"   Features: {', '.join(X.columns[:5].tolist())}...")
print(f"   Target distribution: Home wins={sum(y)}, Away wins={len(y)-sum(y)}")

# Step 5: Train model
print("\nSTEP 5: Training machine learning model")
print("-" * 70)

model = CFBModel(model_type="random_forest")
metrics = model.train(X, y, test_size=0.25)

print(f"✅ Model trained successfully!")
print(f"   Training Accuracy: {metrics['train_accuracy']:.1%}")
print(f"   Test Accuracy: {metrics['test_accuracy']:.1%}")
print(f"   Cross-Validation: {metrics['cv_mean']:.1%} (±{metrics['cv_std']:.1%})")

print("\n   Top 3 Most Important Features:")
sorted_features = sorted(metrics['feature_importance'].items(), 
                        key=lambda x: x[1], reverse=True)
for i, (feat, imp) in enumerate(sorted_features[:3], 1):
    print(f"   {i}. {feat}: {imp:.1%}")

# Step 6: Make predictions on new games
print("\nSTEP 6: Making predictions on upcoming games")
print("-" * 70)

# Create 5 "upcoming" games for prediction
upcoming_games = []
matchups = [
    ('Alabama', 'Georgia'),
    ('Ohio State', 'Michigan'),
    ('Clemson', 'Notre Dame'),
    ('Texas', 'Oklahoma'),
    ('USC', 'Oregon'),
]

for home, away in matchups:
    upcoming_games.append({
        'homeTeam': home,
        'awayTeam': away,
        'homePoints': None,  # Unknown (future game)
        'awayPoints': None,
    })

upcoming_df = pd.DataFrame(upcoming_games)

# Prepare features for prediction
pred_features = preprocessor.prepare_game_features(upcoming_df, stats_df, talent_df)
X_pred, _ = preprocessor.create_training_data(pred_features)

# Make predictions
predictions = model.predict(X_pred)
probabilities = model.predict_proba(X_pred)

print("✅ Predictions generated for 5 games:\n")

for i, (_, game) in enumerate(upcoming_df.iterrows()):
    home = game['homeTeam']
    away = game['awayTeam']
    
    if predictions[i] == 1:
        winner = home
        confidence = probabilities[i][1]
    else:
        winner = away
        confidence = probabilities[i][0]
    
    # Visual confidence bar
    bar_length = int(confidence * 20)
    bar = '█' * bar_length + '░' * (20 - bar_length)
    
    print(f"   {away:15s} @ {home:15s}")
    print(f"   → Predicted Winner: {winner:15s} {bar} {confidence:.1%}")
    print()

# Step 7: Save model
print("STEP 7: Saving trained model")
print("-" * 70)

model_path = "/tmp/demo_cfb_model.pkl"
model.save(model_path)
print(f"✅ Model saved to {model_path}")

# Step 8: Load and verify
print("\nSTEP 8: Loading model and verifying")
print("-" * 70)

model2 = CFBModel()
model2.load(model_path)

# Verify predictions match
predictions2 = model2.predict(X_pred)
match = all(predictions == predictions2)

print(f"✅ Model loaded successfully")
print(f"   Predictions match: {match}")

# Summary
print("\n" + "="*70)
print("DEMONSTRATION COMPLETE")
print("="*70)
print("\n✅ All steps completed successfully!")
print("\nThe CFB Model is fully functional and ready for use.")
print("With a valid API key, you can:")
print("  1. Fetch real game data from College Football Data API")
print("  2. Train models on historical seasons")
print("  3. Make predictions on upcoming games")
print("  4. Analyze feature importance and model performance")
print("\nFor more information, see README.md and FUNCTIONALITY_VERIFICATION.md")
print("="*70)
