# Workflow API Key Handling Enhancement

## Summary

This update improves the `.github/workflows/run-model.yml` workflow to handle missing API keys gracefully, provide clear error messages, and allow users to provide API keys when manually running the workflow.

## Changes Made

### 1. Added Optional `api_key` Workflow Input

The workflow now accepts an optional `api_key` input when manually dispatched:

```yaml
workflow_dispatch:
  inputs:
    api_key:
      description: 'Optional: CFB API key to use for this run (will not be stored in repository).'
      required: false
      default: ''
```

This allows users to provide a temporary API key without storing it as a repository secret.

### 2. Added API Key Pre-Check Step

A new step "Check API key availability" runs before the model execution:

- **When API key is available** (from either secret or input):
  - Prints "✓ API key is available"
  - Writes `0` to `exit_code.txt`
  - Allows workflow to continue

- **When API key is missing**:
  - Prints clear, actionable error message
  - Creates `summary.md` with instructions on how to fix
  - Writes `1` to `exit_code.txt`
  - Displays summary in GitHub Actions UI
  - Exits with status 1 to stop the workflow early

This prevents the low-level script error and provides helpful guidance to repository maintainers.

### 3. Updated Environment Variable Logic

The "Run model training and predictions" step now sets the `CFB_API_KEY` environment variable with fallback logic:

```bash
if [ -n "${{ secrets.CFB_API_KEY }}" ]; then
  export CFB_API_KEY="${{ secrets.CFB_API_KEY }}"
elif [ -n "${{ github.event.inputs.api_key }}" ]; then
  export CFB_API_KEY="${{ github.event.inputs.api_key }}"
fi
```

**Priority order:**
1. Repository secret `CFB_API_KEY` (preferred)
2. Workflow input `api_key` (fallback)

### 4. Security Considerations

- API keys are never directly echoed to workflow logs
- Keys are only used as environment variables
- The workflow input is not stored in the repository
- Secret is preferred over manual input for security

## Testing

Created `test_workflow_api_key.py` to validate:

- ✓ Pre-check passes when secret is set
- ✓ Pre-check passes when workflow input is set
- ✓ Pre-check fails gracefully when no key is provided
- ✓ Secret is preferred over workflow input
- ✓ Workflow input is used as fallback
- ✓ Workflow YAML structure is correct
- ✓ No API key exposure in logs

All existing tests continue to pass.

## Benefits

### Before
- Workflow would fail with cryptic error: "Error: API key required. Set CFB_API_KEY environment variable or use --api-key"
- No clear guidance on how to fix
- Required repository administrator access to add secrets
- Failed late in the workflow (after installing dependencies)

### After
- Clear pre-check with actionable error messages
- Two options for providing API key:
  - **Option 1 (Recommended):** Add as repository secret
  - **Option 2:** Provide when manually running workflow
- Fails early with helpful summary in GitHub Actions UI
- Artifacts include instructions for fixing the issue
- All existing functionality preserved (timestamped outputs, artifacts, summary)

## Usage

### For Repository Owners

**Recommended:** Add `CFB_API_KEY` as a repository secret:
1. Go to: Settings > Secrets and variables > Actions
2. Click "New repository secret"
3. Name: `CFB_API_KEY`
4. Value: Your API key from https://collegefootballdata.com/

### For Manual Workflow Runs

When manually running the workflow:
1. Go to: Actions > Run CFB Model and Generate Predictions
2. Click "Run workflow"
3. Optionally enter your API key in the `api_key` field
4. Select other parameters (year, week, train_year) as needed
5. Click "Run workflow"

## Backward Compatibility

- Scheduled runs work exactly as before when secret is configured
- All existing parameters (year, week, train_year) remain unchanged
- Artifact upload behavior unchanged
- Summary generation unchanged
- Timestamp functionality unchanged

## Files Modified

- `.github/workflows/run-model.yml` - Enhanced workflow with API key handling
- `test_workflow_api_key.py` - New comprehensive test suite

## Notes

- The workflow does NOT modify or create repository secrets
- Repository administrators must add `CFB_API_KEY` via Settings > Secrets
- Workflow input is ephemeral and not stored
- API keys provided via workflow input are masked in logs by GitHub Actions
