"""
College Football Prediction Model
"""

import numpy as np
import pandas as pd
import logging
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from typing import Tuple, Dict, Any
import pickle
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CFBModel:
    """Machine learning model for predicting college football games"""
    
    def __init__(self, model_type: str = "random_forest"):
        """
        Initialize the CFB model
        
        Args:
            model_type: Type of model to use ("random_forest" or "gradient_boosting")
        """
        self.model_type = model_type
        
        if model_type == "random_forest":
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=10,
                random_state=42
            )
        elif model_type == "gradient_boosting":
            self.model = GradientBoostingClassifier(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=42
            )
        else:
            raise ValueError(f"Unknown model type: {model_type}")
    
    def train(self, X: pd.DataFrame, y: pd.Series, 
              test_size: float = 0.2) -> Dict[str, Any]:
        """
        Train the model
        
        Args:
            X: Feature matrix
            y: Target variable
            test_size: Proportion of data to use for testing
            
        Returns:
            Dictionary with training metrics
            
        Raises:
            ValueError: If invalid input data is provided
        """
        if X.empty or len(y) == 0:
            raise ValueError("Cannot train on empty dataset")
        
        if len(X) != len(y):
            raise ValueError(f"X and y must have same length. Got X={len(X)}, y={len(y)}")
        
        if test_size <= 0 or test_size >= 1:
            raise ValueError(f"test_size must be between 0 and 1. Got {test_size}")
        
        logger.info(f"Training {self.model_type} model on {len(X)} samples")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        logger.info(f"Training set: {len(X_train)} samples, Test set: {len(X_test)} samples")
        
        # Train model
        self.model.fit(X_train, y_train)
        logger.info("Model training completed")
        
        # Evaluate
        train_pred = self.model.predict(X_train)
        test_pred = self.model.predict(X_test)
        
        train_acc = accuracy_score(y_train, train_pred)
        test_acc = accuracy_score(y_test, test_pred)
        
        logger.info(f"Training accuracy: {train_acc:.4f}")
        logger.info(f"Test accuracy: {test_acc:.4f}")
        
        # Cross-validation score
        logger.info("Performing cross-validation...")
        cv_scores = cross_val_score(self.model, X, y, cv=5)
        logger.info(f"CV score: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
        
        metrics = {
            "train_accuracy": train_acc,
            "test_accuracy": test_acc,
            "cv_mean": cv_scores.mean(),
            "cv_std": cv_scores.std(),
            "feature_importance": dict(zip(X.columns, self.model.feature_importances_)),
            "classification_report": classification_report(y_test, test_pred)
        }
        
        return metrics
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Make predictions
        
        Args:
            X: Feature matrix
            
        Returns:
            Array of predictions
        """
        return self.model.predict(X)
    
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """
        Predict probabilities
        
        Args:
            X: Feature matrix
            
        Returns:
            Array of prediction probabilities
        """
        return self.model.predict_proba(X)
    
    def save(self, filepath: str):
        """
        Save model to file
        
        Args:
            filepath: Path to save the model
            
        Raises:
            IOError: If unable to save the model
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else '.', exist_ok=True)
            
            with open(filepath, 'wb') as f:
                pickle.dump(self.model, f)
            logger.info(f"Model saved successfully to {filepath}")
        except Exception as e:
            logger.error(f"Error saving model: {e}")
            raise IOError(f"Failed to save model to {filepath}: {e}")
    
    def load(self, filepath: str):
        """
        Load model from file
        
        Args:
            filepath: Path to load the model from
            
        Raises:
            FileNotFoundError: If model file doesn't exist
            IOError: If unable to load the model
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model file not found: {filepath}")
        
        try:
            with open(filepath, 'rb') as f:
                self.model = pickle.load(f)
            logger.info(f"Model loaded successfully from {filepath}")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise IOError(f"Failed to load model from {filepath}: {e}")
