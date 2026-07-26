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

Each rating system is standardized (z-scored across that week's teams)
before being averaged together, since ELO's raw ~1500 scale would otherwise
swamp SP+/FPI/SRS's much smaller point scales. Each of the four rating
sources is also fetched independently, so one temporarily-unavailable feed
(e.g. FPI) doesn't prevent the others from being used.

### Picking a Side

When ratings and win probability agree on a side, that's a clean signal.
When they disagree, the pick defers to CFBD's own pregame win-probability
model rather than the ratings average — it's a purpose-built combined
estimate, whereas the ratings signal here is just an unweighted average of
four raw rating systems. Ratings only decide the pick when win probability
has no data for that game; home-field advantage is the last-resort default
when neither signal has anything.

### Confidence Scoring Algorithm

Confidence is scored only from signals that agree with the side actually
picked — a signal pointing the other way contributes nothing (and is called
out as a caveat in the reasoning) rather than inflating confidence in a pick
it argues against.

- **HIGH Confidence (6+ points)**: large rating edge (>1.2 SD across the
  standardized rating systems), strong win-probability edge (>30%), and/or
  the betting spread agreeing with the pick
- **MEDIUM Confidence (3-5 points)**: moderate rating edge (0.6-1.2 SD),
  moderate win-probability edge (15-30%)
- **LOW Confidence (0-2 points)**: small/no rating or win-probability edge
  in the picked side's favor, or the available signals mostly disagreeing
  with each other

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
  Reasoning: Large rating edge (1.8 SD); Strong win probability edge (50.6%); Spread aligns with the pick
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

Note: examples using a completed past season (like `2024` once that season
has ended) will print a hindsight-bias warning — see Limitations below.

## Limitations

- **API Key Required**: Most endpoints require a valid CFBD API key
- **Data Availability**: Some rating systems may not be available for all
  teams/weeks (SRS and FPI in particular start partway through a season)
- **Live use only, not a backtest**: FPI, SP+, and SRS have no point-in-time
  lookup in the CFBD API — only ELO accepts a `week` parameter. Requesting a
  past week always returns those three systems' *current* season-to-date
  values, not what was knowable entering that week. This tool is intended
  for live, current-week picks; picks generated for a completed past season
  will look more confident than they should, since three of the four rating
  inputs are effectively hindsight. The script prints a warning when this
  applies.
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

**`Warning: Could not fetch <source> ratings`** — Normal when a specific
rating source (ELO, FPI, SP+, or SRS) isn't published yet for that week or
is temporarily unavailable; each source is fetched independently, so picks
are still generated from whichever of the other three are available.
