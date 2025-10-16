#!/usr/bin/env python3
"""
Example: How to use prediction outputs from the workflow
"""

import json
import pandas as pd


def analyze_predictions_from_json(json_file):
    """Analyze predictions from JSON output"""
    print(f"=== Analyzing Predictions from {json_file} ===\n")
    
    # Load predictions
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    metadata = data['metadata']
    predictions = data['predictions']
    
    print(f"Year: {metadata['year']}")
    print(f"Week: {metadata['week']}")
    print(f"Model Type: {metadata['model_type']}")
    print(f"Total Games: {metadata['games_found']}")
    if 'generated_at' in metadata:
        print(f"Generated At: {metadata['generated_at']}")
    print()
    
    # Calculate statistics
    home_wins = sum(1 for p in predictions if p['predicted_winner'] == p['home_team'])
    away_wins = sum(1 for p in predictions if p['predicted_winner'] == p['away_team'])
    
    high_confidence = [p for p in predictions if p['confidence'] > 75]
    low_confidence = [p for p in predictions if p['confidence'] < 55]
    
    print(f"=== Prediction Statistics ===")
    print(f"Home Wins Predicted: {home_wins} ({home_wins/len(predictions)*100:.1f}%)")
    print(f"Away Wins Predicted: {away_wins} ({away_wins/len(predictions)*100:.1f}%)")
    print(f"High Confidence (>75%): {len(high_confidence)} games")
    print(f"Low Confidence (<55%): {len(low_confidence)} games")
    print()
    
    # Show high confidence predictions
    if high_confidence:
        print(f"=== High Confidence Predictions ===")
        for p in sorted(high_confidence, key=lambda x: x['confidence'], reverse=True):
            print(f"{p['away_team']} @ {p['home_team']}")
            print(f"  Winner: {p['predicted_winner']} ({p['confidence']:.1f}% confidence)")
        print()
    
    # Show toss-up games
    if low_confidence:
        print(f"=== Toss-Up Games (<55% confidence) ===")
        for p in sorted(low_confidence, key=lambda x: x['confidence']):
            print(f"{p['away_team']} @ {p['home_team']}")
            print(f"  Winner: {p['predicted_winner']} ({p['confidence']:.1f}% confidence)")
        print()
    
    return data


def analyze_predictions_from_csv(csv_file):
    """Analyze predictions from CSV output"""
    print(f"=== Analyzing Predictions from {csv_file} ===\n")
    
    # Load predictions
    df = pd.read_csv(csv_file)
    
    print(f"Total Games: {len(df)}")
    print()
    
    # Statistics
    print(f"=== Statistical Analysis ===")
    print(f"Average Confidence: {df['confidence'].mean():.1f}%")
    print(f"Median Confidence: {df['confidence'].median():.1f}%")
    print(f"Min Confidence: {df['confidence'].min():.1f}%")
    print(f"Max Confidence: {df['confidence'].max():.1f}%")
    print()
    
    # Home field advantage analysis
    home_win_prob = df['home_win_probability'].mean()
    print(f"Average Home Win Probability: {home_win_prob:.1f}%")
    print()
    
    # Games by confidence bracket
    print(f"=== Games by Confidence Level ===")
    print(f"Very High (>85%): {len(df[df['confidence'] > 85])} games")
    print(f"High (75-85%): {len(df[(df['confidence'] > 75) & (df['confidence'] <= 85)])} games")
    print(f"Medium (60-75%): {len(df[(df['confidence'] > 60) & (df['confidence'] <= 75)])} games")
    print(f"Low (50-60%): {len(df[(df['confidence'] > 50) & (df['confidence'] <= 60)])} games")
    print(f"Toss-Up (50-55%): {len(df[(df['confidence'] >= 50) & (df['confidence'] <= 55)])} games")
    print()
    
    return df


def export_top_picks(predictions_data, output_file, min_confidence=75):
    """Export top picks to a new file"""
    predictions = predictions_data['predictions']
    
    top_picks = [
        p for p in predictions 
        if p['confidence'] >= min_confidence
    ]
    
    # Sort by confidence
    top_picks.sort(key=lambda x: x['confidence'], reverse=True)
    
    with open(output_file, 'w') as f:
        f.write(f"# Top Picks (>= {min_confidence}% confidence)\n")
        f.write(f"Week {predictions_data['metadata']['week']} - {predictions_data['metadata']['year']}\n")
        if 'generated_at' in predictions_data['metadata']:
            f.write(f"Generated: {predictions_data['metadata']['generated_at']}\n")
        f.write("\n")
        
        for i, p in enumerate(top_picks, 1):
            f.write(f"{i}. {p['predicted_winner']} - {p['confidence']:.1f}% confidence\n")
            f.write(f"   {p['away_team']} @ {p['home_team']}\n\n")
    
    print(f"✓ Exported {len(top_picks)} top picks to {output_file}")


if __name__ == "__main__":
    import sys
    
    # Use test files if available
    json_file = "/tmp/test_predictions.json"
    csv_file = "/tmp/test_predictions.csv"
    
    # Check if files exist from command line arguments
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
        csv_file = json_file.replace('.json', '.csv')
    
    try:
        # Analyze JSON
        print("="*70)
        data = analyze_predictions_from_json(json_file)
        print("="*70)
        print()
        
        # Analyze CSV
        print("="*70)
        df = analyze_predictions_from_csv(csv_file)
        print("="*70)
        print()
        
        # Export top picks
        export_top_picks(data, "/tmp/top_picks.txt", min_confidence=70)
        print()
        
        print("✓ Analysis complete!")
        
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
        print("\nUsage: python example_use_outputs.py [predictions.json]")
        print("\nOr run test_workflow_outputs.py first to generate test files:")
        print("  python test_workflow_outputs.py")
        print("  python example_use_outputs.py")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
