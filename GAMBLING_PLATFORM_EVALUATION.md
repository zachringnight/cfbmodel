# CFB Model: Gambling Platform Evaluation

**Evaluator:** AI Technical Analyst
**Date:** March 2026
**Client:** Professional Gambling Syndicate
**Scope:** Full codebase, data pipeline, model architecture, and betting utility assessment

---

## Executive Summary

This repository is a **college football prediction system** built on the College Football Data API, featuring ML-based win prediction, point spread forecasting, over/under modeling, and rudimentary edge detection against Vegas lines. It is a **solid foundation** with clean architecture and working automation, but in its current state it is a **research-grade prototype**, not a production betting engine. The model's ~59% ATS-equivalent accuracy and lack of historical P&L tracking mean it cannot yet demonstrate positive expected value. With targeted improvements — particularly around model sophistication, calibration, bankroll management, and backtesting infrastructure — this platform could become a serious competitive tool.

**Current Estimated Value (as-is):** $15,000–$30,000 (development time savings + data pipeline)
**Projected Value (after roadmap):** $150,000–$500,000+ annually in operational value, depending on bankroll size and edge realization

---

## 1. Current State Assessment

### 1.1 What Works Well

| Component | Assessment | Detail |
|-----------|-----------|--------|
| **Data Pipeline** | Strong | Robust API client with retry logic, 20+ years of historical data, EPA/advanced stats integration |
| **Feature Engineering** | Good | 81+ features including EPA, havoc, talent ratings, situational splits |
| **Code Quality** | Good | Clean Python, input validation, error handling, logging |
| **Automation** | Strong | GitHub Actions runs predictions every Saturday at 8 AM UTC automatically |
| **Output Formats** | Strong | JSON, CSV, text — ready for downstream consumption |
| **Documentation** | Good | 17+ docs, usage guides, security practices |
| **Testing** | Adequate | 5 test files, core functionality covered |
| **Props System** | Promising | Spread, total, and team point predictions with confidence intervals |

### 1.2 Critical Weaknesses for Gambling Use

| Weakness | Severity | Detail |
|----------|----------|--------|
| **Model Accuracy** | HIGH | 59% win prediction accuracy is near coin-flip; insufficient edge for profitable betting |
| **No Backtesting Framework** | HIGH | No historical P&L tracking, no paper trading, no way to validate if the model has ever been profitable |
| **No Bankroll Management** | HIGH | No Kelly Criterion, no unit sizing, no risk management — a dealbreaker for any serious operation |
| **No Line Movement Analysis** | MEDIUM | Only uses consensus close; ignores opening lines, steam moves, and sharp action |
| **Naive Edge Detection** | MEDIUM | Fixed 2.0-point threshold is arbitrary; no statistical significance testing on edges |
| **No Calibration Validation** | MEDIUM | Brier score calculated but not used to adjust predictions; probabilities may be poorly calibrated |
| **Simple Models** | MEDIUM | Random Forest/Gradient Boosting are reasonable but outdated vs. modern approaches (neural nets, ensemble stacking) |
| **No Market-Adjusted Features** | MEDIUM | Doesn't incorporate closing line value (CLV), market consensus, or reverse line movement |
| **No Live/In-Game** | LOW | Pregame only — no in-game model or live betting capability |
| **Flat Code Structure** | LOW | 24 Python files at root; needs packaging for scale |

### 1.3 Model Performance Deep Dive

```
Win Prediction (Classification):
  Training Accuracy:     63-65%
  Test Accuracy:         59-60%
  Cross-Validation:      59% ±1.6%

  VERDICT: Insufficient for profitable ATS betting.
  Industry benchmark: need 52.4%+ ATS to overcome -110 vig.
  This model predicts winners, NOT against-the-spread.

Props Prediction (Regression):
  Team Points MAE:       ~7-8 points
  Game Total MAE:        ~14-15 points
  Spread MAE:            Not explicitly tracked

  VERDICT: MAE of 7-8 points per team is too noisy for
  consistent edge. Professional models target MAE < 5.

Top Features by Importance:
  1. yards_diff          28.3%  (yardage differential)
  2. home_off_yards      14.5%
  3. away_off_yards      13.6%
  4. home_passing_yards  11.8%
  5. home_rushing_yards  11.7%

  CONCERN: Heavy reliance on raw yardage stats.
  Missing: tempo adjustment, garbage time filtering,
  opponent-strength adjustment, recency weighting.
```

---

## 2. Improvement Roadmap

### Phase 1: Foundation (Weeks 1-4) — Make It Trustworthy

**Goal:** Build backtesting infrastructure and validate whether the model has ANY edge.

| Task | Priority | Effort |
|------|----------|--------|
| Build backtesting engine with historical season-by-season P&L | P0 | 3 days |
| Implement Closing Line Value (CLV) tracking | P0 | 2 days |
| Add proper ATS (against-the-spread) prediction mode | P0 | 2 days |
| Implement probability calibration (Platt scaling / isotonic regression) | P0 | 1 day |
| Add Kelly Criterion / fractional Kelly bankroll sizing | P0 | 1 day |
| Restructure code into proper Python package (src/ layout) | P1 | 2 days |
| Add comprehensive logging with prediction audit trail | P1 | 1 day |

**Deliverable:** A backtesting report showing historical ATS performance, CLV capture, and simulated bankroll growth/decline across 5+ seasons.

### Phase 2: Model Upgrade (Weeks 5-10) — Make It Accurate

**Goal:** Achieve 54%+ ATS accuracy with well-calibrated probabilities.

| Task | Priority | Effort |
|------|----------|--------|
| Implement power ratings model (Elo + margin-adjusted) | P0 | 3 days |
| Add tempo-adjusted efficiency metrics (points per play, not per game) | P0 | 2 days |
| Garbage time filtering (exclude non-competitive game states) | P0 | 2 days |
| Opponent-strength-adjusted stats (SOS-weighted features) | P0 | 2 days |
| Recency weighting (exponential decay on older games) | P0 | 1 day |
| Implement stacked ensemble (RF + XGB + LightGBM + neural net) | P1 | 5 days |
| Add player-level features (injuries, transfers, QB ratings) | P1 | 5 days |
| Weather and venue features | P2 | 2 days |
| Rivalry / motivation features | P2 | 1 day |
| Monte Carlo game simulation (10,000+ iterations) | P1 | 3 days |

**Deliverable:** Model achieving 54%+ ATS on out-of-sample backtests with calibrated probabilities (Brier score < 0.24).

### Phase 3: Market Integration (Weeks 11-14) — Make It Profitable

**Goal:** Integrate real-time odds, automate edge detection, and implement proper risk management.

| Task | Priority | Effort |
|------|----------|--------|
| Multi-book odds integration (DraftKings, FanDuel, BetMGM, Pinnacle) | P0 | 3 days |
| Opening-to-closing line movement tracking | P0 | 2 days |
| Sharp vs. public money indicators | P1 | 2 days |
| Automated edge alerts (email/Slack/Discord) | P1 | 2 days |
| Position sizing engine (Kelly + max exposure limits) | P0 | 2 days |
| Correlation-aware portfolio management (parlay/teaser analysis) | P1 | 3 days |
| Dashboard with real-time P&L, ROI, and edge tracking | P1 | 5 days |
| Steam move detection and rapid-fire bet triggering | P2 | 3 days |

**Deliverable:** An automated system that ingests odds from multiple books, identifies +EV opportunities, sizes bets appropriately, and tracks performance in real-time.

### Phase 4: Scale & Diversify (Weeks 15-20) — Make It a Business

**Goal:** Expand to additional markets and build operational resilience.

| Task | Priority | Effort |
|------|----------|--------|
| NFL model (transfer learning from CFB features) | P1 | 5 days |
| First-half / second-half spread models | P1 | 3 days |
| Player prop models (passing yards, rushing yards, TDs) | P1 | 5 days |
| Live/in-game model with play-by-play ingestion | P2 | 10 days |
| API service layer (FastAPI) for internal consumption | P1 | 3 days |
| Database backend (PostgreSQL) replacing CSV files | P0 | 3 days |
| Automated model retraining and drift detection | P1 | 3 days |
| A/B testing framework for model variants | P2 | 3 days |

---

## 3. Value Assessment

### Current Value (As-Is)

| Component | Value Estimate | Rationale |
|-----------|---------------|-----------|
| Data pipeline & API integration | $8,000-$12,000 | 2-3 weeks of senior dev time saved |
| Feature engineering & preprocessing | $5,000-$8,000 | Domain knowledge embedded in code |
| ML model infrastructure | $3,000-$5,000 | Training, evaluation, persistence framework |
| Automation (CI/CD) | $2,000-$3,000 | GitHub Actions workflow, artifact management |
| Documentation & tests | $2,000-$3,000 | Onboarding time reduction |
| **Total As-Is** | **$15,000-$30,000** | Development time savings only |

**Important caveat:** The model in its current form has **no demonstrated positive expected value** for betting purposes. The 59% straight-up accuracy does not translate to ATS profitability. The value above reflects engineering effort, not betting edge.

### Projected Value (Post-Roadmap)

| Scenario | Assumptions | Annual Value |
|----------|-------------|--------------|
| **Conservative** | 54% ATS, $100/unit, 200 bets/season, flat betting | $3,600 net profit/year |
| **Moderate** | 55% ATS, $500/unit, 300 bets/season, Kelly sizing | $45,000-$75,000/year |
| **Aggressive** | 56%+ ATS, $1,000+ units, 400+ bets, multi-sport | $150,000-$500,000/year |
| **Platform Value** | Licensing model to other syndicates/touts | $200,000-$1M+ (one-time + recurring) |

**Key insight:** At professional scale ($1,000+ units), even a 1% edge improvement is worth $50,000+/year. The roadmap targets 54-56% ATS which, if achieved, creates significant value.

### Break-Even Analysis

```
Current vig at -110: Need 52.38% to break even
Phase 2 target:      54-56% ATS accuracy
Edge at 54%:         1.62% per bet
Edge at 56%:         3.62% per bet

At $500/unit, 300 bets/season:
  54% ATS → ~$7,500 expected profit
  55% ATS → ~$15,000 expected profit
  56% ATS → ~$22,500 expected profit

ROI on roadmap development ($50K-$80K):
  Payback period: 1-3 seasons at moderate scale
```

---

## 4. Risk Factors

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Model doesn't achieve 54%+ ATS | Medium | Fatal | Extensive backtesting before live deployment |
| API data source discontinuation | Low | High | Cache historical data, build scraping fallbacks |
| Market efficiency erodes edge | Medium | High | Continuous model retraining, feature innovation |
| Regulatory changes | Medium | Medium | Operate in legal jurisdictions only |
| Bankroll ruin from variance | Medium | High | Fractional Kelly, max exposure limits, stop-losses |
| Overfitting to historical data | High | High | Strict out-of-sample validation, walk-forward testing |

---

## 5. Final Recommendation

**BUY with conditions.** The codebase is a legitimate, well-engineered foundation that would cost $15K-$30K to recreate from scratch. However, it is **not ready for live betting** in its current form.

**Conditions for acquisition:**
1. Negotiate price at asset value ($15K-$30K), not projected value
2. Budget $50K-$80K for Phase 1-3 development (hire 1-2 quant developers for 3-5 months)
3. Do not deploy capital until backtesting demonstrates 53%+ ATS over 3+ out-of-sample seasons
4. Start with paper trading for one full season before live deployment

**The opportunity is real** — CFB markets are less efficient than NFL, the data infrastructure here is solid, and the feature set covers the right statistical domains. But the current model is a starting point, not a finished product. The value is in the platform, not the predictions.

---

*This evaluation is based on a complete code review of 24 Python source files (~5,000 lines), 5 test files, 17 documentation files, data pipelines, and model outputs. All assessments reflect the codebase as of the evaluation date.*
