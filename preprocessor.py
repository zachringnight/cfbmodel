"""
Data preprocessing and feature engineering for CFB model
"""

import pandas as pd
import numpy as np
import logging
from typing import Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CFBPreprocessor:
    """Preprocessor for college football data"""
    
    def __init__(self):
        self.team_stats_cache = {}
    
    def prepare_game_features(self, games_df: pd.DataFrame, 
                              team_stats_df: pd.DataFrame,
                              talent_df: pd.DataFrame = None) -> pd.DataFrame:
        """
        Prepare features for game prediction
        
        Args:
            games_df: DataFrame with game information
            team_stats_df: DataFrame with team statistics
            talent_df: DataFrame with team talent ratings (optional)
            
        Returns:
            DataFrame with engineered features for modeling
            
        Raises:
            ValueError: If invalid input data is provided
        """
        if games_df.empty:
            raise ValueError("games_df cannot be empty")
        if team_stats_df.empty:
            raise ValueError("team_stats_df cannot be empty")
        
        logger.info(f"Preparing features for {len(games_df)} games")
        
        # Create a copy to avoid modifying original
        features = games_df.copy()
        
        # Convert team stats to dict for easy lookup
        # Stats come in long format (statName, statValue), need to pivot
        stats_dict = {}
        if 'statName' in team_stats_df.columns and 'statValue' in team_stats_df.columns:
            # Pivot the stats data
            logger.info("Pivoting team statistics from long to wide format")
            for team_name in team_stats_df['team'].unique():
                team_data = team_stats_df[team_stats_df['team'] == team_name]
                stats_dict[team_name] = dict(zip(team_data['statName'], team_data['statValue']))
            logger.info(f"Processed stats for {len(stats_dict)} teams")
        else:
            # Legacy format - stats are already in wide format
            logger.info("Processing team statistics in wide format")
            for _, row in team_stats_df.iterrows():
                team = row.get('team', row.get('school', ''))
                if team:
                    stats_dict[team] = row.to_dict()
        
        # Create talent lookup if available
        talent_dict = {}
        if talent_df is not None and not talent_df.empty:
            logger.info(f"Processing talent ratings for {len(talent_df)} teams")
            for _, row in talent_df.iterrows():
                team = row.get('school', '')
                if team:
                    talent_dict[team] = row.get('talent', 0)
        else:
            logger.info("No talent ratings provided")
        
        # Add features for home and away teams
        home_features = []
        away_features = []
        
        for _, game in features.iterrows():
            # Handle both snake_case and camelCase column names
            home_team = game.get('homeTeam', game.get('home_team', ''))
            away_team = game.get('awayTeam', game.get('away_team', ''))
            
            # Get stats for home team
            home_stats = stats_dict.get(home_team, {})
            away_stats = stats_dict.get(away_team, {})
            
            # Extract key statistics
            home_dict = {
                'home_off_total_yards': home_stats.get('totalYards', 0),
                'home_off_passing_yards': home_stats.get('netPassingYards', 0),
                'home_off_rushing_yards': home_stats.get('rushingYards', 0),
                'home_off_points': home_stats.get('points', 0),  # Will be 0 as points not in stats
                'home_talent': talent_dict.get(home_team, 0)
            }
            
            away_dict = {
                'away_off_total_yards': away_stats.get('totalYards', 0),
                'away_off_passing_yards': away_stats.get('netPassingYards', 0),
                'away_off_rushing_yards': away_stats.get('rushingYards', 0),
                'away_off_points': away_stats.get('points', 0),  # Will be 0 as points not in stats
                'away_talent': talent_dict.get(away_team, 0)
            }
            
            home_features.append(home_dict)
            away_features.append(away_dict)
        
        # Add features to dataframe
        for key in home_features[0].keys():
            features[key] = [f[key] for f in home_features]
        
        for key in away_features[0].keys():
            features[key] = [f[key] for f in away_features]
        
        # Calculate differential features
        features['talent_diff'] = features['home_talent'] - features['away_talent']
        features['yards_diff'] = features['home_off_total_yards'] - features['away_off_total_yards']
        features['points_diff'] = features['home_off_points'] - features['away_off_points']
        
        return features
    
    def create_training_data(self, features_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Create training data from features DataFrame
        
        Args:
            features_df: DataFrame with game features
            
        Returns:
            Tuple of (X, y) where X is features and y is target
        """
        # Select feature columns
        feature_cols = [
            'home_off_total_yards', 'home_off_passing_yards', 'home_off_rushing_yards',
            'home_off_points', 'home_talent',
            'away_off_total_yards', 'away_off_passing_yards', 'away_off_rushing_yards',
            'away_off_points', 'away_talent',
            'talent_diff', 'yards_diff', 'points_diff'
        ]
        
        # Filter to only include columns that exist
        available_cols = [col for col in feature_cols if col in features_df.columns]
        
        X = features_df[available_cols].fillna(0)
        
        # Create target variable (home team win = 1, loss = 0)
        # Handle both snake_case and camelCase column names
        home_points_col = 'homePoints' if 'homePoints' in features_df.columns else 'home_points'
        away_points_col = 'awayPoints' if 'awayPoints' in features_df.columns else 'away_points'
        
        if home_points_col in features_df.columns and away_points_col in features_df.columns:
            y = (features_df[home_points_col] > features_df[away_points_col]).astype(int)
        else:
            y = pd.Series([0] * len(features_df))
        
        return X, y
