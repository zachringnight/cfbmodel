"""
College Football Prediction Model
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from typing import Tuple, Dict, Any
import pickle


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
        """
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        # Train model
        self.model.fit(X_train, y_train)
        
        # Evaluate
        train_pred = self.model.predict(X_train)
        test_pred = self.model.predict(X_test)
        
        train_acc = accuracy_score(y_train, train_pred)
        test_acc = accuracy_score(y_test, test_pred)
        
        # Cross-validation score
        cv_scores = cross_val_score(self.model, X, y, cv=5)
        
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
        """
        with open(filepath, 'wb') as f:
            pickle.dump(self.model, f)
    
    def load(self, filepath: str):
        """
        Load model from file
        
        Args:
            filepath: Path to load the model from
        """
        with open(filepath, 'rb') as f:
            self.model = pickle.load(f)
