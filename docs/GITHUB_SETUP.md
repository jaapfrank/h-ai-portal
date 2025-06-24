# GitHub Repository Setup Instructions

## Manual Repository Creation

Since GitHub CLI authentication isn't working, please follow these steps to create the repository manually:

### Step 1: Create Repository on GitHub.com
1. Go to https://github.com/new
2. Set Repository name: `hoeflon-ai-portaal`
3. Set Description: `Hoeflon AI Portal - AI-powered ERP chatbot for business intelligence`
4. Choose **Public** (or Private as you prefer)
5. **DO NOT** initialize with README, .gitignore, or license (we already have these)
6. Click "Create repository"

### Step 2: Add Remote and Push
After creating the repository, run these commands in your terminal:

```bash
# Navigate to your project directory
cd "/home/jaapfrank/Projecten/Hoeflon Ridder/Ridder AI"

# Add the GitHub repository as remote origin
git remote add origin https://github.com/jaapfrank/hoeflon-ai-portaal.git

# Push your code to GitHub
git push -u origin master
```

### Step 3: Verify Upload
1. Go to https://github.com/jaapfrank/hoeflon-ai-portaal
2. Verify all your files are uploaded
3. Check that the README and project structure are visible

## Alternative: Use Personal Access Token

If you prefer to use the CLI with authentication:

1. Go to GitHub Settings > Developer settings > Personal access tokens > Tokens (classic)
2. Generate a new token with `repo` scope
3. Set environment variable: `export GH_TOKEN=your_token_here`
4. Run: `gh repo create hoeflon-ai-portaal --public --push --source .`

## Project Structure

Your repository will contain:
- `backend/` - FastAPI backend with AI routing
- `agents/` - AutoGen agent orchestration system
- `tests/` - Test suite for all components
- `react-frontend/` - React.js frontend interface
- `.gitignore` - Comprehensive ignore rules
- `requirements.txt` - Python dependencies

## Next Steps

Once the repository is created:
1. Set up GitHub Actions for CI/CD
2. Add issue templates
3. Create project documentation
4. Set up deployment workflows