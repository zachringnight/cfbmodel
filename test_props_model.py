"""
Tests for CFB Props Model

Run with: python -m pytest test_props_model.py -v
"""

import pytest
import numpy as np
import pandas as pd
import os
import tempfile

from props_model import CFBPropsModel, format_actionable_output
from props_preprocessor import CFBPropsPreprocessor, prepare_training_pipeline


class TestCFBPropsModel:
    """Tests for the CFBPropsModel class"""

    @pytest.fixture
    def sample_training_data(self):
        """Create sample training data"""
        np.random.seed(42)
        n_samples = 200

        X = pd.DataFrame({
            'home_rolling_pts_scored': np.random.uniform(20, 40, n_samples),
            'home_rolling_pts_allowed': np.random.uniform(15, 35, n_samples),
            'home_rolling_margin': np.random.uniform(-10, 15, n_samples),
            'home_rolling_win_pct': np.random.uniform(0.3, 0.8, n_samples),
            'home_games_played': np.random.randint(3, 10, n_samples),
            'away_rolling_pts_scored': np.random.uniform(20, 40, n_samples),
            'away_rolling_pts_allowed': np.random.uniform(15, 35, n_samples),
            'away_rolling_margin': np.random.uniform(-10, 15, n_samples),
            'away_rolling_win_pct': np.random.uniform(0.3, 0.8, n_samples),
            'away_games_played': np.random.randint(3, 10, n_samples),
            'home_elo': np.random.uniform(1300, 1700, n_samples),
            'away_elo': np.random.uniform(1300, 1700, n_samples),
            'elo_diff': np.random.uniform(-300, 300, n_samples),
            'neutral_site': np.random.choice([0, 1], n_samples, p=[0.9, 0.1]),
            'conference_game': np.random.choice([0, 1], n_samples, p=[0.4, 0.6]),
        })

        # Generate realistic target values based on features
        y_home = (
            X['home_rolling_pts_scored'] * 0.6 +
            X['away_rolling_pts_allowed'] * 0.3 +
            X['elo_diff'] * 0.01 +
            np.random.normal(0, 5, n_samples)
        ).clip(0, 70)

        y_away = (
            X['away_rolling_pts_scored'] * 0.6 +
            X['home_rolling_pts_allowed'] * 0.3 -
            X['elo_diff'] * 0.01 +
            np.random.normal(0, 5, n_samples)
        ).clip(0, 70)

        return X, pd.Series(y_home), pd.Series(y_away)

    def test_model_initialization_random_forest(self):
        """Test model initializes with random forest"""
        model = CFBPropsModel(model_type="random_forest")
        assert model.model_type == "random_forest"
        assert model.is_trained is False

    def test_model_initialization_gradient_boosting(self):
        """Test model initializes with gradient boosting"""
        model = CFBPropsModel(model_type="gradient_boosting")
        assert model.model_type == "gradient_boosting"

    def test_model_initialization_invalid_type(self):
        """Test model raises error for invalid type"""
        with pytest.raises(ValueError):
            CFBPropsModel(model_type="invalid_model")

    def test_model_training(self, sample_training_data):
        """Test model training works correctly"""
        X, y_home, y_away = sample_training_data
        model = CFBPropsModel()

        metrics = model.train(X, y_home, y_away)

        assert model.is_trained is True
        assert 'home_points' in metrics
        assert 'away_points' in metrics
        assert 'game_total' in metrics
        assert 'spread' in metrics

        # Check metrics exist for each prop type
        for prop_type in ['home_points', 'away_points', 'game_total', 'spread']:
            assert 'test_mae' in metrics[prop_type]
            assert 'test_rmse' in metrics[prop_type]
            assert 'test_r2' in metrics[prop_type]

    def test_model_training_empty_data(self):
        """Test model raises error for empty data"""
        model = CFBPropsModel()

        with pytest.raises(ValueError):
            model.train(pd.DataFrame(), pd.Series([]), pd.Series([]))

    def test_model_training_mismatched_lengths(self, sample_training_data):
        """Test model raises error for mismatched data lengths"""
        X, y_home, y_away = sample_training_data
        model = CFBPropsModel()

        with pytest.raises(ValueError):
            model.train(X, y_home[:50], y_away)

    def test_model_prediction(self, sample_training_data):
        """Test model prediction works"""
        X, y_home, y_away = sample_training_data
        model = CFBPropsModel()
        model.train(X, y_home, y_away)

        predictions = model.predict(X[:10])

        assert 'home_points' in predictions
        assert 'away_points' in predictions
        assert 'game_total' in predictions
        assert 'spread' in predictions
        assert len(predictions['home_points']) == 10

    def test_model_prediction_untrained(self, sample_training_data):
        """Test untrained model raises error on prediction"""
        X, _, _ = sample_training_data
        model = CFBPropsModel()

        with pytest.raises(ValueError):
            model.predict(X)

    def test_model_predict_with_confidence(self, sample_training_data):
        """Test prediction with confidence intervals"""
        X, y_home, y_away = sample_training_data
        model = CFBPropsModel()
        model.train(X, y_home, y_away)

        results = model.predict_with_confidence(X[:10])

        for prop_type in ['home_points', 'away_points']:
            assert 'prediction' in results[prop_type]
            assert 'lower' in results[prop_type]
            assert 'upper' in results[prop_type]
            # Lower should be <= prediction <= upper
            assert all(results[prop_type]['lower'] <= results[prop_type]['prediction'])
            assert all(results[prop_type]['prediction'] <= results[prop_type]['upper'])

    def test_model_save_load(self, sample_training_data):
        """Test model save and load"""
        X, y_home, y_away = sample_training_data
        model = CFBPropsModel()
        model.train(X, y_home, y_away)

        # Save
        with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as f:
            filepath = f.name

        try:
            model.save(filepath)
            assert os.path.exists(filepath)

            # Load into new model
            model2 = CFBPropsModel()
            model2.load(filepath)

            assert model2.is_trained is True
            assert model2.model_type == model.model_type

            # Check predictions are same
            pred1 = model.predict(X[:5])
            pred2 = model2.predict(X[:5])

            np.testing.assert_array_almost_equal(
                pred1['home_points'],
                pred2['home_points']
            )
        finally:
            os.unlink(filepath)

    def test_get_actionable_props(self, sample_training_data):
        """Test actionable props recommendations"""
        X, y_home, y_away = sample_training_data
        model = CFBPropsModel()
        model.train(X, y_home, y_away)

        # Create fake betting lines
        betting_lines = pd.DataFrame({
            'home_team': [f'Team{i}' for i in range(10)],
            'away_team': [f'Opponent{i}' for i in range(10)],
            'spread': np.random.uniform(-14, 14, 10),
            'over_under': np.random.uniform(40, 60, 10)
        })

        recommendations = model.get_actionable_props(
            X[:10],
            betting_lines,
            min_edge=2.0
        )

        assert len(recommendations) == 10
        assert 'spread_rec' in recommendations.columns
        assert 'total_rec' in recommendations.columns
        assert 'pred_home_pts' in recommendations.columns
        assert 'pred_away_pts' in recommendations.columns


class TestCFBPropsPreprocessor:
    """Tests for the CFBPropsPreprocessor class"""

    @pytest.fixture
    def sample_games_df(self):
        """Create sample games DataFrame"""
        np.random.seed(42)
        n_games = 100

        dates = pd.date_range('2023-09-01', periods=n_games, freq='7D')
        teams = ['Alabama', 'Georgia', 'Ohio State', 'Michigan', 'Texas', 'Oregon']

        games = []
        for i in range(n_games):
            home = np.random.choice(teams)
            away = np.random.choice([t for t in teams if t != home])
            games.append({
                'id': i,
                'start_date': dates[i % len(dates)],
                'season': 2023,
                'week': (i % 14) + 1,
                'home_team': home,
                'away_team': away,
                'home_points': np.random.randint(10, 50),
                'away_points': np.random.randint(10, 50),
                'neutral_site': False,
                'conference_game': np.random.choice([True, False]),
                'status': 'completed',
                'home_start_elo': np.random.uniform(1400, 1700),
                'away_start_elo': np.random.uniform(1400, 1700)
            })

        return pd.DataFrame(games)

    def test_preprocessor_initialization(self):
        """Test preprocessor initializes correctly"""
        preprocessor = CFBPropsPreprocessor(lookback_games=5)
        assert preprocessor.lookback_games == 5

    def test_calculate_team_rolling_stats(self, sample_games_df):
        """Test rolling stats calculation"""
        preprocessor = CFBPropsPreprocessor(lookback_games=3)
        team_stats = preprocessor.calculate_team_rolling_stats(sample_games_df)

        assert len(team_stats) > 0
        for team, stats in team_stats.items():
            assert 'rolling_pts_scored' in stats.columns
            assert 'rolling_pts_allowed' in stats.columns
            assert 'rolling_margin' in stats.columns

    def test_prepare_props_features(self, sample_games_df):
        """Test feature preparation"""
        preprocessor = CFBPropsPreprocessor()
        features = preprocessor.prepare_props_features(sample_games_df)

        assert len(features) == len(sample_games_df)
        assert 'home_rolling_pts_scored' in features.columns
        assert 'away_rolling_pts_scored' in features.columns
        assert 'elo_diff' in features.columns
        assert 'expected_total' in features.columns

    def test_create_training_data(self, sample_games_df):
        """Test training data creation"""
        preprocessor = CFBPropsPreprocessor()
        features = preprocessor.prepare_props_features(sample_games_df)
        X, y_home, y_away = preprocessor.create_training_data(features)

        assert len(X) == len(y_home) == len(y_away)
        assert not X.empty
        assert 'home_rolling_pts_scored' in X.columns

    def test_process_betting_lines(self):
        """Test betting lines processing"""
        preprocessor = CFBPropsPreprocessor()

        # Simulate API response format
        lines_df = pd.DataFrame([
            {
                'id': 1,
                'homeTeam': 'Alabama',
                'awayTeam': 'Georgia',
                'week': 10,
                'lines': [
                    {'provider': 'consensus', 'spread': -3.5, 'overUnder': 52.5},
                    {'provider': 'Bovada', 'spread': -3.0, 'overUnder': 53.0}
                ]
            },
            {
                'id': 2,
                'homeTeam': 'Ohio State',
                'awayTeam': 'Michigan',
                'week': 10,
                'lines': [
                    {'provider': 'consensus', 'spread': 7.0, 'overUnder': 45.5}
                ]
            }
        ])

        processed = preprocessor.process_betting_lines(lines_df)

        assert len(processed) == 2
        assert processed.iloc[0]['spread'] == -3.5  # Consensus line
        assert processed.iloc[0]['over_under'] == 52.5


class TestFormatActionableOutput:
    """Tests for the output formatting function"""

    def test_format_output(self):
        """Test report formatting"""
        recommendations = pd.DataFrame([
            {
                'home_team': 'Alabama',
                'away_team': 'Georgia',
                'book_spread': -3.5,
                'pred_spread': -7.0,
                'spread_edge': -3.5,
                'spread_range': '[-10.0, -4.0]',
                'spread_rec': 'TAKE AWAY',
                'spread_reasoning': 'Model predicts away -3.5 vs line',
                'book_total': 52.5,
                'pred_total': 48.0,
                'total_edge': -4.5,
                'total_range': '[42.0, 54.0]',
                'total_rec': 'UNDER',
                'total_reasoning': 'Model predicts 4.5 pts below line',
                'pred_home_pts': 20.5,
                'pred_away_pts': 27.5
            }
        ])

        output = format_actionable_output(recommendations)

        assert 'COLLEGE FOOTBALL PROPS' in output
        assert 'Alabama' in output
        assert 'Georgia' in output
        assert 'TAKE AWAY' in output
        assert 'UNDER' in output


class TestIntegration:
    """Integration tests for full pipeline"""

    def test_full_pipeline_synthetic(self):
        """Test full pipeline with synthetic data"""
        np.random.seed(42)

        # Create synthetic games
        n_games = 150
        teams = ['Team_A', 'Team_B', 'Team_C', 'Team_D', 'Team_E']
        dates = pd.date_range('2023-09-01', periods=n_games, freq='3D')

        games = []
        for i in range(n_games):
            home = teams[i % len(teams)]
            away = teams[(i + 1) % len(teams)]
            games.append({
                'id': i,
                'start_date': dates[i],
                'season': 2023,
                'week': (i // 10) + 1,
                'home_team': home,
                'away_team': away,
                'home_points': np.random.randint(14, 45),
                'away_points': np.random.randint(14, 45),
                'neutral_site': False,
                'conference_game': True,
                'status': 'completed',
                'home_start_elo': 1500 + np.random.randint(-100, 100),
                'away_start_elo': 1500 + np.random.randint(-100, 100)
            })

        games_df = pd.DataFrame(games)

        # Run preprocessing
        preprocessor = CFBPropsPreprocessor(lookback_games=3)
        features_df = preprocessor.prepare_props_features(games_df)
        X, y_home, y_away = preprocessor.create_training_data(features_df)

        # Train model
        model = CFBPropsModel(model_type="random_forest")
        metrics = model.train(X, y_home, y_away, test_size=0.2)

        # Verify reasonable performance
        assert metrics['home_points']['test_mae'] < 15  # MAE under 15 points
        assert metrics['game_total']['test_mae'] < 20  # Total MAE under 20

        # Make predictions on last few games
        predictions = model.predict(X[-5:])
        assert len(predictions['home_points']) == 5

        # Test with confidence
        conf_pred = model.predict_with_confidence(X[-5:])
        assert 'lower' in conf_pred['home_points']
        assert 'upper' in conf_pred['home_points']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
