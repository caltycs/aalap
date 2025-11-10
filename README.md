# Aalap 🎵

> An interactive command-line interface for Claude AI with MCP server support

Simply type `aalap` to enter an elegant, interactive terminal session with Claude AI. Have conversations, manage context, and integrate powerful MCP tools—all from your command line.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## ✨ Features

-  **Beautiful Interactive CLI** - Clean, intuitive interface with ASCII art
-  **Conversational Context** - Maintains conversation history throughout sessions
-  **MCP Server Support** - Install and manage Model Context Protocol servers
-  **Command History** - Navigate previous commands with arrow keys
-  **Quick Commands** - Slash commands for easy control
-  **Pipe Support** - Works seamlessly with Unix pipes and streams
-  **Persistent Config** - Saves your preferences and API keys securely

##  Installation

### Homebrew (Recommended for macOS/Linux)

```bash
# Add the Aalap tap
brew tap yourusername/aalap

# Install Aalap
brew install aalap

# Start using Aalap
aalap
```

### pip (All Platforms)

```bash
# Install from GitHub
pip install git+https://github.com/caltycs/aalap

# Or install with pipx (isolated environment)
pipx install git+https://github.com/caltycs/aalap
```

### Quick Install Script

```bash
# One-line install
curl -sSL https://raw.githubusercontent.com/yourusername/aalap/main/scripts/install.sh | bash
```

### From Source

```bash
# Clone the repository
git clone https://github.com/caltycs/aalap.git
cd aalap

# Install in development mode
pip install -e .

# Or build and install
python setup.py install
```

##  Quick Start

### 1. Get Your API Key

Get your Anthropic API key from [console.anthropic.com](https://console.anthropic.com/)

### 2. Configure Aalap

```bash
aalap config --api-key YOUR_ANTHROPIC_API_KEY
```

### 3. Launch Aalap

```bash
aalap
```

You'll see:

```
╔════════════════════════════════════════════════════════════════╗
║              Interactive Claude AI Terminal                    ║
╚════════════════════════════════════════════════════════════════╝

Type /help for commands or start chatting!

💬 You: 
```

##  Usage

### Interactive Mode (Default)

Simply type `aalap` to enter the interactive terminal:

```bash
aalap
```

Start chatting naturally with Claude. The conversation context is maintained throughout your session.

### Interactive Commands

| Command | Description |
|---------|-------------|
| `<message>` | Chat with Claude naturally |
| `/help` | Show all available commands |
| `/clear` | Clear conversation history |
| `/history` | View conversation history |
| `/config` | Show current configuration |
| `/config apikey <key>` | Set your API key |
| `/config model <model>` | Change Claude model |
| `/mcp list` | List installed MCP servers |
| `/mcp install <name> <cmd>` | Install an MCP server |
| `/mcp remove <name>` | Remove an MCP server |
| `/version` | Show Aalap version |
| `/exit` or `/quit` | Exit Aalap |

### Command-Line Mode

Use Aalap for quick one-off queries:

```bash
# Ask a quick question
aalap chat "Explain quantum entanglement"

# Pipe input from other commands
echo "def hello(): pass" | aalap chat "Review this Python code"

# With system prompt
aalap chat "Write a haiku" --system "You are a poet"

# View configuration
aalap config

# Check version
aalap --version
```

## 🔧 Configuration

### View Current Settings

```bash
aalap config
```

Or in interactive mode:
```
💬 You: /config
```

### Set API Key

**Command line:**
```bash
aalap config --api-key sk-ant-xxxxx
```

**Interactive mode:**
```
💬 You: /config apikey sk-ant-xxxxx
```

**Environment variable:**
```bash
export ANTHROPIC_API_KEY=sk-ant-xxxxx
```

### Change Model

```bash
# Command line
aalap config --model claude-sonnet-4-20250514

# Interactive mode
💬 You: /config model claude-sonnet-4-20250514
```

### Adjust Token Limit

```bash
aalap config --max-tokens 8192
```

##  MCP Server Management

Model Context Protocol (MCP) servers extend Claude's capabilities with tools and data sources.

### Installing MCP Servers

**Filesystem Access:**
```bash
aalap mcp install filesystem npx --args @modelcontextprotocol/server-filesystem ~/Documents
```

**GitHub Integration:**
```bash
aalap mcp install github npx --args @modelcontextprotocol/server-github \
  --env '{"GITHUB_TOKEN":"ghp_xxxxx"}'
```

**Database Access:**
```bash
aalap mcp install postgres npx --args @modelcontextprotocol/server-postgres \
  --env '{"DATABASE_URL":"postgresql://localhost/mydb"}'
```

**Web Search:**
```bash
aalap mcp install brave-search npx --args @modelcontextprotocol/server-brave-search \
  --env '{"BRAVE_API_KEY":"xxxxx"}'
```

### Managing Servers

```bash
# List all installed servers
aalap mcp list

# Remove a server
aalap mcp remove filesystem
```

### In Interactive Mode

```
💬 You: /mcp list
💬 You: /mcp install filesystem npx @modelcontextprotocol/server-filesystem ~/Documents
💬 You: /mcp remove filesystem
```

##  Examples

### Basic Conversation

```bash
$ aalap

💬 You: Hello! Can you help me with Python?

🤖 Claude is thinking...

Of course! I'd be happy to help you with Python. What would you like to know or work on?

💬 You: How do I read a CSV file?

🤖 Claude is thinking...

There are several ways to read CSV files in Python...
```

### Code Review

```bash
$ aalap

💬 You: Review this Python function

def calculate_fibonacci(n):
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

🤖 Claude is thinking...

This is a classic recursive Fibonacci implementation. Here are my observations:

1. Correctness: The logic is correct...
2. Performance: This has exponential time complexity...
3. Improvements: Consider using memoization...
```

### Contextual Conversations

```bash
💬 You: I'm building a REST API in Python

🤖 Claude is thinking...
Great! I can help you build a REST API. What framework are you considering?

💬 You: Should I use Flask or FastAPI?

🤖 Claude is thinking...
For a REST API, here's how Flask and FastAPI compare...

💬 You: Let's go with FastAPI. Show me a basic example

🤖 Claude is thinking...
Excellent choice! Here's a basic FastAPI example building on our discussion...
```

### Unix Integration

```bash
# Explain errors
python script.py 2>&1 | aalap chat "What's wrong with this code?"

# Generate commit messages
git diff --staged | aalap chat "Write a commit message for these changes"

# Analyze logs
tail -100 app.log | aalap chat "Summarize any errors or issues"

# Code review
cat myfile.py | aalap chat "Review this code for security vulnerabilities"

# Explain command output
ls -la | aalap chat "Explain these file permissions"
```

##  Configuration Files

Aalap stores its configuration in `~/.aalap/`:

```
~/.aalap/
├── config.json          # API key and settings
├── mcp_servers.json     # MCP server configurations
└── history              # Command history
```

### Configuration File Format

`~/.aalap/config.json`:
```json
{
  "api_key": "sk-ant-xxxxx",
  "model": "claude-sonnet-4-20250514",
  "max_tokens": 4096
}
```

`~/.aalap/mcp_servers.json`:
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-filesystem", "/path/to/dir"]
    }
  }
}
```

##  Tips & Best Practices

1. **Use Interactive Mode for Conversations** - Maintain context across multiple questions
2. **Clear Context When Switching Topics** - Use `/clear` for fresh starts
3. **Leverage MCP Servers** - Extend Claude's capabilities with specialized tools
4. **Pipe Liberally** - Aalap integrates seamlessly with Unix workflows
5. **Create Aliases** - Add shortcuts to your shell config:

```bash
# Add to ~/.bashrc or ~/.zshrc
alias ask="aalap chat"
alias ai="aalap"
alias claude="aalap"
```

Then use:
```bash
ask "How do I sort a dictionary in Python?"
ai  # Launch interactive mode
```

##  Security

- API keys are stored in `~/.aalap/config.json`
- Recommended permissions: `chmod 600 ~/.aalap/config.json`
- Never commit config files to version control
- Use environment variables for CI/CD: `export ANTHROPIC_API_KEY=xxx`
- Consider using a secrets manager for production environments

##  Updating

### Homebrew

```bash
brew upgrade aalap
```

### pip

```bash
pip install --upgrade git+https://github.com/caltycs/aalap
```

##  Troubleshooting

### Command Not Found

```bash
# Check if aalap is installed
which aalap

# If using pip, ensure your PATH includes pip's bin directory
echo $PATH

# Add to ~/.bashrc or ~/.zshrc if needed
export PATH="$HOME/.local/bin:$PATH"
```

### API Key Issues

```bash
# Verify your API key is set
aalap config

# Reset your API key
aalap config --api-key YOUR_NEW_KEY

# Or use environment variable
export ANTHROPIC_API_KEY=sk-ant-xxxxx
aalap
```

### Permission Denied

```bash
# If installed via Homebrew
brew reinstall aalap

# If installed via pip
pip install --user --force-reinstall git+https://github.com/caltycs/aalap
```

### Python Version Issues

```bash
# Check Python version (needs 3.8+)
python3 --version

# Use a specific Python version
python3.11 -m pip install git+https://github.com/caltycs/aalap
```

### Readline Issues on macOS

```bash
# Install readline support
pip install gnureadline
```

##  Uninstallation

### Homebrew

```bash
brew uninstall aalap
brew untap yourusername/aalap
```

### pip

```bash
pip uninstall aalap-cli
```

### Remove Configuration (Optional)

```bash
rm -rf ~/.aalap
```

##  Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/caltycs/aalap.git
cd aalap

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable mode with dev dependencies
pip install -e .

# Run Aalap
aalap
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest

# Run with coverage
pytest --cov=aalap tests/
```

### Building Distribution

```bash
# Install build tools
pip install build twine

# Build package
python -m build

# Check the distribution
twine check dist/*
```

##  Resources

- [Anthropic Documentation](https://docs.anthropic.com)
- [Claude API Reference](https://docs.anthropic.com/en/api)
- [MCP Documentation](https://modelcontextprotocol.io)
- [Python Anthropic SDK](https://github.com/anthropics/anthropic-sdk-python)

##  Roadmap

- [x] Interactive CLI with conversation context
- [x] MCP server management
- [x] Homebrew installation
- [ ] Streaming responses for real-time output
- [ ] Conversation export (JSON, Markdown, HTML)
- [ ] Custom prompt templates and presets
- [ ] Tab completion for commands
- [ ] Plugin system for extensions
- [ ] Multi-session management
- [ ] Syntax highlighting for code blocks
- [ ] Image input support
- [ ] Token usage tracking and statistics


##  License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

##  About the Name

**Aalap**  is a term from Indian classical music referring to the opening section of a performance—a slow, improvised exploration that sets the mood and introduces the raga. Just like a musical aalap, this CLI is your opening conversation with AI, setting the stage for deeper exploration and creative dialogue.


##  Support

- **Issues**: [GitHub Issues](https://github.com/caltycs/aalap/issues)
- **Discussions**: [GitHub Discussions](https://github.com/caltycs/aalapp/discussions)
- **Email**: info.caltycs@gmail.com

---

**Made with ❤️ for developers who love the command line**

```
     █████╗  █████╗ ██╗      █████╗ ██████╗
    ██╔══██╗██╔══██╗██║     ██╔══██╗██╔══██╗
    ███████║███████║██║     ███████║██████╔╝
    ██╔══██║██╔══██║██║     ██╔══██║██╔═══╝
    ██║  ██║██║  ██║███████╗██║  ██║██║
    ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝
```

---

