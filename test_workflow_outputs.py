#!/usr/bin/env python3
"""
Test the workflow outputs generation
"""

import os
import sys
import json
import pandas as pd
import numpy as np
from model import CFBModel
from preprocessor import CFBPreprocessor


def test_model_outputs():
    """Test that the model can generate and save outputs"""
    print("=== Testing Model Output Generation ===\n")
    
    # Create sample data
    print("1. Creating sample training data...")
    X_train = pd.DataFrame({
        'home_off_total_yards': np.random.randint(200, 500, 100),
        'away_off_total_yards': np.random.randint(200, 500, 100),
        'home_off_passing_yards': np.random.randint(150, 350, 100),
        'away_off_passing_yards': np.random.randint(150, 350, 100),
        'home_off_rushing_yards': np.random.randint(50, 200, 100),
        'away_off_rushing_yards': np.random.randint(50, 200, 100),
        'home_talent': np.random.uniform(50, 100, 100),
        'away_talent': np.random.uniform(50, 100, 100),
        'yards_diff': np.random.uniform(-100, 100, 100),
    })
    y_train = pd.Series(np.random.randint(0, 2, 100))
    print(f"   ✓ Created training data: {X_train.shape}")
    
    # Train model
    print("\n2. Training model...")
    model = CFBModel(model_type="random_forest")
    metrics = model.train(X_train, y_train, test_size=0.3)
    print(f"   ✓ Model trained successfully")
    print(f"   ✓ Training accuracy: {metrics['train_accuracy']:.2%}")
    print(f"   ✓ Test accuracy: {metrics['test_accuracy']:.2%}")
    
    # Save model
    print("\n3. Saving model...")
    test_model_path = "/tmp/test_cfb_model.pkl"
    model.save(test_model_path)
    print(f"   ✓ Model saved to {test_model_path}")
    
    # Load model
    print("\n4. Loading model...")
    loaded_model = CFBModel()
    loaded_model.load(test_model_path)
    print(f"   ✓ Model loaded successfully")
    
    # Create sample prediction data
    print("\n5. Creating sample prediction data...")
    X_pred = pd.DataFrame({
        'home_off_total_yards': np.random.randint(200, 500, 10),
        'away_off_total_yards': np.random.randint(200, 500, 10),
        'home_off_passing_yards': np.random.randint(150, 350, 10),
        'away_off_passing_yards': np.random.randint(150, 350, 10),
        'home_off_rushing_yards': np.random.randint(50, 200, 10),
        'away_off_rushing_yards': np.random.randint(50, 200, 10),
        'home_talent': np.random.uniform(50, 100, 10),
        'away_talent': np.random.uniform(50, 100, 10),
        'yards_diff': np.random.uniform(-100, 100, 10),
    })
    print(f"   ✓ Created prediction data: {X_pred.shape}")
    
    # Make predictions
    print("\n6. Making predictions...")
    predictions = loaded_model.predict(X_pred)
    probabilities = loaded_model.predict_proba(X_pred)
    print(f"   ✓ Generated {len(predictions)} predictions")
    
    # Build output structure
    print("\n7. Building output structure...")
    predictions_list = []
    for i in range(len(predictions)):
        pred = predictions[i]
        prob = probabilities[i]
        
        prediction_entry = {
            "game_number": i + 1,
            "home_team": f"Home Team {i+1}",
            "away_team": f"Away Team {i+1}",
            "predicted_winner": "Home" if pred == 1 else "Away",
            "confidence": round(max(prob) * 100, 2),
            "home_win_probability": round(prob[1] * 100, 2),
            "away_win_probability": round(prob[0] * 100, 2)
        }
        predictions_list.append(prediction_entry)
    
    output_data = {
        "metadata": {
            "year": 2024,
            "week": 8,
            "model_type": "random_forest",
            "games_found": len(predictions)
        },
        "predictions": predictions_list
    }
    print(f"   ✓ Built output structure with {len(predictions_list)} entries")
    
    # Save to JSON
    print("\n8. Saving outputs...")
    json_path = "/tmp/test_predictions.json"
    with open(json_path, 'w') as f:
        json.dump(output_data, f, indent=2)
    print(f"   ✓ JSON saved to {json_path}")
    
    # Save to CSV
    csv_path = "/tmp/test_predictions.csv"
    df = pd.DataFrame(predictions_list)
    df.to_csv(csv_path, index=False)
    print(f"   ✓ CSV saved to {csv_path}")
    
    # Verify files exist
    print("\n9. Verifying output files...")
    assert os.path.exists(json_path), "JSON file not created"
    assert os.path.exists(csv_path), "CSV file not created"
    print(f"   ✓ JSON file size: {os.path.getsize(json_path)} bytes")
    print(f"   ✓ CSV file size: {os.path.getsize(csv_path)} bytes")
    
    # Display sample output
    print("\n10. Sample JSON output:")
    print(json.dumps(output_data['predictions'][0], indent=2))
    
    print("\n=== All Tests Passed ✓ ===\n")
    return True


if __name__ == "__main__":
    try:
        success = test_model_outputs()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
