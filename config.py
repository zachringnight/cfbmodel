# CFB Model Configuration

# Model Parameters
MODEL_TYPE = "random_forest"  # Options: "random_forest", "gradient_boosting"
RANDOM_STATE = 42
TEST_SIZE = 0.2
CV_FOLDS = 5

# Random Forest Parameters
RF_N_ESTIMATORS = 100
RF_MAX_DEPTH = 10
RF_MIN_SAMPLES_SPLIT = 10

# Gradient Boosting Parameters
GB_N_ESTIMATORS = 100
GB_MAX_DEPTH = 5
GB_LEARNING_RATE = 0.1

# API Parameters
API_TIMEOUT = 30  # seconds
API_MAX_RETRIES = 3

# Data Parameters
MIN_YEAR = 2000
MAX_YEAR = 2100
MIN_WEEK = 1
MAX_WEEK = 20

# Logging
LOG_LEVEL = "INFO"  # Options: "DEBUG", "INFO", "WARNING", "ERROR"
