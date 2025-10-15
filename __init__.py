"""
College Football Prediction Model Package

A production-ready machine learning model for predicting college football 
game outcomes using data from the College Football Data API.
"""

__version__ = "2.0.0"
__author__ = "Zach Ring"

from .model import CFBModel
from .preprocessor import CFBPreprocessor
from .data_fetcher import CFBDataFetcher

__all__ = ['CFBModel', 'CFBPreprocessor', 'CFBDataFetcher']
