# Aalap 🎵

> An intelligent command-line interface for Claude AI with RAG, Database Querying, and MCP server support

Simply type `aalap` to enter an elegant, interactive terminal session with Claude AI. Have conversations, query databases with natural language, build organization-specific knowledge bases, and integrate powerful MCP tools—all from your command line.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## ✨ Features

### 💬 Core Features
-  **Beautiful Interactive CLI** - Clean, intuitive interface with ASCII art
-  **Conversational Context** - Maintains conversation history throughout sessions
-  **Command History** - Navigate previous commands with arrow keys
-  **Quick Commands** - Slash commands for easy control
-  **Pipe Support** - Works seamlessly with Unix pipes and streams
-  **Persistent Config** - Saves your preferences and API keys securely

### 🧠 RAG (Retrieval-Augmented Generation)
-  **Organization-Specific Knowledge Bases** - Build private, isolated knowledge repositories per organization
-  **Multi-Source Indexing** - Index documents, code files, databases, and more
-  **Semantic Search** - Find relevant information using natural language queries
-  **Context-Aware Responses** - Claude automatically uses relevant knowledge from your indexed data
-  **Collection Management** - Organize knowledge into logical collections
-  **Automatic Deduplication** - Smart document tracking prevents duplicate indexing

### 🗄️ Database Intelligence
-  **Text-to-SQL** - Ask questions in natural language, get SQL queries automatically
-  **Universal Database Support** - Works with SQLite, PostgreSQL, and MySQL
-  **Schema Auto-Discovery** - Automatically indexes and understands your database structure
-  **Query Execution** - Runs generated SQL and returns results
-  **AI-Powered Insights** - Get intelligent analysis and insights from your data
-  **Sample Data Indexing** - Optionally include sample rows for better context

### 🔧 Advanced Features
-  **MCP Server Support** - Install and manage Model Context Protocol servers
-  **Multi-Organization Support** - Separate knowledge bases for different organizations
-  **Configurable Similarity Thresholds** - Fine-tune RAG search sensitivity
-  **Token Usage Optimization** - Smart chunking and context management

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

#### Core Commands
| Command | Description |
|---------|-------------|
| `<message>` | Chat with Claude naturally |
| `/help` | Show all available commands |
| `/clear` | Clear conversation history |
| `/history` | View conversation history |
| `/config` | Show current configuration |
| `/config apikey <key>` | Set your API key |
| `/config model <model>` | Change Claude model |
| `/config org <org_id>` | Set organization ID for RAG isolation |
| `/exit` or `/quit` | Exit Aalap |

#### RAG Commands
| Command | Description |
|---------|-------------|
| `/rag enable` | Enable RAG context for conversations |
| `/rag disable` | Disable RAG context |
| `/rag status` | Show RAG statistics and status |
| `/rag index <file>` | Index a file or directory |
| `/rag collections` | List all knowledge collections |
| `/rag search <query>` | Search the knowledge base |
| `/rag threshold <0-1>` | Set similarity threshold (default: 0.0) |
| `/rag clear` | Clear all indexed data |
| `/rag db index <type> <connection> [options]` | Index a database schema |

#### Database Query Commands
| Command | Description |
|---------|-------------|
| `/db connect <type> <connection>` | Connect to a database for querying |
| `/db query <question>` | Ask natural language questions about your database |
| `/db status` | Show active database connection |
| `/db disconnect` | Disconnect from database |

#### MCP Commands
| Command | Description |
|---------|-------------|
| `/mcp list` | List installed MCP servers |
| `/mcp install <name> <cmd>` | Install an MCP server |
| `/mcp remove <name>` | Remove an MCP server |

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

## 🧠 RAG (Retrieval-Augmented Generation)

Build organization-specific knowledge bases that Claude can use to provide context-aware responses.

### Quick Start with RAG

```bash
$ aalap

# Enable RAG
💬 You: /rag enable

# Index your documentation
💬 You: /rag index ~/Documents/project-docs/

# Index specific files
💬 You: /rag index ~/README.md

# Check what's indexed
💬 You: /rag status

# Now chat with RAG-enhanced context
💬 You: How does our authentication system work?

📚 Retrieved 3 relevant sources from knowledge base

🤖 Claude is thinking...

Based on your documentation, your authentication system uses JWT tokens with...
[Source 1] auth.md (relevance: 0.89)
[Source 2] api-design.md (relevance: 0.76)
```

### Indexing Documents

```bash
# Index a single file
/rag index ~/project/README.md

# Index an entire directory
/rag index ~/Documents/company-docs/

# Index code files
/rag index ~/project/src/

# Supported file types:
# - Text: .txt, .md
# - Code: .py, .js, .java, .cpp, .c, .h
# - Documents: .pdf, .docx (requires additional dependencies)
```

### Managing Collections

```bash
# View all collections
/rag collections

# Output:
# 📚 Available Collections:
#   • documents (45 chunks)
#   • code (123 chunks)
#   • database (12 chunks)

# Search across collections
/rag search authentication

# Clear all data
/rag clear
```

### Organization Isolation

```bash
# Set organization ID
/config org acme-corp

# Now all RAG data is isolated to 'acme-corp'
# Switch organizations
/config org client-xyz

# Each organization has its own knowledge base
```

### Adjusting Search Sensitivity

```bash
# Set similarity threshold (0.0 = accept all, 1.0 = only perfect matches)
/rag threshold 0.3

# Lower values = more results, may include less relevant content
# Higher values = fewer results, only highly relevant content
# Default: 0.0 (recommended for most use cases)
```

## 🗄️ Database Intelligence

Query your databases using natural language. Aalap automatically generates SQL, executes it, and provides insights.

### Quick Start with Database Querying

```bash
$ aalap

# Step 1: Index your database schema
💬 You: /rag db index sqlite ~/company.db

🔄 Indexing sqlite database...
   Collection: database
   Tables: All
   Sample data: No

✅ Database indexing complete!

📊 Statistics:
   Database type: sqlite
   Tables indexed: 5
   Schemas indexed: 6

# Step 2: Connect to the database
💬 You: /db connect sqlite ~/company.db

✓ Connected to sqlite database

# Step 3: Ask questions in natural language!
💬 You: /db query how many customers do we have?

🔍 Question: how many customers do we have?
📊 Database: sqlite at /Users/you/company.db
============================================================

💡 Generated SQL:
   SELECT COUNT(*) FROM customers

📈 Results: 1 row(s)

📋 Data:
   Row 1:
      COUNT(*): 1,247

============================================================

🤖 Insights:

Your database currently contains 1,247 customers. This represents
the total count of customer records in the customers table.

============================================================

📚 Used 2 schema sources from knowledge base
```

### Indexing Databases

#### SQLite
```bash
# Basic indexing
/rag db index sqlite ~/myapp.db

# With sample data (includes example rows for better context)
/rag db index sqlite ~/myapp.db --sample-data

# Specific tables only
/rag db index sqlite ~/myapp.db --tables users,orders,products

# Custom collection name
/rag db index sqlite ~/myapp.db --collection production_db

# With all options
/rag db index sqlite ~/myapp.db \
  --collection myapp \
  --tables users,orders \
  --sample-data \
  --sample-rows 10
```

#### PostgreSQL
```bash
# Index PostgreSQL database
/rag db index postgresql postgresql://user:password@localhost/mydb

# With sample data
/rag db index postgresql postgresql://user:password@localhost:5432/mydb --sample-data

# Specific tables
/rag db index postgresql postgresql://user:password@localhost/mydb \
  --tables customers,transactions,products
```

#### MySQL
```bash
# Index MySQL database
/rag db index mysql mysql://user:password@localhost/mydb

# With options
/rag db index mysql mysql://user:password@localhost:3306/mydb \
  --tables users,orders \
  --sample-data \
  --sample-rows 5
```

### Querying Databases

Once connected, ask any question about your data:

```bash
# Connect first
/db connect sqlite ~/company.db

# Count queries
/db query how many orders were placed last month?
/db query how many active users do we have?

# Aggregation queries
/db query what is the average order value?
/db query what's the total revenue by product category?

# Listing queries
/db query show me the top 10 customers by spending
/db query list all products that are out of stock

# Analytical queries
/db query which day of the week has the most orders?
/db query what is the customer retention rate?

# Complex queries
/db query compare revenue between Q1 and Q2 this year
/db query find customers who haven't ordered in 6 months
```

### Database Query Features

**What you get with each query:**
1. **Generated SQL** - See the exact SQL query created
2. **Query Results** - Actual data from your database (up to 10 rows displayed)
3. **AI Insights** - Intelligent analysis of the results
4. **Schema Sources** - Which tables/schemas were used

**Supported databases:**
- SQLite (built-in, no extra dependencies)
- PostgreSQL (requires `pip install psycopg2-binary`)
- MySQL (requires `pip install mysql-connector-python`)

### Managing Database Connections

```bash
# Check active connection
/db status

# Disconnect
/db disconnect

# Connect to different database
/db connect postgresql postgresql://localhost/analytics
```

##  Configuration Files

Aalap stores its configuration in `~/.aalap/`:

```
~/.aalap/
├── config.json          # API key and settings
├── mcp_servers.json     # MCP server configurations
├── history              # Command history
└── rag/                 # RAG data (per organization)
    └── {org_id}/
        ├── chroma/      # Vector database
        └── rag_config.json  # RAG settings
```

### Configuration File Format

`~/.aalap/config.json`:
```json
{
  "api_key": "sk-ant-xxxxx",
  "model": "claude-sonnet-4-20250514",
  "max_tokens": 4096,
  "rag_enabled": true,
  "rag_auto_context": true,
  "rag_collections": []
}
```

`~/.aalap/rag/{org_id}/rag_config.json`:
```json
{
  "max_context_tokens": 3000,
  "top_k_results": 5,
  "similarity_threshold": 0.0,
  "chunk_size": 500,
  "chunk_overlap": 50,
  "rerank": true
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

### General Usage
1. **Use Interactive Mode for Conversations** - Maintain context across multiple questions
2. **Clear Context When Switching Topics** - Use `/clear` for fresh starts
3. **Leverage MCP Servers** - Extend Claude's capabilities with specialized tools
4. **Pipe Liberally** - Aalap integrates seamlessly with Unix workflows

### RAG Best Practices
5. **Enable RAG for Domain-Specific Work** - Get better answers using your own docs
6. **Index Before You Chat** - Build your knowledge base first for best results
7. **Use Organizations for Isolation** - Keep client/project data separate
8. **Search to Test** - Use `/rag search` to verify your data is indexed correctly
9. **Adjust Threshold if Needed** - Start with 0.0, increase if results are too broad

### Database Query Best Practices
10. **Index Schema First** - Always run `/rag db index` before querying
11. **Use Sample Data for Complex Queries** - Helps Claude understand data patterns
12. **Start Simple** - Test with basic counts before complex aggregations
13. **Review Generated SQL** - Always check the SQL before relying on results

### Shell Aliases
14. **Create Shortcuts** - Add aliases to your shell config:

```bash
# Add to ~/.bashrc or ~/.zshrc
alias ask="aalap chat"
alias ai="aalap"
alias claude="aalap"
alias dbquery="aalap -c '/db query'"
```

Then use:
```bash
ask "How do I sort a dictionary in Python?"
ai  # Launch interactive mode
```

##  Security

### API Keys & Credentials
- API keys are stored in `~/.aalap/config.json`
- Recommended permissions: `chmod 600 ~/.aalap/config.json`
- Never commit config files to version control
- Use environment variables for CI/CD: `export ANTHROPIC_API_KEY=xxx`
- Consider using a secrets manager for production environments

### RAG Data Privacy
- All RAG data is stored locally in `~/.aalap/rag/`
- Organization isolation ensures data separation
- Vector embeddings are generated locally using open-source models
- No data is sent to third parties except Claude API for responses

### Database Security
- Database credentials in connection strings are only used for the session
- Not stored permanently (re-enter on each connection)
- Use read-only database users when possible
- Be cautious with sample data indexing (may include sensitive information)

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

### Completed ✅
- [x] Interactive CLI with conversation context
- [x] MCP server management
- [x] RAG system with multi-source indexing
- [x] Organization-specific knowledge bases
- [x] Database schema indexing (SQLite, PostgreSQL, MySQL)
- [x] Natural language to SQL conversion
- [x] Database query execution with insights
- [x] Semantic search across documents

### In Progress 🚧
- [ ] Streaming responses for real-time output
- [ ] Enhanced PDF and DOCX support
- [ ] Web page indexing (fetch and index URLs)
- [ ] Git repository indexing

### Planned 📋
- [ ] Conversation export (JSON, Markdown, HTML)
- [ ] Custom prompt templates and presets
- [ ] Tab completion for commands
- [ ] Plugin system for extensions
- [ ] Multi-session management
- [ ] Syntax highlighting for code blocks
- [ ] Image input support
- [ ] Token usage tracking and statistics
- [ ] RAG query history and analytics
- [ ] Database query caching
- [ ] Support for MongoDB and other NoSQL databases
- [ ] Slack/Discord integration for team knowledge bases
- [ ] API server mode for team deployments


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

