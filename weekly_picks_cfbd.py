#!/usr/bin/env python3
"""
Weekly College Football Picks Generator (CFBD ratings + betting lines)

Generates weekly game picks by combining betting lines with team ratings
(ELO, SP+, FPI, SRS) and pregame win probabilities pulled live from the
College Football Data (CFBD) API. Each pick is labeled HIGH / MEDIUM / LOW
confidence with a plain-language explanation of the ratings/market signal
behind it.

This is a complementary, ratings-based sibling to this repo's own trained
models:
    - run_weekly_predictions.py / main.py train and score with cfbmodel's
      own historical data (games.csv, training_data.csv) via scikit-learn.
    - run_props.py / props_model.py do the same for points/spreads/totals.
    - weekly_picks_cfbd.py (this script) instead queries the CFBD API
      directly for that week's live ratings and betting-line feeds, so it
      needs no local training step and reflects same-week market data.

Ported from the picks generator originally prototyped in the
zachringnight/cfbd-python repo (demo_picks.py / examples/weekly_picks.py),
adapted here to import the official `cfbd` package from PyPI instead of a
vendored copy of the SDK. See docs/WEEKLY_PICKS_GUIDE.md for full details.

Requires an API key from https://collegefootballdata.com/key, supplied via
--api-key, the CFBD_API_KEY environment variable, or (for consistency with
the rest of this repo) the CFB_API_KEY environment variable.

CLI usage:
    python weekly_picks_cfbd.py --year 2024 --week 10
    python weekly_picks_cfbd.py --year 2024 --week 10 --conference SEC
    python weekly_picks_cfbd.py --year 2024 --week 10 --min-confidence HIGH

Programmatic usage:
    from weekly_picks_cfbd import WeeklyPicksGenerator

    generator = WeeklyPicksGenerator(api_key="your-key")
    picks = generator.generate_weekly_picks(year=2024, week=10)
    generator.print_picks(picks)
"""

import os
import sys
from typing import Dict, List, Optional, Tuple

import cfbd
from cfbd.rest import ApiException


class WeeklyPicksGenerator:
    """Generate weekly college football picks using CFBD API data."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the picks generator.

        Args:
            api_key: CFBD API key (optional, can be set via the CFBD_API_KEY
                or CFB_API_KEY environment variables)
        """
        configuration = cfbd.Configuration(
            host="https://api.collegefootballdata.com"
        )

        # Set API key if provided, falling back to either env var this repo
        # recognizes (CFBD_API_KEY matches the upstream cfbd convention,
        # CFB_API_KEY matches the convention used by the rest of cfbmodel).
        resolved_key = (
            api_key
            or os.environ.get("CFBD_API_KEY")
            or os.environ.get("CFB_API_KEY")
        )
        if resolved_key:
            configuration.access_token = resolved_key

        self.api_client = cfbd.ApiClient(configuration)
        self.games_api = cfbd.GamesApi(self.api_client)
        self.betting_api = cfbd.BettingApi(self.api_client)
        self.ratings_api = cfbd.RatingsApi(self.api_client)
        self.metrics_api = cfbd.MetricsApi(self.api_client)

    def get_weekly_games(self, year: int, week: int,
                          season_type: str = "regular",
                          conference: Optional[str] = None) -> List:
        """Fetch games for a specific week."""
        try:
            return self.games_api.get_games(
                year=year,
                week=week,
                season_type=season_type,
                conference=conference,
            )
        except ApiException as e:
            print(f"Error fetching games: {e}")
            return []

    def get_betting_lines(self, year: int, week: int,
                           season_type: str = "regular") -> Dict:
        """Fetch betting lines for games in a specific week."""
        try:
            lines = self.betting_api.get_lines(
                year=year,
                week=week,
                season_type=season_type,
            )

            betting_data = {}
            for game in lines:
                if not game.id:
                    continue

                betting_data[game.id] = {
                    "spread": None,
                    "over_under": None,
                    "lines": [],
                }

                if game.lines:
                    for line in game.lines:
                        betting_data[game.id]["lines"].append({
                            "provider": line.provider,
                            "spread": line.spread,
                            "formatted_spread": line.formatted_spread,
                            "over_under": line.over_under,
                        })

                        # Use the first available spread/total
                        if line.spread and betting_data[game.id]["spread"] is None:
                            betting_data[game.id]["spread"] = line.spread
                        if line.over_under and betting_data[game.id]["over_under"] is None:
                            betting_data[game.id]["over_under"] = line.over_under

            return betting_data
        except ApiException as e:
            print(f"Error fetching betting lines: {e}")
            return {}

    def get_team_ratings(self, year: int, week: Optional[int] = None) -> Dict:
        """Fetch ELO, FPI, SP+, and SRS ratings for analysis."""
        ratings = {"elo": {}, "fpi": {}, "sp": {}, "srs": {}}

        try:
            for rating in self.ratings_api.get_elo(year=year, week=week):
                if rating.team:
                    ratings["elo"][rating.team] = rating.elo

            for rating in self.ratings_api.get_fpi(year=year):
                if rating.team:
                    ratings["fpi"][rating.team] = rating.fpi

            for rating in self.ratings_api.get_sp(year=year):
                if rating.team:
                    ratings["sp"][rating.team] = rating.rating

            for rating in self.ratings_api.get_srs(year=year):
                if rating.team:
                    ratings["srs"][rating.team] = rating.rating

        except ApiException as e:
            print(f"Warning: Could not fetch all ratings: {e}")

        return ratings

    def _normalize_ratings(self, ratings: Dict) -> Dict:
        """Z-score each rating system across all teams with a value that week.

        Raw ELO ratings (~1500 scale) and SP+/FPI/SRS point-scale ratings
        get averaged together directly downstream. Without standardizing
        first, whichever system(s) happen to have data for a given matchup
        dominate the combined signal (ELO alone can swing the average by
        hundreds of points versus single-digit SP+/FPI/SRS contributions).
        Standardizing each system to a comparable scale first fixes that.
        """
        normalized: Dict[str, Dict[str, float]] = {}
        for rating_type, team_values in ratings.items():
            values = list(team_values.values())
            if len(values) < 2:
                normalized[rating_type] = dict.fromkeys(team_values, 0.0)
                continue
            mean = sum(values) / len(values)
            variance = sum((v - mean) ** 2 for v in values) / len(values)
            std = variance ** 0.5
            if std == 0:
                normalized[rating_type] = dict.fromkeys(team_values, 0.0)
            else:
                normalized[rating_type] = {
                    team: (value - mean) / std for team, value in team_values.items()
                }
        return normalized

    def get_win_probabilities(self, year: int, week: int,
                               season_type: str = "regular") -> Dict:
        """Fetch pregame win probabilities.

        The cfbd>=5 SDK's PregameWinProbability model only exposes a single
        ``home_win_probability`` field (a 0-1 fraction) — there is no
        ``away_win_probability``. We derive the away-side value and scale
        both to 0-100 to match the rest of this module's percentage-based
        thresholds and display formatting.
        """
        try:
            probabilities = self.metrics_api.get_pregame_win_probabilities(
                year=year,
                week=week,
                season_type=season_type,
            )

            result = {}
            for prob in probabilities:
                if not prob.game_id:
                    continue
                home_pct = prob.home_win_probability * 100
                result[prob.game_id] = {
                    "home_win_prob": home_pct,
                    "away_win_prob": 100 - home_pct,
                    "spread": prob.spread,
                }
            return result
        except ApiException as e:
            print(f"Error fetching win probabilities: {e}")
            return {}

    def calculate_pick_confidence(self,
                                   ratings_diff: float,
                                   win_prob_diff: float,
                                   spread: Optional[float]) -> Tuple[str, str]:
        """
        Calculate pick confidence based on available data.

        Returns:
            Tuple of (confidence_level, reasoning)
        """
        confidence_score = 0
        reasons = []

        # Rating difference contributes to confidence.
        # ratings_diff is an average of per-system z-scores (see
        # _normalize_ratings), so it typically ranges roughly -3..3 rather
        # than the raw ELO-dominated scale this was originally tuned for.
        if abs(ratings_diff) > 1.2:
            confidence_score += 3
            reasons.append(f"Large rating edge ({ratings_diff:+.2f} SD)")
        elif abs(ratings_diff) > 0.6:
            confidence_score += 2
            reasons.append(f"Moderate rating edge ({ratings_diff:+.2f} SD)")
        elif abs(ratings_diff) > 0.25:
            confidence_score += 1
            reasons.append(f"Small rating edge ({ratings_diff:+.2f} SD)")

        # Win probability difference
        if abs(win_prob_diff) > 30:
            confidence_score += 3
            reasons.append(f"Strong win probability edge ({win_prob_diff:.1f}%)")
        elif abs(win_prob_diff) > 15:
            confidence_score += 2
            reasons.append(f"Moderate win probability edge ({win_prob_diff:.1f}%)")
        elif abs(win_prob_diff) > 5:
            confidence_score += 1
            reasons.append(f"Slight win probability edge ({win_prob_diff:.1f}%)")

        # Spread agreement
        if spread is not None:
            if (ratings_diff > 0 and spread < 0) or (ratings_diff < 0 and spread > 0):
                confidence_score += 2
                reasons.append("Ratings align with spread")

        if confidence_score >= 6:
            confidence = "HIGH"
        elif confidence_score >= 3:
            confidence = "MEDIUM"
        else:
            confidence = "LOW"

        reasoning = "; ".join(reasons) if reasons else "Limited data available"
        return confidence, reasoning

    def make_pick(self, game, ratings: Dict, win_probs: Dict,
                  betting_data: Dict) -> Dict:
        """Generate a pick for a single game.

        ``ratings`` is expected to already be normalized (see
        _normalize_ratings) so that averaging across rating systems is
        scale-comparable.
        """
        pick_data = {
            "game_id": game.id,
            "home_team": game.home_team,
            "away_team": game.away_team,
            "week": game.week,
            "pick": None,
            "confidence": None,
            "reasoning": None,
            "spread": None,
            "win_probability": None,
        }

        if game.id in betting_data:
            pick_data["spread"] = betting_data[game.id].get("spread")

        # Average each team's rating across all available systems
        home_ratings = []
        away_ratings = []
        for rating_type in ("elo", "fpi", "sp", "srs"):
            if game.home_team in ratings[rating_type]:
                home_ratings.append(ratings[rating_type][game.home_team])
            if game.away_team in ratings[rating_type]:
                away_ratings.append(ratings[rating_type][game.away_team])

        ratings_diff = 0
        if home_ratings and away_ratings:
            avg_home = sum(home_ratings) / len(home_ratings)
            avg_away = sum(away_ratings) / len(away_ratings)
            ratings_diff = avg_home - avg_away

        win_prob_diff = 0
        if game.id in win_probs:
            home_prob = win_probs[game.id].get("home_win_prob", 50)
            away_prob = win_probs[game.id].get("away_win_prob", 50)
            win_prob_diff = home_prob - away_prob
            pick_data["win_probability"] = home_prob

        # Make the pick
        if ratings_diff > 0 or win_prob_diff > 0:
            pick_data["pick"] = game.home_team
        elif ratings_diff < 0 or win_prob_diff < 0:
            pick_data["pick"] = game.away_team
        else:
            # No clear edge; go with home-field advantage. Use a small
            # nudge (well under the "small edge" threshold) rather than a
            # full z-score's worth of ratings_diff, since this path means
            # we have no real signal and shouldn't be scored as if we did.
            pick_data["pick"] = game.home_team
            ratings_diff = 0.1

        confidence, reasoning = self.calculate_pick_confidence(
            ratings_diff, win_prob_diff, pick_data["spread"]
        )
        pick_data["confidence"] = confidence
        pick_data["reasoning"] = reasoning

        return pick_data

    def generate_weekly_picks(self, year: int, week: int,
                               season_type: str = "regular",
                               conference: Optional[str] = None,
                               min_confidence: Optional[str] = None) -> List[Dict]:
        """Generate picks for every game in a week."""
        print(f"Generating picks for {year} Week {week} ({season_type})...")
        print("=" * 80)

        print("Fetching games...")
        games = self.get_weekly_games(year, week, season_type, conference)
        if not games:
            print("No games found for specified criteria.")
            return []
        print(f"Found {len(games)} games")

        print("Fetching betting lines...")
        betting_data = self.get_betting_lines(year, week, season_type)

        print("Fetching team ratings...")
        ratings = self._normalize_ratings(self.get_team_ratings(year, week))

        print("Fetching win probabilities...")
        win_probs = self.get_win_probabilities(year, week, season_type)

        print("\nGenerating picks...")
        print("=" * 80)

        all_picks = []
        for game in games:
            if not (game.home_team and game.away_team):
                continue

            pick = self.make_pick(game, ratings, win_probs, betting_data)

            if min_confidence:
                confidence_levels = ["LOW", "MEDIUM", "HIGH"]
                if confidence_levels.index(pick["confidence"]) >= confidence_levels.index(min_confidence):
                    all_picks.append(pick)
            else:
                all_picks.append(pick)

        return all_picks

    def print_picks(self, picks: List[Dict], show_reasoning: bool = True):
        """Print picks in a readable format, grouped by confidence."""
        if not picks:
            print("No picks to display.")
            return

        high_confidence = [p for p in picks if p["confidence"] == "HIGH"]
        medium_confidence = [p for p in picks if p["confidence"] == "MEDIUM"]
        low_confidence = [p for p in picks if p["confidence"] == "LOW"]

        print(f"\n{'=' * 80}")
        print(f"WEEKLY PICKS SUMMARY ({len(picks)} games)")
        print(f"{'=' * 80}")
        print(f"High Confidence: {len(high_confidence)}")
        print(f"Medium Confidence: {len(medium_confidence)}")
        print(f"Low Confidence: {len(low_confidence)}")

        for confidence_level, picks_list in [
            ("HIGH CONFIDENCE PICKS", high_confidence),
            ("MEDIUM CONFIDENCE PICKS", medium_confidence),
            ("LOW CONFIDENCE PICKS", low_confidence),
        ]:
            if not picks_list:
                continue

            print(f"\n{'-' * 80}")
            print(confidence_level)
            print(f"{'-' * 80}")

            for pick in picks_list:
                print(f"\n{pick['away_team']} @ {pick['home_team']}")
                print(f"  Pick: {pick['pick']} ({pick['confidence']} confidence)")

                if pick["spread"] is not None:
                    print(f"  Spread: {pick['spread']}")

                if pick["win_probability"] is not None:
                    other_prob = 100 - pick["win_probability"]
                    if pick["pick"] == pick["home_team"]:
                        print(f"  Win Probability: {pick['home_team']} {pick['win_probability']:.1f}% | {pick['away_team']} {other_prob:.1f}%")
                    else:
                        print(f"  Win Probability: {pick['away_team']} {other_prob:.1f}% | {pick['home_team']} {pick['win_probability']:.1f}%")

                if show_reasoning and pick["reasoning"]:
                    print(f"  Reasoning: {pick['reasoning']}")

        print(f"\n{'=' * 80}\n")


def main():
    """CLI entry point for generating weekly CFBD-ratings-based picks."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate weekly college football picks from CFBD ratings and betting lines"
    )
    parser.add_argument("--year", type=int, required=True,
                         help="Season year (e.g., 2024)")
    parser.add_argument("--week", type=int, required=True,
                         help="Week number (e.g., 10)")
    parser.add_argument("--season-type", type=str, default="regular",
                         choices=["regular", "postseason"],
                         help="Season type (default: regular)")
    parser.add_argument("--conference", type=str,
                         help="Optional conference filter (e.g., SEC, B1G)")
    parser.add_argument("--min-confidence", type=str,
                         choices=["LOW", "MEDIUM", "HIGH"],
                         help="Minimum confidence level to display")
    parser.add_argument("--api-key", type=str,
                         help="CFBD API key (or set CFBD_API_KEY / CFB_API_KEY env var)")
    parser.add_argument("--no-reasoning", action="store_true",
                         help="Hide detailed reasoning for picks")

    args = parser.parse_args()

    if not args.api_key and not (os.environ.get("CFBD_API_KEY") or os.environ.get("CFB_API_KEY")):
        print("Warning: No API key provided. Some endpoints may not work.")
        print("Get an API key from: https://collegefootballdata.com/key")
        print("Set it with --api-key, CFBD_API_KEY, or CFB_API_KEY.\n")

    try:
        generator = WeeklyPicksGenerator(api_key=args.api_key)

        picks = generator.generate_weekly_picks(
            year=args.year,
            week=args.week,
            season_type=args.season_type,
            conference=args.conference,
            min_confidence=args.min_confidence,
        )

        generator.print_picks(picks, show_reasoning=not args.no_reasoning)

        if picks:
            high_conf = sum(1 for p in picks if p["confidence"] == "HIGH")
            print(f"Generated {len(picks)} picks")
            print(f"Recommended plays: {high_conf} high confidence picks")

    except ApiException as e:
        print(f"\nAPI Error: {e}")
        if e.status == 401:
            print("Authentication failed. Check your API key.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
