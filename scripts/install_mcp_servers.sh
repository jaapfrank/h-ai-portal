#!/bin/bash

echo "=' Installing MCP Servers for Hoeflon AI Portal Testing"
echo "======================================================"

# Navigate to home directory for user-level installation
cd ~

# Create MCP directory structure
mkdir -p ~/.mcp/servers
mkdir -p ~/.mcp/logs

echo "=æ Installing Core MCP Servers..."

# Install Puppeteer MCP for frontend testing
echo "Installing Puppeteer MCP..."
npm install -g @modelcontextprotocol/server-puppeteer

# Install Sequential Thinking MCP
echo "Installing Sequential Thinking MCP..."
npm install -g @modelcontextprotocol/server-sequential-thinking

# Install Filesystem MCP
echo "Installing Filesystem MCP..."
npm install -g @modelcontextprotocol/server-filesystem

# Install Fetch MCP
echo "Installing Fetch MCP..."
npm install -g @kazuph/mcp-fetch

# Install Browser Tools MCP
echo "Installing Browser Tools MCP..."
npm install -g @agentdeskai/browser-tools-mcp@1.2.1

echo ">ê Installing Testing-specific MCP Servers..."

# Install Testing MCP servers
echo "Installing Testing MCP..."
npm install -g @modelcontextprotocol/server-everything

# Install Memory MCP
echo "Installing Memory MCP..."
npm install -g @modelcontextprotocol/server-memory

# Install Time MCP
echo "Installing Time MCP..."
npm install -g @modelcontextprotocol/server-time

echo "= Installing Development MCP Servers..."

# Install PostgreSQL MCP for database testing
echo "Installing PostgreSQL MCP..."
npm install -g @modelcontextprotocol/server-postgres

# Install SQLite MCP for local testing
echo "Installing SQLite MCP..."
npm install -g @modelcontextprotocol/server-sqlite

echo " MCP Server Installation Complete!"
echo "======================================"

# Verify installations
echo "= Verifying MCP Server Installations..."
echo "----------------------------------------"

# Test each server
servers=(
    "@modelcontextprotocol/server-puppeteer"
    "@modelcontextprotocol/server-sequential-thinking"
    "@modelcontextprotocol/server-filesystem"
    "@kazuph/mcp-fetch"
    "@agentdeskai/browser-tools-mcp"
    "@modelcontextprotocol/server-everything"
    "@modelcontextprotocol/server-memory"
    "@modelcontextprotocol/server-time"
    "@modelcontextprotocol/server-postgres"
    "@modelcontextprotocol/server-sqlite"
)

for server in "${servers[@]}"; do
    echo -n "Testing $server... "
    if npm list -g $server > /dev/null 2>&1; then
        echo " Installed"
    else
        echo "L Failed"
    fi
done

echo ""
echo "<¯ MCP Configuration Tips:"
echo "========================="
echo "1. Update your Claude Desktop settings to use these servers"
echo "2. MCP servers are installed globally with npm"
echo "3. Logs can be found in ~/.mcp/logs/"
echo "4. Server configs should be in your Claude Desktop settings"

echo ""
echo "=€ Ready for comprehensive testing!"