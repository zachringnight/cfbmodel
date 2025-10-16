# Security Best Practices

## ⚠️ CRITICAL: API Key Security

### Never Hardcode API Keys

**DO NOT** hardcode your API key in any file, including:
- Source code files (`.py`, `.js`, etc.)
- Configuration files
- Workflow files (`.yml`)
- Documentation files
- Comments or commit messages

### ❌ WRONG - Hardcoded API Key
```python
# NEVER DO THIS!
api_key = "your_actual_api_key_here"
fetcher = CFBDataFetcher(api_key)
```

```yaml
# NEVER DO THIS!
env:
  CFB_API_KEY: "your_actual_api_key_here"
```

### ✅ CORRECT - Using GitHub Secrets

**Workflow (already implemented):**
```yaml
env:
  CFB_API_KEY: ${{ secrets.CFB_API_KEY }}
```

**Python script (already implemented):**
```python
import os
api_key = os.environ.get("CFB_API_KEY")
```

## How This Workflow Securely Uses API Keys

### 1. GitHub Secrets Storage
The API key is stored securely in GitHub Secrets:
- Encrypted at rest
- Not visible in logs or workflow runs
- Only accessible to workflow jobs
- Can be rotated without changing code

### 2. Environment Variables
The workflow passes the secret as an environment variable:
```yaml
- name: Run model training and predictions
  env:
    CFB_API_KEY: ${{ secrets.CFB_API_KEY }}
  run: |
    python run_predictions_with_outputs.py --train --train-year 2024
```

### 3. Runtime Access
The Python script reads the key from environment variables:
```python
parser.add_argument(
    "--api-key",
    help="College Football Data API key (or set CFB_API_KEY env var)",
    default=os.environ.get("CFB_API_KEY")
)
```

## Setting Up Your API Key (Secure Method)

### Step 1: Get an API Key
1. Visit https://collegefootballdata.com/
2. Create an account or sign in
3. Generate an API key from your account settings

### Step 2: Add as GitHub Secret
1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `CFB_API_KEY`
5. Value: Paste your API key
6. Click **Add secret**

### Step 3: Verify Setup
The workflow will now have access to your API key securely without it ever being exposed in code or logs.

## 🚨 If Your API Key Was Exposed

If you accidentally exposed your API key in:
- Code commits
- Pull request comments
- Issue discussions
- Public documentation

**Take these steps immediately:**

1. **Revoke the exposed key**
   - Go to https://collegefootballdata.com/
   - Navigate to your API keys settings
   - Revoke/delete the exposed key

2. **Generate a new key**
   - Create a new API key in your account
   - Follow the secure setup steps above

3. **Update the GitHub Secret**
   - Go to Settings → Secrets and variables → Actions
   - Click on `CFB_API_KEY`
   - Click **Update secret**
   - Enter your new API key

4. **Clean up exposure**
   - If exposed in commits: Consider rewriting git history (advanced)
   - If exposed in comments: Delete the comment if possible
   - If exposed in PRs: Close and create a new PR without the key

## Local Development Security

### Using Environment Variables
```bash
# Set temporarily for current session
export CFB_API_KEY="your_api_key_here"

# Or use .env file (add to .gitignore!)
echo "CFB_API_KEY=your_api_key_here" > .env
```

### .gitignore Protection
Ensure `.env` files are in `.gitignore`:
```
# Already included in .gitignore
.env
.venv
env/
venv/
```

## Additional Security Measures

### 1. Least Privilege
- Only grant API keys the minimum necessary permissions
- Use read-only keys when possible

### 2. Key Rotation
- Periodically rotate API keys (e.g., every 90 days)
- Update the GitHub Secret with the new key

### 3. Audit Access
- Monitor who has access to repository secrets
- Review workflow runs for suspicious activity

### 4. Separate Keys for Different Environments
- Use different API keys for:
  - Development/testing
  - Production workflows
  - Different team members (if supported)

## Monitoring and Alerts

### Check for Exposed Secrets
GitHub will automatically scan for exposed secrets and alert you. Enable:
1. Settings → Code security and analysis
2. Enable **Secret scanning**
3. Enable **Push protection**

### Rate Limiting
Monitor your API usage:
- Check API rate limits regularly
- Set up alerts for unusual activity
- Implement request throttling if needed

## Summary

✅ **DO:**
- Store API keys in GitHub Secrets
- Use environment variables
- Rotate keys periodically
- Monitor for exposed secrets

❌ **DON'T:**
- Hardcode API keys in code
- Commit keys to git
- Share keys in comments or issues
- Use production keys for testing

## Questions?

If you have questions about API key security:
1. Review GitHub's secret management documentation
2. Check the College Football Data API documentation
3. Consult your organization's security policies

**Remember: Once a key is exposed publicly, it must be revoked immediately.**
