#!/bin/bash

# =============================================================================
# MCP SERVERS INSTALLATION SCRIPT
# =============================================================================
# This script installs the requested MCP (Model Context Protocol) servers:
# - Filesystem: File system access and manipulation
# - Memory: Knowledge graph-based persistent memory
# - Puppeteer: Browser automation and web interaction
# - SQLite: Database operations and queries
# - Perplexity: Web search using Perplexity AI API
# - Git: Git repository operations
# - GitHub: GitHub repository management and API integration
# - Sequential Thinking: Dynamic problem-solving through structured thinking
# =============================================================================

echo "🚀 Starting MCP Servers Installation..."
echo "==============================================="

# Function to check if a command was successful
check_success() {
    if [ $? -eq 0 ]; then
        echo "✅ $1 - SUCCESS"
    else
        echo "❌ $1 - FAILED"
        exit 1
    fi
}

# Function to install MCP server via Claude Code
install_claude_mcp() {
    local name=$1
    local command=$2
    echo "📦 Installing $name..."
    eval "$command"
    check_success "$name installation"
}

# Check if Claude Code is installed
echo "🔍 Checking Claude Code installation..."
if ! command -v claude &> /dev/null; then
    echo "❌ Claude Code is not installed or not in PATH"
    echo "Please install Claude Code first: https://docs.anthropic.com/en/docs/claude-code"
    exit 1
fi
echo "✅ Claude Code found"

# Install MCP Servers
echo ""
echo "📥 Installing MCP Servers..."
echo "==============================================="

# 1. Sequential Thinking Server
install_claude_mcp "Sequential Thinking" "claude mcp add sequential-thinking -s user -- npx -y @modelcontextprotocol/server-sequential-thinking"

# 2. Filesystem Server (with common directories)
install_claude_mcp "Filesystem" "claude mcp add filesystem -s user -- npx -y @modelcontextprotocol/server-filesystem ~/Documents ~/Desktop ~/Downloads ~/Projects"

# 3. Memory Server
install_claude_mcp "Memory" "claude mcp add memory -s user -- npx -y @modelcontextprotocol/server-memory"

# 4. Puppeteer Server
install_claude_mcp "Puppeteer" "claude mcp add puppeteer -s user -- npx -y @modelcontextprotocol/server-puppeteer"

# 5. SQLite Server (using uvx)
install_claude_mcp "SQLite" "claude mcp add sqlite -s user -- uvx mcp-server-sqlite --db-path ./database.db"

# 6. Git Server (using uvx)
install_claude_mcp "Git" "claude mcp add git -s user -- uvx mcp-server-git --repository ."

# 7. GitHub Server (requires GitHub token)
echo "📦 Installing GitHub Server..."
echo "⚠️  GitHub server requires a personal access token"
echo "Please set your GITHUB_PERSONAL_ACCESS_TOKEN environment variable"
echo "You can create a token at: https://github.com/settings/tokens"
claude mcp add github -s user -- npx -y @modelcontextprotocol/server-github
check_success "GitHub Server installation"

# 8. Perplexity Server (using community implementation)
echo "📦 Installing Perplexity Server..."
echo "⚠️  Perplexity server requires a Perplexity API key"
echo "Please sign up at: https://docs.perplexity.ai/docs/getting-started"
claude mcp add perplexity -s user -- npx -y server-perplexity-ask
check_success "Perplexity Server installation"

echo ""
echo "🎉 MCP Servers Installation Complete!"
echo "==============================================="

# Verify installations
echo "🔍 Verifying installations..."
claude mcp list

echo ""
echo "📋 Next Steps:"
echo "==============================================="
echo "1. Set up API keys for GitHub and Perplexity servers:"
echo "   - GitHub: export GITHUB_PERSONAL_ACCESS_TOKEN=your_token_here"
echo "   - Perplexity: export PERPLEXITY_API_KEY=your_key_here"
echo ""
echo "2. Test your MCP servers:"
echo "   - Run: claude mcp list"
echo "   - Use: /mcp in Claude Code to check connection status"
echo ""
echo "3. Configure directories for filesystem server if needed:"
echo "   - Current directories: ~/Documents ~/Desktop ~/Downloads ~/Projects"
echo "   - Modify the script to add more directories as needed"
echo ""
echo "4. For SQLite server, create your database file:"
echo "   - Default path: ./database.db"
echo "   - Modify the --db-path parameter as needed"
echo ""
echo "5. For Git server, ensure you're in a git repository:"
echo "   - Current setting: . (current directory)"
echo "   - Modify --repository parameter to point to your git repo"
echo ""
echo "🎯 All servers are now installed and ready to use!"
echo "Check the documentation for each server's specific capabilities."