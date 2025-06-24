# MCP Servers Installation Guide

## 🎯 Quick Installation

Run the installation script:
```bash
./install_mcp_servers.sh
```

## 📋 Installed MCP Servers

### 1. **Sequential Thinking** 🧠
- **Purpose**: Dynamic problem-solving through structured thinking
- **Command**: `@modelcontextprotocol/server-sequential-thinking`
- **Usage**: Helps break down complex problems into manageable steps

### 2. **Filesystem** 📁
- **Purpose**: File system access and manipulation
- **Command**: `@modelcontextprotocol/server-filesystem`
- **Directories**: `~/Documents ~/Desktop ~/Downloads ~/Projects`
- **Usage**: Read, write, and manipulate files in specified directories

### 3. **Memory** 🧠
- **Purpose**: Knowledge graph-based persistent memory
- **Command**: `@modelcontextprotocol/server-memory`
- **Usage**: Persistent storage and retrieval of information

### 4. **Puppeteer** 🌐
- **Purpose**: Browser automation and web interaction
- **Command**: `@modelcontextprotocol/server-puppeteer`
- **Usage**: Navigate websites, take screenshots, interact with web pages

### 5. **SQLite** 🗄️
- **Purpose**: Database operations and queries
- **Command**: `uvx mcp-server-sqlite --db-path ./database.db`
- **Usage**: Execute SQL queries on SQLite databases

### 6. **Git** 🔄
- **Purpose**: Git repository operations
- **Command**: `uvx mcp-server-git --repository .`
- **Usage**: Read, search, and manipulate Git repositories

### 7. **GitHub** 🐙
- **Purpose**: GitHub repository management and API integration
- **Command**: `@modelcontextprotocol/server-github`
- **Requirement**: `GITHUB_PERSONAL_ACCESS_TOKEN` environment variable
- **Usage**: File operations, repository management, search functionality

### 8. **Perplexity** 🔍
- **Purpose**: Web search using Perplexity AI API
- **Command**: `server-perplexity-ask`
- **Requirement**: `PERPLEXITY_API_KEY` environment variable
- **Usage**: Real-time web search and research capabilities

## 🔑 API Keys Setup

### GitHub Personal Access Token
1. Go to: https://github.com/settings/tokens
2. Generate a new token with appropriate permissions
3. Set environment variable:
   ```bash
   export GITHUB_PERSONAL_ACCESS_TOKEN=your_token_here
   ```

### Perplexity API Key
1. Sign up at: https://docs.perplexity.ai/docs/getting-started
2. Get your API key from the developer dashboard
3. Set environment variable:
   ```bash
   export PERPLEXITY_API_KEY=your_key_here
   ```

## 🧪 Testing Your Installation

### Verify MCP Servers
```bash
claude mcp list
```

### Check Connection Status
Use `/mcp` command in Claude Code to check connection status

### Test Individual Servers
Each server provides different capabilities that you can test through Claude Code:

- **Sequential Thinking**: Ask for help breaking down complex problems
- **Filesystem**: Request file operations in your configured directories
- **Memory**: Store and retrieve information across sessions
- **Puppeteer**: Ask for web automation tasks
- **SQLite**: Query databases you've configured
- **Git**: Request git repository information
- **GitHub**: Ask for GitHub repository operations
- **Perplexity**: Request web search and research

## 🛠️ Customization

### Adding More Directories to Filesystem Server
Edit the installation script and modify this line:
```bash
claude mcp add filesystem -s user -- npx -y @modelcontextprotocol/server-filesystem ~/Documents ~/Desktop ~/Downloads ~/Projects ~/YourNewDirectory
```

### Changing SQLite Database Path
Modify the SQLite installation command:
```bash
claude mcp add sqlite -s user -- uvx mcp-server-sqlite --db-path /path/to/your/database.db
```

### Setting Different Git Repository
Change the Git server repository path:
```bash
claude mcp add git -s user -- uvx mcp-server-git --repository /path/to/your/repo
```

## 🔧 Troubleshooting

### Common Issues
1. **Command not found**: Ensure Claude Code is installed and in your PATH
2. **Permission denied**: Run `chmod +x install_mcp_servers.sh`
3. **NPX errors**: Ensure Node.js and npm are installed
4. **UVX errors**: Install uvx with `pip install uvx`

### Windows Users
For Windows, you may need to add `cmd /c` before npx commands:
```bash
claude mcp add filesystem -s user -- cmd /c npx -y @modelcontextprotocol/server-filesystem
```

### Timeout Issues
If you experience timeout issues, increase the timeout:
```bash
MCP_TIMEOUT=10000 claude
```

## 📚 Documentation Links

- [Model Context Protocol Documentation](https://modelcontextprotocol.io/)
- [Claude Code MCP Documentation](https://docs.anthropic.com/en/docs/claude-code/mcp)
- [MCP Servers Repository](https://github.com/modelcontextprotocol/servers)
- [Awesome MCP Servers](https://github.com/punkpeye/awesome-mcp-servers)

## 🎉 Success!

You now have a comprehensive set of MCP servers installed that will greatly enhance Claude Code's capabilities. Each server provides unique functionality that can help with various development and automation tasks.