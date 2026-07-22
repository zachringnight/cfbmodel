# Weekly Picks Guide (CFBD Ratings)

## Overview

`weekly_picks_cfbd.py` is a ratings-based picks generator that queries the
[College Football Data (CFBD) API](https://collegefootballdata.com) directly
for a given week's betting lines, team ratings, and win probabilities, and
turns them into game picks with a HIGH / MEDIUM / LOW confidence label and a
plain-language reason for each one.

It is deliberately a different approach from this repo's own trained models:

| Script | Approach | Data source |
|---|---|---|
| `main.py` / `run_weekly_predictions.py` | Trains a scikit-learn classifier on historical results | `games.csv`, team stats/talent from the API |
| `run_props.py` / `props_model.py` | Trains regressors for points/spreads/totals | `training_data.csv` |
| `weekly_picks_cfbd.py` (this guide) | No training step; scores each game from that week's live CFBD ratings feeds | CFBD betting lines, ELO/SP+/FPI/SRS ratings, pregame win probabilities |

Because it needs no trained model file, it is a fast way to get a second,
independent opinion alongside the repo's own predictions — useful for
sanity-checking `run_weekly_predictions.py` output or for weeks where a
freshly trained model isn't available.

This tool was originally prototyped in the `cfbd-python` repo
(`demo_picks.py` / `examples/weekly_picks.py`) and has been ported here so it
lives alongside the rest of the active prediction pipeline and imports the
official `cfbd` package from PyPI (see `requirements.txt`) instead of a
vendored copy of the SDK.

## Features

- **Multi-Source Analysis**: Combines betting lines, team ratings (ELO, SP+,
  FPI, SRS), and pregame win probabilities
- **Confidence Scoring**: Each pick gets a confidence level (HIGH, MEDIUM,
  LOW) based on how strongly the signals agree
- **Detailed Reasoning**: Explains the ratings/market signal behind each pick
- **Flexible Filtering**: Filter by conference, week, season type, and
  minimum confidence level
- **CLI or Programmatic**: Use it as a script or import `WeeklyPicksGenerator`
  into your own code

## Quick Start

### Get an API Key

Sign up for a free API key at [CollegeFootballData.com](https://collegefootballdata.com/key).

### Basic Usage

```bash
# Set your API key (either variable name works)
export CFBD_API_KEY='your-api-key-here'
# or: export CFB_API_KEY='your-api-key-here'

# Generate picks for a specific week
python weekly_picks_cfbd.py --year 2024 --week 10

# Filter by conference
python weekly_picks_cfbd.py --year 2024 --week 10 --conference SEC

# Show only high-confidence picks
python weekly_picks_cfbd.py --year 2024 --week 10 --min-confidence HIGH
```

## Command-Line Options

| Option | Description | Required |
|--------|-------------|----------|
| `--year` | Season year (e.g., 2024) | Yes |
| `--week` | Week number (e.g., 10) | Yes |
| `--season-type` | Season type: `regular` or `postseason` | No (default: regular) |
| `--conference` | Conference abbreviation (e.g., SEC, B1G, ACC) | No |
| `--min-confidence` | Minimum confidence: `LOW`, `MEDIUM`, or `HIGH` | No |
| `--api-key` | CFBD API key | No (uses `CFBD_API_KEY` / `CFB_API_KEY` env var) |
| `--no-reasoning` | Hide detailed reasoning | No |

## How It Works

### Data Sources

1. **Betting Lines**: Point spreads and over/under totals
2. **Team Ratings**:
   - **ELO**: Chess-style rating tracking team performance over time
   - **SP+**: Tempo-free ratings adjusting for opponent strength
   - **FPI**: ESPN's Football Power Index
   - **SRS**: Simple Rating System based on point differential and strength of schedule
3. **Win Probabilities**: Pregame win probability models from CFBD

### Confidence Scoring Algorithm

- **HIGH Confidence (6+ points)**: large rating differences (>20 points),
  strong win-probability edges (>30%), and/or ratings agreeing with the
  market spread
- **MEDIUM Confidence (3-5 points)**: moderate rating differences
  (10-20 points), moderate win-probability edges (15-30%)
- **LOW Confidence (0-2 points)**: small rating differences, slight
  win-probability edges, or limited/conflicting data

### Output Format

```
================================================================================
WEEKLY PICKS SUMMARY (15 games)
================================================================================
High Confidence: 5
Medium Confidence: 7
Low Confidence: 3

--------------------------------------------------------------------------------
HIGH CONFIDENCE PICKS
--------------------------------------------------------------------------------

Florida State @ Clemson
  Pick: Clemson (HIGH confidence)
  Spread: -10.5
  Win Probability: Clemson 75.3% | Florida State 24.7%
  Reasoning: Large rating difference (15.2); Strong win probability edge (50.6%); Ratings align with spread
```

## Programmatic Usage

```python
from weekly_picks_cfbd import WeeklyPicksGenerator

# Initialize with an API key
generator = WeeklyPicksGenerator(api_key='your-key-here')

# Generate picks
picks = generator.generate_weekly_picks(
    year=2024,
    week=10,
    season_type='regular',
    conference='SEC',
    min_confidence='MEDIUM'
)

# Display results
generator.print_picks(picks, show_reasoning=True)

# Or process picks programmatically
for pick in picks:
    if pick['confidence'] == 'HIGH':
        opponent = pick['away_team'] if pick['pick'] == pick['home_team'] else pick['home_team']
        print(f"Recommended: {pick['pick']} over {opponent}")
```

`calculate_pick_confidence()` and `make_pick()` are also usable directly if
you want to score matchups you've already fetched data for.

## Examples

```bash
# Rivalry week, high-confidence picks only
python weekly_picks_cfbd.py --year 2024 --week 13 --min-confidence HIGH

# Conference championship week, one conference
python weekly_picks_cfbd.py --year 2024 --week 15 --conference SEC

# Bowl season
python weekly_picks_cfbd.py --year 2024 --week 1 --season-type postseason
```

## Limitations

- **API Key Required**: Most endpoints require a valid CFBD API key
- **Data Availability**: Some rating systems may not be available for all
  teams/weeks (SRS and FPI in particular start partway through a season)
- **No Guarantees**: This is an analytical aid, not a promise of outcomes —
  use it alongside `run_weekly_predictions.py`/`run_props.py` and your own
  judgment, not as a substitute for either

## Troubleshooting

**`API Error: 401`** — Your API key is missing or invalid. Verify it's set:
```bash
export CFBD_API_KEY='your-actual-key'
```

**`No games found for specified criteria.`** — Check that the year/week
combination is valid and that games exist for the specified conference or
season type.

**`Warning: Could not fetch all ratings`** — Normal when a rating source
(e.g., FPI or SRS) isn't published yet for that week; picks are still
generated from whatever data is available.
