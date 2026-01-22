#!/usr/bin/env python3
"""
Train the enhanced profit-focused model using all available features.
"""

import argparse
import pathlib

import joblib

from profit_model import get_feature_inventory, load_training_frame, train_profit_model


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Train the enhanced CFB model with full feature coverage."
    )
    parser.add_argument(
        "--data-path",
        default="training_data.csv",
        help="Path to the training CSV file.",
    )
    parser.add_argument(
        "--model-path",
        default="cfb_profit_model.joblib",
        help="Path to save the trained model pipeline.",
    )
    parser.add_argument(
        "--holdout-season",
        type=int,
        default=None,
        help="Season to hold out for evaluation (defaults to latest season).",
    )
    parser.add_argument(
        "--season-stats-path",
        default="season_stats.zip",
        help="Path to the season stats zip for pace/style features.",
    )

    args = parser.parse_args()

    data_path = pathlib.Path(args.data_path)
    if not data_path.exists():
        raise SystemExit(f"Training data not found: {data_path}")

    pipeline, metrics = train_profit_model(
        data_path=str(data_path),
        holdout_season=args.holdout_season,
        season_stats_path=args.season_stats_path,
    )

    joblib.dump(pipeline, args.model_path)

    frame = load_training_frame(str(data_path), season_stats_path=args.season_stats_path)
    inventory = get_feature_inventory(frame)

    print("\n=== Enhanced Model Metrics ===")
    print(f"Accuracy: {metrics.accuracy:.4f}")
    print(f"ROC-AUC: {metrics.roc_auc:.4f}")
    print(f"Log Loss: {metrics.log_loss:.4f}")
    print(f"Brier Score: {metrics.brier_score:.4f}")
    print("\nClassification Report:")
    print(metrics.classification_report)

    print("\n=== Feature Coverage ===")
    print(f"Numeric features: {len(inventory['numeric'])}")
    print(f"Categorical features: {len(inventory['categorical'])}")
    print("Sample categorical features:", ", ".join(inventory["categorical"][:8]))

    print(f"\nModel saved to {args.model_path}")


if __name__ == "__main__":
    main()
