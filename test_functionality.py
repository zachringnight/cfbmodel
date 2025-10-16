#!/usr/bin/env python3
"""
Comprehensive functionality test for CFB Model
Tests all core features without requiring an API key
"""

import sys
import os
import sys
from functools import wraps
from pathlib import Path

import numpy as np
import pandas as pd

# Test results
test_results = []

def register_test(name):
    """Decorator to track test results without interfering with pytest."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except Exception as exc:  # pragma: no cover - exercised via pytest
                print(f"❌ FAIL: {name}")
                print(f"   Error: {exc}")
                test_results.append((name, False, str(exc)))
                raise
            else:
                print(f"✅ PASS: {name}")
                test_results.append((name, True, None))

        return wrapper

    return decorator


@register_test("Import core modules")
def test_imports():
    """Test that all core modules can be imported"""
    from model import CFBModel
    from preprocessor import CFBPreprocessor
    from data_fetcher import CFBDataFetcher
    import config
    assert CFBModel is not None
    assert CFBPreprocessor is not None
    assert CFBDataFetcher is not None
    assert config.MODEL_TYPE is not None


@register_test("Initialize CFBModel")
def test_model_init():
    """Test model initialization"""
    from model import CFBModel
    model = CFBModel(model_type="random_forest")
    assert model.model_type == "random_forest"
    assert model.model is not None


@register_test("Initialize CFBPreprocessor")
def test_preprocessor_init():
    """Test preprocessor initialization"""
    from preprocessor import CFBPreprocessor
    preprocessor = CFBPreprocessor()
    assert preprocessor is not None


@register_test("Initialize CFBDataFetcher")
def test_data_fetcher_init():
    """Test data fetcher initialization with dummy key"""
    from data_fetcher import CFBDataFetcher
    fetcher = CFBDataFetcher(api_key="test_key_123")
    assert fetcher.api_key == "test_key_123"


@register_test("Train model with synthetic data")
def test_model_training():
    """Test model training with synthetic data"""
    from model import CFBModel
    
    # Create synthetic training data
    np.random.seed(42)
    n_samples = 200
    X = pd.DataFrame({
        'home_off_total_yards': np.random.randint(250, 500, n_samples),
        'away_off_total_yards': np.random.randint(250, 500, n_samples),
        'home_off_passing_yards': np.random.randint(150, 350, n_samples),
        'away_off_passing_yards': np.random.randint(150, 350, n_samples),
        'home_off_rushing_yards': np.random.randint(100, 250, n_samples),
        'away_off_rushing_yards': np.random.randint(100, 250, n_samples),
        'home_talent': np.random.uniform(50, 95, n_samples),
        'away_talent': np.random.uniform(50, 95, n_samples),
    })
    
    # Create target based on total yards (home wins if home > away)
    y = pd.Series((X['home_off_total_yards'] > X['away_off_total_yards']).astype(int))
    
    model = CFBModel(model_type="random_forest")
    metrics = model.train(X, y, test_size=0.3)
    
    assert 'train_accuracy' in metrics
    assert 'test_accuracy' in metrics
    assert 'cv_mean' in metrics
    assert 0 <= metrics['test_accuracy'] <= 1
    assert metrics['train_accuracy'] > 0.5  # Should do better than random


@register_test("Make predictions")
def test_predictions():
    """Test model predictions"""
    from model import CFBModel
    
    # Train a simple model
    np.random.seed(42)
    n_samples = 100
    X = pd.DataFrame({
        'home_off_total_yards': np.random.randint(250, 500, n_samples),
        'away_off_total_yards': np.random.randint(250, 500, n_samples),
    })
    y = pd.Series((X['home_off_total_yards'] > X['away_off_total_yards']).astype(int))
    
    model = CFBModel(model_type="random_forest")
    model.train(X, y)
    
    # Make predictions
    predictions = model.predict(X)
    probabilities = model.predict_proba(X)
    
    assert len(predictions) == len(X)
    assert all(p in [0, 1] for p in predictions)
    assert probabilities.shape == (len(X), 2)
    assert all(0 <= p <= 1 for row in probabilities for p in row)


@register_test("Save and load model")
def test_save_load():
    """Test saving and loading model"""
    from model import CFBModel
    import tempfile
    
    # Train a simple model
    np.random.seed(42)
    X = pd.DataFrame({
        'feature1': np.random.rand(50),
        'feature2': np.random.rand(50),
    })
    y = pd.Series(np.random.randint(0, 2, 50))
    
    model = CFBModel(model_type="random_forest")
    model.train(X, y)
    
    # Save model
    with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as tmp:
        tmp_path = tmp.name
    
    try:
        model.save(tmp_path)
        assert os.path.exists(tmp_path)
        
        # Load model
        model2 = CFBModel()
        model2.load(tmp_path)
        
        # Verify predictions match
        pred1 = model.predict(X)
        pred2 = model2.predict(X)
        assert all(pred1 == pred2)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@register_test("Preprocessor feature preparation")
def test_feature_prep():
    """Test feature preparation"""
    from preprocessor import CFBPreprocessor
    
    # Create sample games data
    games_df = pd.DataFrame({
        'id': [1, 2],
        'homeTeam': ['Team A', 'Team C'],
        'awayTeam': ['Team B', 'Team D'],
        'homePoints': [35, 28],
        'awayPoints': [21, 31],
    })
    
    # Create sample stats data (in long format as API returns)
    stats_df = pd.DataFrame({
        'team': ['Team A', 'Team A', 'Team A', 'Team B', 'Team B', 'Team B',
                 'Team C', 'Team C', 'Team C', 'Team D', 'Team D', 'Team D'],
        'statName': ['totalYards', 'passingYards', 'rushingYards'] * 4,
        'statValue': [450, 300, 150, 380, 250, 130, 420, 280, 140, 400, 270, 130],
    })
    
    preprocessor = CFBPreprocessor()
    features = preprocessor.prepare_game_features(games_df, stats_df)
    
    assert features is not None
    assert len(features) > 0
    assert 'home_team' in features.columns or 'homeTeam' in features.columns


@register_test("Preprocessor training data creation")
def test_training_data_creation():
    """Test creating training data from features"""
    from preprocessor import CFBPreprocessor
    
    # Create sample feature data
    features_df = pd.DataFrame({
        'home_off_total_yards': [450, 420],
        'away_off_total_yards': [380, 400],
        'home_off_passing_yards': [300, 280],
        'away_off_passing_yards': [250, 270],
        'home_points': [35, 28],
        'away_points': [21, 31],
    })
    
    preprocessor = CFBPreprocessor()
    X, y = preprocessor.create_training_data(features_df)
    
    assert len(X) == 2
    assert len(y) == 2
    assert all(label in [0, 1] for label in y)


@register_test("Main script is executable")
def test_main_executable():
    """Test that main.py has executable permissions"""
    main_path = Path(__file__).parent / "main.py"
    assert main_path.exists()
    assert os.access(main_path, os.X_OK)


@register_test("Command-line interface works")
def test_cli():
    """Test command-line interface"""
    import subprocess
    
    # Test help command
    result = subprocess.run(
        ['python', 'main.py', '--help'],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent
    )
    
    assert result.returncode == 0
    assert 'College Football Prediction Model' in result.stdout
    assert '--api-key' in result.stdout
    assert '--year' in result.stdout


def print_summary():
    """Print test summary"""
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result, _ in test_results if result)
    total = len(test_results)
    
    print(f"\nTotal Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {passed/total*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! The CFB model is FULLY FUNCTIONAL!")
    else:
        print("\n⚠️  Some tests failed. See details above.")
    
    print("\n" + "="*70)
    return passed == total


def main():
    """Run all tests"""
    print("="*70)
    print("CFB MODEL FUNCTIONALITY TEST")
    print("="*70)
    print("\nTesting core functionality without API access...")
    print()
    
    # Run all tests
    test_imports()
    test_model_init()
    test_preprocessor_init()
    test_data_fetcher_init()
    test_model_training()
    test_predictions()
    test_save_load()
    test_feature_prep()
    test_training_data_creation()
    test_main_executable()
    test_cli()
    
    # Print summary
    all_passed = print_summary()
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
