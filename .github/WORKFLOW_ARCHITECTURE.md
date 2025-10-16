# Workflow Architecture

## Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     GitHub Actions Trigger                       │
│                                                                   │
│  • Every Saturday at 8 AM UTC (Scheduled)                        │
│  • Manual trigger with parameters (On-Demand)                    │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Setup Environment                                │
│                                                                   │
│  1. Checkout repository                                          │
│  2. Setup Python 3.11                                            │
│  3. Install dependencies (cached)                                │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│              Run Model Training & Predictions                     │
│                                                                   │
│  Script: run_predictions_with_outputs.py                         │
│                                                                   │
│  Steps:                                                          │
│  1. Train model on previous year's data                          │
│  2. Fetch current week's games                                   │
│  3. Generate predictions                                         │
│  4. Calculate confidence scores                                  │
│  5. Save outputs (JSON, CSV, logs)                              │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Generate Summary Report                         │
│                                                                   │
│  • Extract key metrics                                           │
│  • Format results as markdown                                    │
│  • Display in GitHub Actions UI                                  │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Upload Artifacts                              │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  predictions-output-{run_number}  (30 days)             │   │
│  │  • predictions_output.txt                                │   │
│  │  • summary.md                                            │   │
│  │  • exit_code.txt                                         │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  trained-model-{run_number}  (90 days)                  │   │
│  │  • cfb_model.pkl                                         │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  predictions-data-{run_number}  (30 days)               │   │
│  │  • predictions_YYYYMMDD_HHMMSS.json                      │   │
│  │  • predictions_YYYYMMDD_HHMMSS.csv                       │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Artifacts Available                            │
│                                                                   │
│  Users can download from:                                        │
│  • GitHub Actions UI                                             │
│  • GitHub API                                                    │
│  • Command line tools                                            │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

```
┌──────────────┐
│   API Key    │──────┐
│  (Secret)    │      │
└──────────────┘      │
                      ▼
┌──────────────┐   ┌─────────────────────────┐   ┌──────────────┐
│ Training     │──▶│  run_predictions_with_  │──▶│ Predictions  │
│ Data (API)   │   │      outputs.py         │   │   (Games)    │
└──────────────┘   └─────────────────────────┘   └──────────────┘
                            │
                            ▼
                   ┌─────────────────┐
                   │  ML Model       │
                   │  Training       │
                   └────────┬────────┘
                            │
                ┌───────────┼───────────┐
                ▼           ▼           ▼
         ┌──────────┐ ┌──────────┐ ┌──────────┐
         │   JSON   │ │   CSV    │ │  Model   │
         │  Output  │ │  Output  │ │   File   │
         └──────────┘ └──────────┘ └──────────┘
                │           │           │
                └───────────┼───────────┘
                            ▼
                   ┌─────────────────┐
                   │   Artifacts     │
                   │  (Download)     │
                   └─────────────────┘
```

## Component Interaction

```
┌────────────────────────────────────────────────────────────────┐
│                      GitHub Repository                          │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  .github/workflows/run-model.yml                         │  │
│  │  • Defines workflow triggers and steps                   │  │
│  │  • Manages environment setup                             │  │
│  │  • Orchestrates artifact uploads                         │  │
│  └────────────────────┬─────────────────────────────────────┘  │
│                       │                                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  run_predictions_with_outputs.py                         │  │
│  │  • Trains model                                          │  │
│  │  • Generates predictions                                 │  │
│  │  • Creates JSON/CSV outputs                              │  │
│  └────────────────────┬─────────────────────────────────────┘  │
│                       │                                          │
│  ┌────────────┬──────────────┬──────────────────┐             │
│  │            │              │                  │             │
│  ▼            ▼              ▼                  ▼             │
│  ┌──────┐  ┌──────┐  ┌──────────┐  ┌───────────────┐        │
│  │ data_│  │ pre  │  │  model   │  │    config     │        │
│  │fetcher│  │proces│  │          │  │               │        │
│  │ .py  │  │sor.py│  │   .py    │  │      .py      │        │
│  └──────┘  └──────┘  └──────────┘  └───────────────┘        │
│                                                                  │
└────────────────────────────────────────────────────────────────┘
           │
           ▼
┌────────────────────────────────────────────────────────────────┐
│                   College Football Data API                     │
│                  https://collegefootballdata.com                │
└────────────────────────────────────────────────────────────────┘
```

## Usage Patterns

### Pattern 1: Scheduled Execution
```
Saturday 8 AM UTC
    ↓
Workflow Triggered Automatically
    ↓
Model Runs with Default Parameters
    ↓
Artifacts Available for Download
```

### Pattern 2: Manual Execution
```
User Opens GitHub Actions Tab
    ↓
Clicks "Run workflow"
    ↓
Optionally Customizes Parameters
    ↓
Model Runs with Custom Configuration
    ↓
Artifacts Available for Download
```

### Pattern 3: Local Development
```
Developer Clones Repository
    ↓
Sets CFB_API_KEY Environment Variable
    ↓
Runs: python run_predictions_with_outputs.py
    ↓
Outputs Saved Locally (JSON/CSV)
```

## Error Handling Flow

```
┌─────────────┐
│ Workflow    │
│  Starts     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Check API   │     No      ┌──────────────┐
│ Key Exists? │────────────▶│ Exit with    │
└──────┬──────┘             │ Error Message│
       │ Yes                └──────────────┘
       ▼
┌─────────────┐
│ Fetch Data  │     Error   ┌──────────────┐
│ from API    │────────────▶│ Log Error &  │
└──────┬──────┘             │ Upload Logs  │
       │ Success            └──────────────┘
       ▼
┌─────────────┐
│ Train Model │     Error   ┌──────────────┐
│             │────────────▶│ Log Error &  │
└──────┬──────┘             │ Upload Logs  │
       │ Success            └──────────────┘
       ▼
┌─────────────┐
│ Generate    │     Error   ┌──────────────┐
│ Predictions │────────────▶│ Log Error &  │
└──────┬──────┘             │ Upload Logs  │
       │ Success            └──────────────┘
       ▼
┌─────────────┐
│ Upload      │
│ Artifacts   │
└─────────────┘
```

## File Dependencies

```
run-model.yml
    │
    ├─▶ run_predictions_with_outputs.py
    │       │
    │       ├─▶ data_fetcher.py
    │       │       └─▶ config.py
    │       │
    │       ├─▶ preprocessor.py
    │       │
    │       └─▶ model.py
    │               └─▶ config.py
    │
    └─▶ requirements.txt
```

## Output Structure

```
Workflow Run #123
│
├─▶ predictions-output-123/
│   ├── predictions_output.txt      (Full console log)
│   ├── summary.md                  (Summary report)
│   └── exit_code.txt               (Exit status)
│
├─▶ trained-model-123/
│   └── cfb_model.pkl               (Trained model)
│
└─▶ predictions-data-123/
    ├── predictions_20251016_120000.json
    └── predictions_20251016_120000.csv
```
