"""
Data preprocessing and feature engineering for CFB Props model

Creates features optimized for predicting:
- Team points
- Game totals
- Spreads/margins
"""

import pandas as pd
import numpy as np
import logging
from typing import Tuple, Optional, Dict, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CFBPropsPreprocessor:
    """Preprocessor for college football props predictions"""

    def __init__(self, lookback_games: int = 5):
        """
        Initialize the props preprocessor

        Args:
            lookback_games: Number of recent games to use for rolling averages
        """
        self.lookback_games = lookback_games
        self.team_stats_cache: Dict[str, pd.DataFrame] = {}

    def load_games_data(self, filepath: str) -> pd.DataFrame:
        """
        Load historical games data from CSV

        Args:
            filepath: Path to games.csv file

        Returns:
            DataFrame with processed game data
        """
        logger.info(f"Loading games data from {filepath}")
        df = pd.read_csv(filepath)

        # Filter to completed games with valid scores
        df = df[df['status'] == 'completed']
        df = df[df['home_points'].notna() & df['away_points'].notna()]

        # Convert points to numeric
        df['home_points'] = pd.to_numeric(df['home_points'], errors='coerce')
        df['away_points'] = pd.to_numeric(df['away_points'], errors='coerce')

        # Parse date
        df['start_date'] = pd.to_datetime(df['start_date'])

        # Sort by date for proper rolling calculations
        df = df.sort_values('start_date').reset_index(drop=True)

        logger.info(f"Loaded {len(df)} completed games")
        return df

    def calculate_team_rolling_stats(self, games_df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """
        Calculate rolling statistics for each team

        Args:
            games_df: DataFrame with game data

        Returns:
            Dictionary mapping team names to their rolling stats
        """
        logger.info("Calculating team rolling statistics...")

        # Get all unique teams
        home_teams = games_df['home_team'].unique()
        away_teams = games_df['away_team'].unique()
        all_teams = set(home_teams) | set(away_teams)

        team_stats = {}

        for team in all_teams:
            # Get all games for this team (home or away)
            home_games = games_df[games_df['home_team'] == team].copy()
            home_games['team_points'] = home_games['home_points']
            home_games['opp_points'] = home_games['away_points']
            home_games['is_home'] = 1

            away_games = games_df[games_df['away_team'] == team].copy()
            away_games['team_points'] = away_games['away_points']
            away_games['opp_points'] = away_games['home_points']
            away_games['is_home'] = 0

            # Combine and sort
            team_games = pd.concat([home_games, away_games]).sort_values('start_date')

            if len(team_games) > 0:
                # Calculate rolling averages (shifted to avoid data leakage)
                team_games['rolling_pts_scored'] = (
                    team_games['team_points']
                    .rolling(window=self.lookback_games, min_periods=1)
                    .mean()
                    .shift(1)
                )
                team_games['rolling_pts_allowed'] = (
                    team_games['opp_points']
                    .rolling(window=self.lookback_games, min_periods=1)
                    .mean()
                    .shift(1)
                )
                team_games['rolling_margin'] = (
                    (team_games['team_points'] - team_games['opp_points'])
                    .rolling(window=self.lookback_games, min_periods=1)
                    .mean()
                    .shift(1)
                )
                team_games['games_played'] = range(len(team_games))

                # Win rate
                team_games['win'] = (team_games['team_points'] > team_games['opp_points']).astype(int)
                team_games['rolling_win_pct'] = (
                    team_games['win']
                    .rolling(window=self.lookback_games, min_periods=1)
                    .mean()
                    .shift(1)
                )

                team_stats[team] = team_games

        logger.info(f"Calculated rolling stats for {len(team_stats)} teams")
        return team_stats

    def prepare_props_features(self, games_df: pd.DataFrame,
                                team_stats: Optional[Dict[str, pd.DataFrame]] = None,
                                include_elo: bool = True) -> pd.DataFrame:
        """
        Prepare features for props prediction

        Args:
            games_df: DataFrame with game data
            team_stats: Pre-calculated team rolling stats (optional)
            include_elo: Whether to include ELO ratings if available

        Returns:
            DataFrame with features ready for modeling
        """
        logger.info(f"Preparing props features for {len(games_df)} games")

        # Calculate team stats if not provided
        if team_stats is None:
            team_stats = self.calculate_team_rolling_stats(games_df)

        features = []

        for _, game in games_df.iterrows():
            home_team = game['home_team']
            away_team = game['away_team']
            game_date = game['start_date']

            feature_dict = {
                'game_id': game.get('id', None),
                'season': game.get('season', None),
                'week': game.get('week', None),
                'start_date': game_date,
                'home_team': home_team,
                'away_team': away_team,
                'neutral_site': 1 if game.get('neutral_site', False) else 0,
                'conference_game': 1 if game.get('conference_game', False) else 0,
            }

            # Get home team rolling stats
            if home_team in team_stats:
                home_df = team_stats[home_team]
                # Find the stats just before this game
                prior_stats = home_df[home_df['start_date'] < game_date]
                if len(prior_stats) > 0:
                    latest = prior_stats.iloc[-1]
                    feature_dict['home_rolling_pts_scored'] = latest.get('rolling_pts_scored', 25)
                    feature_dict['home_rolling_pts_allowed'] = latest.get('rolling_pts_allowed', 25)
                    feature_dict['home_rolling_margin'] = latest.get('rolling_margin', 0)
                    feature_dict['home_rolling_win_pct'] = latest.get('rolling_win_pct', 0.5)
                    feature_dict['home_games_played'] = latest.get('games_played', 0)
                else:
                    # No prior games - use defaults
                    feature_dict['home_rolling_pts_scored'] = 25
                    feature_dict['home_rolling_pts_allowed'] = 25
                    feature_dict['home_rolling_margin'] = 0
                    feature_dict['home_rolling_win_pct'] = 0.5
                    feature_dict['home_games_played'] = 0
            else:
                feature_dict['home_rolling_pts_scored'] = 25
                feature_dict['home_rolling_pts_allowed'] = 25
                feature_dict['home_rolling_margin'] = 0
                feature_dict['home_rolling_win_pct'] = 0.5
                feature_dict['home_games_played'] = 0

            # Get away team rolling stats
            if away_team in team_stats:
                away_df = team_stats[away_team]
                prior_stats = away_df[away_df['start_date'] < game_date]
                if len(prior_stats) > 0:
                    latest = prior_stats.iloc[-1]
                    feature_dict['away_rolling_pts_scored'] = latest.get('rolling_pts_scored', 25)
                    feature_dict['away_rolling_pts_allowed'] = latest.get('rolling_pts_allowed', 25)
                    feature_dict['away_rolling_margin'] = latest.get('rolling_margin', 0)
                    feature_dict['away_rolling_win_pct'] = latest.get('rolling_win_pct', 0.5)
                    feature_dict['away_games_played'] = latest.get('games_played', 0)
                else:
                    feature_dict['away_rolling_pts_scored'] = 25
                    feature_dict['away_rolling_pts_allowed'] = 25
                    feature_dict['away_rolling_margin'] = 0
                    feature_dict['away_rolling_win_pct'] = 0.5
                    feature_dict['away_games_played'] = 0
            else:
                feature_dict['away_rolling_pts_scored'] = 25
                feature_dict['away_rolling_pts_allowed'] = 25
                feature_dict['away_rolling_margin'] = 0
                feature_dict['away_rolling_win_pct'] = 0.5
                feature_dict['away_games_played'] = 0

            # Add ELO ratings if available
            if include_elo:
                feature_dict['home_elo'] = game.get('home_start_elo', 1500)
                feature_dict['away_elo'] = game.get('away_start_elo', 1500)
                if pd.isna(feature_dict['home_elo']):
                    feature_dict['home_elo'] = 1500
                if pd.isna(feature_dict['away_elo']):
                    feature_dict['away_elo'] = 1500

            # Add actual outcomes (for training)
            feature_dict['home_points'] = game.get('home_points', None)
            feature_dict['away_points'] = game.get('away_points', None)

            features.append(feature_dict)

        features_df = pd.DataFrame(features)

        # Calculate derived features
        features_df['elo_diff'] = features_df['home_elo'] - features_df['away_elo']
        features_df['margin_diff'] = features_df['home_rolling_margin'] - features_df['away_rolling_margin']
        features_df['pts_scored_diff'] = features_df['home_rolling_pts_scored'] - features_df['away_rolling_pts_scored']
        features_df['pts_allowed_diff'] = features_df['home_rolling_pts_allowed'] - features_df['away_rolling_pts_allowed']
        features_df['win_pct_diff'] = features_df['home_rolling_win_pct'] - features_df['away_rolling_win_pct']

        # Expected total (simple average of scoring + allowed)
        features_df['expected_total'] = (
            features_df['home_rolling_pts_scored'] + features_df['away_rolling_pts_scored'] +
            features_df['home_rolling_pts_allowed'] + features_df['away_rolling_pts_allowed']
        ) / 2

        logger.info(f"Created {len(features_df)} game feature records with {len(features_df.columns)} features")
        return features_df

    def create_training_data(self, features_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series, pd.Series]:
        """
        Create training data for props models

        Args:
            features_df: DataFrame with game features

        Returns:
            Tuple of (X, y_home, y_away)
        """
        # Define feature columns
        feature_cols = [
            # Rolling stats
            'home_rolling_pts_scored', 'home_rolling_pts_allowed', 'home_rolling_margin',
            'home_rolling_win_pct', 'home_games_played',
            'away_rolling_pts_scored', 'away_rolling_pts_allowed', 'away_rolling_margin',
            'away_rolling_win_pct', 'away_games_played',
            # ELO
            'home_elo', 'away_elo', 'elo_diff',
            # Derived
            'margin_diff', 'pts_scored_diff', 'pts_allowed_diff', 'win_pct_diff',
            'expected_total',
            # Context
            'neutral_site', 'conference_game'
        ]

        # Filter to columns that exist
        available_cols = [col for col in feature_cols if col in features_df.columns]

        # Filter to rows with valid targets
        valid_mask = features_df['home_points'].notna() & features_df['away_points'].notna()
        valid_df = features_df[valid_mask].copy()

        X = valid_df[available_cols].fillna(0)
        y_home = valid_df['home_points']
        y_away = valid_df['away_points']

        logger.info(f"Created training data: X shape={X.shape}, samples={len(y_home)}")
        return X, y_home, y_away

    def process_betting_lines(self, lines_df: pd.DataFrame) -> pd.DataFrame:
        """
        Process betting lines data from API

        Args:
            lines_df: Raw betting lines DataFrame from API

        Returns:
            Processed DataFrame with one row per game
        """
        if lines_df.empty:
            return pd.DataFrame()

        logger.info(f"Processing {len(lines_df)} betting line records")

        # The API returns nested 'lines' field - need to extract
        processed = []

        for _, row in lines_df.iterrows():
            game_data = {
                'game_id': row.get('id', None),
                'home_team': row.get('homeTeam', row.get('home_team', None)),
                'away_team': row.get('awayTeam', row.get('away_team', None)),
                'week': row.get('week', None),
            }

            # Extract lines from nested structure
            lines = row.get('lines', [])
            if isinstance(lines, list) and len(lines) > 0:
                # Use consensus line or first available
                consensus = None
                for line in lines:
                    if isinstance(line, dict):
                        if line.get('provider', '').lower() == 'consensus':
                            consensus = line
                            break

                line_data = consensus if consensus else (lines[0] if isinstance(lines[0], dict) else {})

                game_data['spread'] = line_data.get('spread', None)
                game_data['over_under'] = line_data.get('overUnder', line_data.get('over_under', None))
                game_data['spread_open'] = line_data.get('spreadOpen', None)
                game_data['over_under_open'] = line_data.get('overUnderOpen', None)
                game_data['provider'] = line_data.get('provider', 'unknown')

            processed.append(game_data)

        result = pd.DataFrame(processed)

        # Convert to numeric
        for col in ['spread', 'over_under', 'spread_open', 'over_under_open']:
            if col in result.columns:
                result[col] = pd.to_numeric(result[col], errors='coerce')

        # Filter to games with valid lines
        valid_lines = result[result['spread'].notna() | result['over_under'].notna()]
        logger.info(f"Processed {len(valid_lines)} games with valid betting lines")

        return valid_lines

    def merge_features_with_lines(self, features_df: pd.DataFrame,
                                   lines_df: pd.DataFrame) -> pd.DataFrame:
        """
        Merge feature data with betting lines

        Args:
            features_df: DataFrame with game features
            lines_df: DataFrame with processed betting lines

        Returns:
            Merged DataFrame
        """
        if lines_df.empty:
            logger.warning("No betting lines to merge")
            return features_df

        # Try to merge on game_id first
        if 'game_id' in features_df.columns and 'game_id' in lines_df.columns:
            merged = features_df.merge(
                lines_df[['game_id', 'spread', 'over_under', 'provider']],
                on='game_id',
                how='left'
            )
        else:
            # Merge on team names
            merged = features_df.merge(
                lines_df[['home_team', 'away_team', 'spread', 'over_under', 'provider']],
                on=['home_team', 'away_team'],
                how='left'
            )

        logger.info(f"Merged features with lines: {merged['spread'].notna().sum()} games with spreads")
        return merged


def prepare_training_pipeline(games_filepath: str,
                               min_season: int = 2015) -> Tuple[pd.DataFrame, pd.Series, pd.Series]:
    """
    Full pipeline to prepare training data from games CSV

    Args:
        games_filepath: Path to games.csv
        min_season: Minimum season to include (for recency)

    Returns:
        Tuple of (X, y_home, y_away)
    """
    preprocessor = CFBPropsPreprocessor(lookback_games=5)

    # Load games
    games_df = preprocessor.load_games_data(games_filepath)

    # Filter to recent seasons
    games_df = games_df[games_df['season'] >= min_season]
    logger.info(f"Filtered to {len(games_df)} games from {min_season} onwards")

    # Calculate team stats
    team_stats = preprocessor.calculate_team_rolling_stats(games_df)

    # Prepare features
    features_df = preprocessor.prepare_props_features(games_df, team_stats)

    # Create training data
    X, y_home, y_away = preprocessor.create_training_data(features_df)

    return X, y_home, y_away
