#!/usr/bin/env python3
"""
Simple script to run predictions for this week's games
Just run: python run_this_week.py
"""

import os
import sys
from datetime import datetime

# Check if API key is available
api_key = os.environ.get("CFB_API_KEY")

if not api_key:
    print("="*70)
    print("CFB Model - This Week's Predictions")
    print("="*70)
    print("\n❌ API key not found!")
    print("\nTo run predictions with real data:")
    print("  1. Get an API key from https://collegefootballdata.com/")
    print("  2. Set the environment variable:")
    print("     export CFB_API_KEY='your_api_key_here'")
    print("  3. Run this script again: python run_this_week.py")
    print("\nAlternatively, test without an API key:")
    print("  python test_weekly_predictions.py")
    print("="*70)
    sys.exit(1)

# Import after checking API key
from run_weekly_predictions import main as run_predictions
import argparse

print("="*70)
print("CFB Model - Running Predictions for This Week's Games")
print("="*70)
print()

# Set up arguments for the current week
current_year = datetime.now().year
train_year = current_year - 1

print(f"Current season: {current_year}")
print(f"Will train on: {train_year} season data")
print()
print("Starting prediction process...")
print()

# Override sys.argv to pass arguments to run_predictions
sys.argv = [
    'run_this_week.py',
    '--api-key', api_key,
    '--year', str(current_year),
    '--train',
    '--train-year', str(train_year)
]

# Run the main predictions function
try:
    run_predictions()
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nFor more options, try:")
    print("  python run_weekly_predictions.py --help")
    sys.exit(1)
