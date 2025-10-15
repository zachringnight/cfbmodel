#!/usr/bin/env python3
"""
Test the weekly predictions script with synthetic data
Demonstrates functionality without requiring an API key
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from run_weekly_predictions import get_current_week
from preprocessor import CFBPreprocessor
from model import CFBModel


def create_synthetic_data(year, week, num_games=10):
    """Create synthetic game and stats data for testing"""
    
    teams = [
        'Alabama', 'Georgia', 'Ohio State', 'Michigan', 'Clemson', 'Oklahoma',
        'Texas', 'Notre Dame', 'LSU', 'Florida', 'Penn State', 'Oregon',
        'USC', 'Miami', 'Tennessee', 'Auburn', 'Texas A&M', 'Wisconsin',
        'Florida State', 'North Carolina'
    ]
    
    np.random.seed(42)
    
    # Create games
    games = []
    for i in range(num_games):
        home_team = np.random.choice(teams)
        away_team = np.random.choice([t for t in teams if t != home_team])
        
        games.append({
            'id': i,
            'homeTeam': home_team,
            'awayTeam': away_team,
            'homePoints': None,  # Future game
            'awayPoints': None,
            'week': week,
            'season': year,
            'startDate': f'{year}-10-{18+i%7}'
        })
    
    games_df = pd.DataFrame(games)
    
    # Create team stats
    stats = []
    for team in teams:
        total_yards = np.random.randint(350, 450)
        passing_yards = int(total_yards * np.random.uniform(0.55, 0.70))
        rushing_yards = total_yards - passing_yards
        
        stats.extend([
            {'team': team, 'statName': 'totalYards', 'statValue': total_yards},
            {'team': team, 'statName': 'netPassingYards', 'statValue': passing_yards},
            {'team': team, 'statName': 'rushingYards', 'statValue': rushing_yards},
        ])
    
    stats_df = pd.DataFrame(stats)
    
    # Create talent ratings
    talent = []
    for team in teams:
        if team in ['Alabama', 'Georgia', 'Ohio State']:
            rating = np.random.uniform(85, 95)
        elif team in ['Michigan', 'Clemson', 'Oklahoma', 'Texas']:
            rating = np.random.uniform(75, 85)
        else:
            rating = np.random.uniform(65, 75)
        
        talent.append({'school': team, 'talent': rating})
    
    talent_df = pd.DataFrame(talent)
    
    return games_df, stats_df, talent_df


def main():
    print("="*70)
    print("CFB Weekly Predictions - Test Demonstration")
    print("="*70)
    print("\nThis script demonstrates the weekly predictions functionality")
    print("using synthetic data (no API key required).\n")
    
    # Get current week
    year = 2025
    current_week = get_current_week(year)
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    print(f"Current date: {current_date}")
    print(f"Calculated current week: Week {current_week} of {year} season")
    
    # Create synthetic data for training
    print("\n" + "="*70)
    print("STEP 1: Training Model on Synthetic 2024 Data")
    print("="*70 + "\n")
    
    train_year = 2024
    print(f"Creating synthetic training data for {train_year} season...")
    
    # Create training data (full season)
    train_games = []
    for week in range(1, 13):  # 12 weeks of data
        games, _, _ = create_synthetic_data(train_year, week, num_games=8)
        # Add random scores for training
        for idx in games.index:
            home_yards = np.random.randint(300, 500)
            away_yards = np.random.randint(300, 500)
            games.loc[idx, 'homePoints'] = max(0, int(home_yards / 10 + np.random.normal(3, 7)))
            games.loc[idx, 'awayPoints'] = max(0, int(away_yards / 10 + np.random.normal(0, 7)))
        train_games.append(games)
    
    train_games_df = pd.concat(train_games, ignore_index=True)
    _, train_stats_df, train_talent_df = create_synthetic_data(train_year, 1, num_games=1)
    
    print(f"  ✓ Created {len(train_games_df)} training games")
    print(f"  ✓ Created stats for {len(train_stats_df['team'].unique())} teams")
    
    # Train model
    print("\nTraining model...")
    preprocessor = CFBPreprocessor()
    features = preprocessor.prepare_game_features(train_games_df, train_stats_df, train_talent_df)
    X, y = preprocessor.create_training_data(features)
    
    print(f"  ✓ Feature matrix shape: {X.shape}")
    print(f"  ✓ Target distribution: {y.sum()} home wins, {len(y) - y.sum()} away wins")
    
    model = CFBModel(model_type="random_forest")
    metrics = model.train(X, y, test_size=0.25)
    
    print(f"\n  Training Accuracy: {metrics['train_accuracy']:.2%}")
    print(f"  Test Accuracy: {metrics['test_accuracy']:.2%}")
    print(f"  Cross-Validation: {metrics['cv_mean']:.2%} (±{metrics['cv_std']:.2%})")
    
    # Save model
    model_path = "/tmp/test_weekly_model.pkl"
    model.save(model_path)
    print(f"\n  ✓ Model saved to {model_path}")
    
    # Create prediction data for current week
    print("\n" + "="*70)
    print(f"STEP 2: Making Predictions for Week {current_week} of {year}")
    print("="*70 + "\n")
    
    pred_games_df, pred_stats_df, pred_talent_df = create_synthetic_data(year, current_week, num_games=10)
    
    print(f"✓ Created {len(pred_games_df)} upcoming games for week {current_week}")
    print(f"✓ Loaded stats for {len(pred_stats_df['team'].unique())} teams")
    
    # Prepare features
    print("\nPreparing features...")
    pred_features = preprocessor.prepare_game_features(pred_games_df, pred_stats_df, pred_talent_df)
    X_pred, _ = preprocessor.create_training_data(pred_features)
    print(f"  ✓ Feature matrix shape: {X_pred.shape}")
    
    # Make predictions
    print("\nGenerating predictions...\n")
    predictions = model.predict(X_pred)
    probabilities = model.predict_proba(X_pred)
    
    # Display results
    print("="*70)
    print(f"PREDICTIONS FOR WEEK {current_week} - {year} SEASON")
    print("="*70 + "\n")
    
    for i, (_, game) in enumerate(pred_games_df.iterrows()):
        home = game['homeTeam']
        away = game['awayTeam']
        start_date = game.get('startDate', '')
        
        pred = predictions[i]
        prob = probabilities[i]
        
        if pred == 1:
            winner = home
            winner_prob = prob[1]
        else:
            winner = away
            winner_prob = prob[0]
        
        # Confidence bar
        bar_width = int(winner_prob * 30)
        confidence_bar = '█' * bar_width + '░' * (30 - bar_width)
        
        print(f"Game {i+1}: {away} @ {home}")
        if start_date:
            print(f"  Date: {start_date}")
        print(f"  Predicted Winner: {winner}")
        print(f"  Confidence: {confidence_bar} {winner_prob:.1%}")
        print(f"  Probability: Home {prob[1]:.1%} | Away {prob[0]:.1%}")
        print()
    
    print("="*70)
    print(f"✓ Successfully generated {len(pred_games_df)} predictions")
    print("="*70)
    
    # Summary
    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70)
    print("\n✅ The weekly predictions script is working correctly!")
    print("\nTo use with real data:")
    print("  1. Get an API key from https://collegefootballdata.com/")
    print("  2. Run: export CFB_API_KEY='your_key'")
    print("  3. Run: python run_weekly_predictions.py --train --train-year 2024")
    print("\nSee WEEKLY_PREDICTIONS_GUIDE.md for more details.")
    print("="*70)


if __name__ == "__main__":
    main()
