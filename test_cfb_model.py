"""
Basic tests for CFB Model
Run with: python -m pytest test_cfb_model.py
"""

import pytest
import pandas as pd
import numpy as np
from model import CFBModel
from preprocessor import CFBPreprocessor


class TestCFBModel:
    """Test cases for CFB Model"""
    
    def test_model_initialization(self):
        """Test model can be initialized"""
        model = CFBModel(model_type="random_forest")
        assert model.model_type == "random_forest"
        assert model.model is not None
    
    def test_invalid_model_type(self):
        """Test that invalid model type raises error"""
        with pytest.raises(ValueError):
            CFBModel(model_type="invalid_model")
    
    def test_model_train_with_valid_data(self):
        """Test model training with valid data"""
        # Create sample data
        X = pd.DataFrame({
            'home_off_total_yards': np.random.randint(200, 500, 100),
            'away_off_total_yards': np.random.randint(200, 500, 100),
            'home_talent': np.random.uniform(0, 100, 100),
            'away_talent': np.random.uniform(0, 100, 100),
        })
        y = pd.Series(np.random.randint(0, 2, 100))
        
        model = CFBModel()
        metrics = model.train(X, y, test_size=0.3)
        
        assert 'train_accuracy' in metrics
        assert 'test_accuracy' in metrics
        assert 'cv_mean' in metrics
        assert 0 <= metrics['test_accuracy'] <= 1
    
    def test_model_train_with_empty_data(self):
        """Test that training with empty data raises error"""
        X = pd.DataFrame()
        y = pd.Series()
        
        model = CFBModel()
        with pytest.raises(ValueError):
            model.train(X, y)
    
    def test_model_train_with_mismatched_data(self):
        """Test that training with mismatched X and y raises error"""
        X = pd.DataFrame({'feature': [1, 2, 3]})
        y = pd.Series([0, 1])  # Different length
        
        model = CFBModel()
        with pytest.raises(ValueError):
            model.train(X, y)
    
    def test_model_prediction(self):
        """Test model can make predictions"""
        X = pd.DataFrame({
            'home_off_total_yards': np.random.randint(200, 500, 50),
            'away_off_total_yards': np.random.randint(200, 500, 50),
        })
        y = pd.Series(np.random.randint(0, 2, 50))
        
        model = CFBModel()
        model.train(X, y)
        
        predictions = model.predict(X)
        assert len(predictions) == len(X)
        assert all(p in [0, 1] for p in predictions)
    
    def test_model_prediction_probabilities(self):
        """Test model can return prediction probabilities"""
        X = pd.DataFrame({
            'home_off_total_yards': np.random.randint(200, 500, 50),
            'away_off_total_yards': np.random.randint(200, 500, 50),
        })
        y = pd.Series(np.random.randint(0, 2, 50))
        
        model = CFBModel()
        model.train(X, y)
        
        probabilities = model.predict_proba(X)
        assert probabilities.shape == (len(X), 2)
        assert all(0 <= p <= 1 for row in probabilities for p in row)


class TestCFBPreprocessor:
    """Test cases for CFB Preprocessor"""
    
    def test_preprocessor_initialization(self):
        """Test preprocessor can be initialized"""
        preprocessor = CFBPreprocessor()
        assert preprocessor is not None
    
    def test_prepare_features_with_empty_games(self):
        """Test that empty games dataframe raises error"""
        preprocessor = CFBPreprocessor()
        games_df = pd.DataFrame()
        stats_df = pd.DataFrame({'team': ['Team A'], 'statName': ['totalYards'], 'statValue': [400]})
        
        with pytest.raises(ValueError):
            preprocessor.prepare_game_features(games_df, stats_df)
    
    def test_prepare_features_with_empty_stats(self):
        """Test that empty stats dataframe raises error"""
        preprocessor = CFBPreprocessor()
        games_df = pd.DataFrame({'homeTeam': ['Team A'], 'awayTeam': ['Team B']})
        stats_df = pd.DataFrame()
        
        with pytest.raises(ValueError):
            preprocessor.prepare_game_features(games_df, stats_df)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
