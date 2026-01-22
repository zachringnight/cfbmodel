"""
Enhanced training pipeline that leverages all available data fields.
"""

from __future__ import annotations

import dataclasses
import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    brier_score_loss,
    classification_report,
    log_loss,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


LEAKAGE_COLUMNS = {
    "home_points",
    "away_points",
    "margin",
    "spread",
}

NON_FEATURE_COLUMNS = {
    "id",
}


@dataclasses.dataclass
class ProfitModelMetrics:
    accuracy: float
    roc_auc: float
    log_loss: float
    brier_score: float
    classification_report: str


def _add_date_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add date-derived features for start_date if present."""
    if "start_date" not in df.columns:
        return df

    date_series = pd.to_datetime(df["start_date"], errors="coerce", utc=True)
    df = df.copy()
    df["start_year"] = date_series.dt.year
    df["start_month"] = date_series.dt.month
    df["start_dayofweek"] = date_series.dt.dayofweek
    return df.drop(columns=["start_date"])


def _load_season_stats(path: str = "season_stats.zip") -> pd.DataFrame:
    """Load season-level stats from the starter pack zip if available."""
    stats_path = Path(path)
    if not stats_path.exists():
        return pd.DataFrame()

    frames = []
    with zipfile.ZipFile(stats_path) as zipped:
        for name in zipped.namelist():
            if not name.startswith("season_stats/") or not name.endswith(".csv"):
                continue
            if "__MACOSX" in name:
                continue
            with zipped.open(name) as handle:
                frames.append(pd.read_csv(handle))

    if not frames:
        return pd.DataFrame()

    stats = pd.concat(frames, ignore_index=True)
    stats["plays"] = stats["passAttempts"] + stats["rushingAttempts"]
    stats["plays_opponent"] = stats["passAttemptsOpponent"] + stats["rushingAttemptsOpponent"]
    stats["plays_per_game"] = stats["plays"] / stats["games"]
    stats["plays_per_game_opponent"] = stats["plays_opponent"] / stats["games"]
    stats["pass_rate"] = stats["passAttempts"] / stats["plays"].replace(0, np.nan)
    stats["rush_rate"] = stats["rushingAttempts"] / stats["plays"].replace(0, np.nan)
    stats["pass_rate_opponent"] = stats["passAttemptsOpponent"] / stats["plays_opponent"].replace(
        0, np.nan
    )
    stats["rush_rate_opponent"] = stats["rushingAttemptsOpponent"] / stats["plays_opponent"].replace(
        0, np.nan
    )
    stats["possession_time_per_game"] = stats["possessionTime"] / stats["games"]
    stats["possession_time_per_game_opponent"] = stats["possessionTimeOpponent"] / stats["games"]

    pace_cols = [
        "season",
        "team",
        "plays_per_game",
        "plays_per_game_opponent",
        "pass_rate",
        "rush_rate",
        "pass_rate_opponent",
        "rush_rate_opponent",
        "possession_time_per_game",
        "possession_time_per_game_opponent",
    ]
    return stats[pace_cols]


def _merge_season_stats(df: pd.DataFrame, stats: pd.DataFrame) -> pd.DataFrame:
    """Merge pace and play-style stats for home and away teams."""
    if stats.empty or "season" not in df.columns:
        return df

    home_stats = stats.rename(
        columns={
            col: f"home_{col}"
            for col in stats.columns
            if col not in {"season", "team"}
        }
    )
    home_stats = home_stats.rename(columns={"team": "home_team", "season": "season"})
    away_stats = stats.rename(
        columns={
            col: f"away_{col}"
            for col in stats.columns
            if col not in {"season", "team"}
        }
    )
    away_stats = away_stats.rename(columns={"team": "away_team", "season": "season"})

    df = df.merge(home_stats, on=["season", "home_team"], how="left")
    df = df.merge(away_stats, on=["season", "away_team"], how="left")
    return df


def load_training_frame(path: str, season_stats_path: str = "season_stats.zip") -> pd.DataFrame:
    """Load the raw training data from CSV."""
    df = pd.read_csv(path)
    df = df.dropna(how="all")
    df = _add_date_features(df)
    return _merge_season_stats(df, _load_season_stats(season_stats_path))


def build_training_sets(
    df: pd.DataFrame,
    holdout_season: Optional[int] = None,
) -> Tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series]:
    """Split into train and holdout sets using season-based separation."""
    df = df.copy()
    df["home_win"] = (df["home_points"] > df["away_points"]).astype(int)

    drop_cols = set(LEAKAGE_COLUMNS) | set(NON_FEATURE_COLUMNS) | {"home_win"}
    features = df.drop(columns=[c for c in drop_cols if c in df.columns])

    if holdout_season is None and "season" in df.columns:
        holdout_season = int(df["season"].max())

    if holdout_season is not None and "season" in df.columns:
        train_mask = df["season"] < holdout_season
        if train_mask.any():
            X_train = features.loc[train_mask]
            y_train = df.loc[train_mask, "home_win"]
            X_test = features.loc[~train_mask]
            y_test = df.loc[~train_mask, "home_win"]
            return X_train, y_train, X_test, y_test

    X_train, X_test, y_train, y_test = train_test_split(
        features, df["home_win"], test_size=0.2, random_state=42, stratify=df["home_win"]
    )
    return X_train, y_train, X_test, y_test


def _build_pipeline(X: pd.DataFrame) -> Pipeline:
    categorical_cols = X.select_dtypes(include=["object", "bool"]).columns.tolist()
    numeric_cols = [col for col in X.columns if col not in categorical_cols]

    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
        ]
    )

    categorical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", numeric_transformer, numeric_cols),
            ("categorical", categorical_transformer, categorical_cols),
        ]
    )

    classifier = LogisticRegression(
        solver="saga",
        max_iter=2000,
        n_jobs=-1,
        class_weight="balanced",
    )

    return Pipeline(steps=[("preprocessor", preprocessor), ("classifier", classifier)])


def train_profit_model(
    data_path: str = "training_data.csv",
    holdout_season: Optional[int] = None,
    season_stats_path: str = "season_stats.zip",
) -> Tuple[Pipeline, ProfitModelMetrics]:
    """Train a calibrated, data-rich model using all available features."""
    df = load_training_frame(data_path, season_stats_path=season_stats_path)
    X_train, y_train, X_test, y_test = build_training_sets(
        df, holdout_season=holdout_season
    )

    pipeline = _build_pipeline(X_train)
    pipeline.fit(X_train, y_train)

    probabilities = pipeline.predict_proba(X_test)[:, 1]
    predictions = (probabilities >= 0.5).astype(int)

    metrics = ProfitModelMetrics(
        accuracy=accuracy_score(y_test, predictions),
        roc_auc=roc_auc_score(y_test, probabilities),
        log_loss=log_loss(y_test, probabilities),
        brier_score=brier_score_loss(y_test, probabilities),
        classification_report=classification_report(y_test, predictions),
    )

    return pipeline, metrics


def get_feature_inventory(df: pd.DataFrame) -> Dict[str, List[str]]:
    """Return feature names categorized by type for reporting."""
    df = df.copy()
    df["home_win"] = (df["home_points"] > df["away_points"]).astype(int)

    drop_cols = set(LEAKAGE_COLUMNS) | set(NON_FEATURE_COLUMNS) | {"home_win"}
    features = df.drop(columns=[c for c in drop_cols if c in df.columns])

    categorical_cols = features.select_dtypes(include=["object", "bool"]).columns.tolist()
    numeric_cols = [col for col in features.columns if col not in categorical_cols]

    return {
        "categorical": categorical_cols,
        "numeric": numeric_cols,
    }
