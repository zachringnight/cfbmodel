#!/bin/bash
# Quick Start Script: Run predictions for this week's games
#
# This script demonstrates how to run the CFB model for the current week's games.
# It will automatically detect the current week and generate predictions.

echo "=================================================================="
echo "CFB Model - Running Predictions for This Week's Games"
echo "=================================================================="
echo ""

# Check if API key is set
if [ -z "$CFB_API_KEY" ]; then
    echo "❌ Error: CFB_API_KEY environment variable is not set"
    echo ""
    echo "To run predictions with real data, you need an API key:"
    echo "  1. Get an API key from https://collegefootballdata.com/"
    echo "  2. Set the environment variable:"
    echo "     export CFB_API_KEY='your_api_key_here'"
    echo ""
    echo "Alternatively, run the test script without an API key:"
    echo "  python test_weekly_predictions.py"
    exit 1
fi

echo "✓ API key found"
echo ""

# Determine current year
CURRENT_YEAR=$(date +%Y)
TRAIN_YEAR=$((CURRENT_YEAR - 1))

echo "Current season: $CURRENT_YEAR"
echo "Training on: $TRAIN_YEAR season data"
echo ""

# Option 1: Train a new model and make predictions
echo "=================================================================="
echo "Option 1: Train model and make predictions"
echo "=================================================================="
echo ""
echo "Command:"
echo "  python run_weekly_predictions.py --train --train-year $TRAIN_YEAR"
echo ""
read -p "Run this option? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python run_weekly_predictions.py --train --train-year "$TRAIN_YEAR"
    exit 0
fi

# Option 2: Use existing model
echo ""
echo "=================================================================="
echo "Option 2: Use existing model (if available)"
echo "=================================================================="
echo ""

if [ -f "cfb_model.pkl" ]; then
    echo "✓ Found existing model: cfb_model.pkl"
    echo ""
    echo "Command:"
    echo "  python run_weekly_predictions.py --model-path cfb_model.pkl"
    echo ""
    read -p "Run this option? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python run_weekly_predictions.py --model-path cfb_model.pkl
        exit 0
    fi
else
    echo "❌ No existing model found. Please use Option 1 to train a model first."
fi

echo ""
echo "=================================================================="
echo "For more options and usage information, see:"
echo "  - WEEKLY_PREDICTIONS_GUIDE.md"
echo "  - python run_weekly_predictions.py --help"
echo "=================================================================="
