"""
College Football Props Prediction Model

Regression-based models for predicting game props:
- Team points (over/under on team totals)
- Game totals (over/under combined score)
- Spreads (point differential / margin)
"""

import numpy as np
import pandas as pd
import logging
import math
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from typing import Tuple, Dict, Any, Optional, List
import pickle
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CFBPropsModel:
    """Machine learning model for predicting college football game props"""

    # Prop types supported
    PROP_TYPES = ['home_points', 'away_points', 'game_total', 'spread']

    def __init__(self, model_type: str = "random_forest"):
        """
        Initialize the CFB Props model

        Args:
            model_type: Type of model to use ("random_forest" or "gradient_boosting")

        Raises:
            ValueError: If invalid model_type is provided
        """
        if model_type not in ["random_forest", "gradient_boosting"]:
            raise ValueError(f"Unknown model type: {model_type}. Must be 'random_forest' or 'gradient_boosting'")

        self.model_type = model_type
        self.models: Dict[str, Any] = {}  # One model per prop type
        self.is_trained = False

        logger.info(f"CFBPropsModel initialized with model_type={model_type}")

    def _create_model(self):
        """Create a new regression model instance"""
        if self.model_type == "random_forest":
            return RandomForestRegressor(
                n_estimators=100,
                max_depth=12,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            )
        elif self.model_type == "gradient_boosting":
            return GradientBoostingRegressor(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                min_samples_split=5,
                random_state=42
            )
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")

    def train(self, X: pd.DataFrame, y_home: pd.Series, y_away: pd.Series,
              test_size: float = 0.2) -> Dict[str, Any]:
        """
        Train models for all prop types

        Args:
            X: Feature matrix
            y_home: Home team points
            y_away: Away team points
            test_size: Proportion of data to use for testing

        Returns:
            Dictionary with training metrics for each prop type
        """
        if X.empty or len(y_home) == 0:
            raise ValueError("Cannot train on empty dataset")

        if len(X) != len(y_home) or len(X) != len(y_away):
            raise ValueError("X, y_home, and y_away must have same length")

        logger.info(f"Training {self.model_type} props models on {len(X)} samples")

        # Calculate derived targets
        y_total = y_home + y_away
        y_spread = y_home - y_away  # Positive = home wins by this margin

        targets = {
            'home_points': y_home,
            'away_points': y_away,
            'game_total': y_total,
            'spread': y_spread
        }

        # Split data (same split for all models for consistency)
        X_train, X_test, indices_train, indices_test = train_test_split(
            X, X.index, test_size=test_size, random_state=42
        )

        metrics = {}

        for prop_type, y in targets.items():
            logger.info(f"Training {prop_type} model...")

            y_train = y.loc[indices_train]
            y_test = y.loc[indices_test]

            # Create and train model
            model = self._create_model()
            model.fit(X_train, y_train)
            self.models[prop_type] = model

            # Evaluate
            train_pred = model.predict(X_train)
            test_pred = model.predict(X_test)

            # Calculate metrics
            train_mae = mean_absolute_error(y_train, train_pred)
            test_mae = mean_absolute_error(y_test, test_pred)
            train_rmse = np.sqrt(mean_squared_error(y_train, train_pred))
            test_rmse = np.sqrt(mean_squared_error(y_test, test_pred))
            test_r2 = r2_score(y_test, test_pred)

            # Cross-validation
            cv_scores = cross_val_score(model, X, y, cv=5, scoring='neg_mean_absolute_error')
            cv_mae = -cv_scores.mean()

            metrics[prop_type] = {
                'train_mae': train_mae,
                'test_mae': test_mae,
                'train_rmse': train_rmse,
                'test_rmse': test_rmse,
                'test_r2': test_r2,
                'cv_mae': cv_mae,
                'cv_std': cv_scores.std(),
                'feature_importance': dict(zip(X.columns, model.feature_importances_))
            }

            logger.info(f"  {prop_type}: MAE={test_mae:.2f}, RMSE={test_rmse:.2f}, R2={test_r2:.3f}")

        self.is_trained = True
        return metrics

    def predict(self, X: pd.DataFrame) -> Dict[str, np.ndarray]:
        """
        Make predictions for all prop types

        Args:
            X: Feature matrix

        Returns:
            Dictionary with predictions for each prop type
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")

        predictions = {}
        for prop_type, model in self.models.items():
            predictions[prop_type] = model.predict(X)

        return predictions

    def predict_with_confidence(self, X: pd.DataFrame,
                                 confidence_pct: float = 0.9) -> Dict[str, Dict[str, np.ndarray]]:
        """
        Make predictions with confidence intervals (for Random Forest only)

        For RF: Uses individual tree predictions to estimate uncertainty
        For GB: Returns point estimates only

        Args:
            X: Feature matrix
            confidence_pct: Confidence level (0.9 = 90% CI)

        Returns:
            Dictionary with predictions, lower bounds, and upper bounds
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")

        results = {}
        alpha = (1 - confidence_pct) / 2

        for prop_type, model in self.models.items():
            pred = model.predict(X)

            if self.model_type == "random_forest":
                # Get predictions from individual trees
                tree_preds = np.array([tree.predict(X) for tree in model.estimators_])
                lower = np.percentile(tree_preds, alpha * 100, axis=0)
                upper = np.percentile(tree_preds, (1 - alpha) * 100, axis=0)
            else:
                # For gradient boosting, use empirical std (approximate)
                std_estimate = np.abs(pred) * 0.15  # ~15% uncertainty
                lower = pred - 1.645 * std_estimate
                upper = pred + 1.645 * std_estimate

            results[prop_type] = {
                'prediction': pred,
                'lower': lower,
                'upper': upper
            }

        return results

    def get_actionable_props(self, X: pd.DataFrame,
                             betting_lines: pd.DataFrame,
                             min_edge: float = 2.0,
                             confidence_threshold: float = 0.7) -> pd.DataFrame:
        """
        Compare predictions to betting lines and identify value opportunities

        Args:
            X: Feature matrix (must align with betting_lines index)
            betting_lines: DataFrame with columns: spread, over_under (or total)
            min_edge: Minimum predicted edge in points to recommend
            confidence_threshold: Minimum confidence to make a recommendation

        Returns:
            DataFrame with actionable props recommendations
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")

        predictions = self.predict_with_confidence(X)

        recommendations = []
        tree_predictions = {}
        if self.model_type == "random_forest":
            for prop_type in ['spread', 'game_total']:
                model = self.models.get(prop_type)
                if model is not None:
                    tree_predictions[prop_type] = np.array([tree.predict(X) for tree in model.estimators_])

        def normal_cdf(value: float, mean: float, std: float) -> float:
            if std <= 0:
                return float(value >= mean)
            z = (value - mean) / (std * math.sqrt(2))
            return 0.5 * (1 + math.erf(z))

        for i, (idx, row) in enumerate(betting_lines.iterrows()):
            game_rec = {
                'game_id': idx,
                'home_team': row.get('home_team', 'Unknown'),
                'away_team': row.get('away_team', 'Unknown'),
            }

            # Spread analysis
            if 'spread' in row and pd.notna(row['spread']):
                book_spread = float(row['spread'])  # Negative = home favored
                pred_spread = predictions['spread']['prediction'][i]
                pred_lower = predictions['spread']['lower'][i]
                pred_upper = predictions['spread']['upper'][i]

                spread_edge = pred_spread - book_spread
                if self.model_type == "random_forest" and 'spread' in tree_predictions:
                    tree_preds = tree_predictions['spread'][:, i]
                    p_home = float(np.mean(tree_preds > book_spread))
                else:
                    std_estimate = max(abs(pred_spread) * 0.15, 1e-6)
                    p_home = 1 - normal_cdf(book_spread, pred_spread, std_estimate)

                spread_confidence = p_home if spread_edge > 0 else 1 - p_home

                game_rec['book_spread'] = book_spread
                game_rec['pred_spread'] = round(pred_spread, 1)
                game_rec['spread_edge'] = round(spread_edge, 1)
                game_rec['spread_range'] = f"[{pred_lower:.1f}, {pred_upper:.1f}]"
                game_rec['spread_confidence'] = round(spread_confidence, 2)

                # Determine recommendation
                if abs(spread_edge) >= min_edge and spread_confidence >= confidence_threshold:
                    if spread_edge > 0:
                        game_rec['spread_rec'] = 'TAKE HOME'
                        game_rec['spread_reasoning'] = f"Model predicts home +{spread_edge:.1f} vs line"
                    else:
                        game_rec['spread_rec'] = 'TAKE AWAY'
                        game_rec['spread_reasoning'] = f"Model predicts away {spread_edge:.1f} vs line"
                else:
                    game_rec['spread_rec'] = 'NO EDGE'
                    if abs(spread_edge) < min_edge:
                        game_rec['spread_reasoning'] = f"Edge ({spread_edge:.1f}) below threshold ({min_edge})"
                    else:
                        game_rec['spread_reasoning'] = (
                            f"Confidence ({spread_confidence:.2f}) below threshold ({confidence_threshold})"
                        )

            # Total (Over/Under) analysis
            total_col = 'over_under' if 'over_under' in row else 'total'
            if total_col in row and pd.notna(row[total_col]):
                book_total = float(row[total_col])
                pred_total = predictions['game_total']['prediction'][i]
                pred_lower = predictions['game_total']['lower'][i]
                pred_upper = predictions['game_total']['upper'][i]

                total_edge = pred_total - book_total
                if self.model_type == "random_forest" and 'game_total' in tree_predictions:
                    tree_preds = tree_predictions['game_total'][:, i]
                    p_over = float(np.mean(tree_preds > book_total))
                else:
                    std_estimate = max(abs(pred_total) * 0.15, 1e-6)
                    p_over = 1 - normal_cdf(book_total, pred_total, std_estimate)

                total_confidence = p_over if total_edge > 0 else 1 - p_over

                game_rec['book_total'] = book_total
                game_rec['pred_total'] = round(pred_total, 1)
                game_rec['total_edge'] = round(total_edge, 1)
                game_rec['total_range'] = f"[{pred_lower:.1f}, {pred_upper:.1f}]"
                game_rec['total_confidence'] = round(total_confidence, 2)

                # Determine recommendation
                if abs(total_edge) >= min_edge and total_confidence >= confidence_threshold:
                    if total_edge > 0:
                        game_rec['total_rec'] = 'OVER'
                        game_rec['total_reasoning'] = f"Model predicts {total_edge:.1f} pts above line"
                    else:
                        game_rec['total_rec'] = 'UNDER'
                        game_rec['total_reasoning'] = f"Model predicts {abs(total_edge):.1f} pts below line"
                else:
                    game_rec['total_rec'] = 'NO EDGE'
                    if abs(total_edge) < min_edge:
                        game_rec['total_reasoning'] = f"Edge ({total_edge:.1f}) below threshold ({min_edge})"
                    else:
                        game_rec['total_reasoning'] = (
                            f"Confidence ({total_confidence:.2f}) below threshold ({confidence_threshold})"
                        )

            # Team points predictions
            game_rec['pred_home_pts'] = round(predictions['home_points']['prediction'][i], 1)
            game_rec['pred_away_pts'] = round(predictions['away_points']['prediction'][i], 1)

            recommendations.append(game_rec)

        return pd.DataFrame(recommendations)

    def save(self, filepath: str):
        """Save models to file"""
        try:
            os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else '.', exist_ok=True)

            save_data = {
                'model_type': self.model_type,
                'models': self.models,
                'is_trained': self.is_trained
            }

            with open(filepath, 'wb') as f:
                pickle.dump(save_data, f)
            logger.info(f"Props models saved successfully to {filepath}")
        except Exception as e:
            logger.error(f"Error saving models: {e}")
            raise IOError(f"Failed to save models to {filepath}: {e}")

    def load(self, filepath: str):
        """Load models from file"""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model file not found: {filepath}")

        try:
            with open(filepath, 'rb') as f:
                save_data = pickle.load(f)

            self.model_type = save_data['model_type']
            self.models = save_data['models']
            self.is_trained = save_data['is_trained']
            logger.info(f"Props models loaded successfully from {filepath}")
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            raise IOError(f"Failed to load models from {filepath}: {e}")


def format_actionable_output(recommendations: pd.DataFrame) -> str:
    """
    Format recommendations into a readable actionable report

    Args:
        recommendations: DataFrame from get_actionable_props()

    Returns:
        Formatted string report
    """
    output = []
    output.append("=" * 80)
    output.append("COLLEGE FOOTBALL PROPS - ACTIONABLE RECOMMENDATIONS")
    output.append("=" * 80)
    output.append("")

    # Filter to games with edges
    spread_edges = recommendations[recommendations.get('spread_rec', 'NO EDGE') != 'NO EDGE']
    total_edges = recommendations[recommendations.get('total_rec', 'NO EDGE') != 'NO EDGE']

    # Summary
    output.append(f"Games analyzed: {len(recommendations)}")
    output.append(f"Spread edges found: {len(spread_edges)}")
    output.append(f"Total edges found: {len(total_edges)}")
    output.append("")

    # Spread recommendations
    if len(spread_edges) > 0:
        output.append("-" * 40)
        output.append("SPREAD RECOMMENDATIONS")
        output.append("-" * 40)
        for _, row in spread_edges.iterrows():
            rec = row.get('spread_rec', 'N/A')
            output.append(f"\n{row.get('away_team', 'Away')} @ {row.get('home_team', 'Home')}")
            output.append(f"  Book Spread: {row.get('book_spread', 'N/A')}")
            output.append(f"  Predicted: {row.get('pred_spread', 'N/A')} {row.get('spread_range', '')}")
            output.append(f"  Edge: {row.get('spread_edge', 'N/A')} points")
            if 'spread_confidence' in row:
                output.append(f"  Confidence: {row.get('spread_confidence', 'N/A')}")
            output.append(f"  >>> ACTION: {rec}")
            output.append(f"  Reasoning: {row.get('spread_reasoning', 'N/A')}")

    output.append("")

    # Total recommendations
    if len(total_edges) > 0:
        output.append("-" * 40)
        output.append("TOTAL (O/U) RECOMMENDATIONS")
        output.append("-" * 40)
        for _, row in total_edges.iterrows():
            rec = row.get('total_rec', 'N/A')
            output.append(f"\n{row.get('away_team', 'Away')} @ {row.get('home_team', 'Home')}")
            output.append(f"  Book Total: {row.get('book_total', 'N/A')}")
            output.append(f"  Predicted: {row.get('pred_total', 'N/A')} {row.get('total_range', '')}")
            output.append(f"  Edge: {row.get('total_edge', 'N/A')} points")
            if 'total_confidence' in row:
                output.append(f"  Confidence: {row.get('total_confidence', 'N/A')}")
            output.append(f"  >>> ACTION: {rec}")
            output.append(f"  Reasoning: {row.get('total_reasoning', 'N/A')}")

    output.append("")
    output.append("=" * 80)
    output.append("END OF REPORT")
    output.append("=" * 80)

    return "\n".join(output)
