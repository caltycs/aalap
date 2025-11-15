#!/usr/bin/env python3
"""
Aalap - Interactive CLI for Claude AI with MCP server support and RAG
"""

import os
import sys
import json
import subprocess
import argparse
from pathlib import Path
from typing import Optional, List, Dict
import anthropic
import readline
from .rag import AalapRAG
from .database_rag import DatabaseRAG
from .database_query import DatabaseQueryExecutor

# Configuration paths
CONFIG_DIR = Path.home() / ".aalap"
CONFIG_FILE = CONFIG_DIR / "config.json"
MCP_CONFIG_FILE = CONFIG_DIR / "mcp_servers.json"
HISTORY_FILE = CONFIG_DIR / "history"

class AalapCLI:
    def __init__(self, org_id: str = "default"):
        self.config_dir = CONFIG_DIR
        self.config_file = CONFIG_FILE
        self.mcp_config_file = MCP_CONFIG_FILE
        self.history_file = HISTORY_FILE
        self.org_id = org_id
        self.ensure_config_dir()
        self.load_config()
        self.conversation_history = []

        # Initialize RAG system
        self.rag = AalapRAG(self.config_dir, org_id=org_id)
        self.rag_enabled = self.config.get("rag_enabled", False)

        # Initialize Database RAG
        self.db_rag = DatabaseRAG(self.rag)

        # Initialize Database Query Executor (will be created when API key is available)
        self.db_query = None
        self.active_database = None  # Store active database connection info

    def ensure_config_dir(self):
        """Create config directory if it doesn't exist"""
        self.config_dir.mkdir(exist_ok=True)

    def load_config(self):
        """Load configuration from file"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {
                "api_key": os.environ.get("ANTHROPIC_API_KEY", ""),
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 4096,
                "rag_enabled": False,
                "rag_auto_context": True,
                "rag_collections": []
            }
            self.save_config()

    def save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

    def load_mcp_servers(self) -> Dict:
        """Load MCP server configuration"""
        if self.mcp_config_file.exists():
            with open(self.mcp_config_file, 'r') as f:
                return json.load(f)
        return {"mcpServers": {}}

    def save_mcp_servers(self, servers: Dict):
        """Save MCP server configuration"""
        with open(self.mcp_config_file, 'w') as f:
            json.dump(servers, f, indent=2)

    def setup_api_key(self, api_key: str):
        """Set up Anthropic API key"""
        self.config["api_key"] = api_key
        self.save_config()
        print("✓ API key saved successfully")

    def chat(self, message: str, system_prompt: Optional[str] = None, show_thinking: bool = True):
        """Send a message to Claude with optional RAG context"""
        if not self.config.get("api_key"):
            print("Error: API key not set. Run: aalap config --api-key YOUR_KEY")
            return None

        try:
            client = anthropic.Anthropic(api_key=self.config["api_key"])

            # Build RAG context if enabled
            rag_context = ""
            sources = []
            if self.rag_enabled and self.config.get("rag_auto_context"):
                rag_context, sources = self.rag.build_context(
                    message,
                    collections=self.config.get("rag_collections")
                )

                if rag_context:
                    print(f"\n📚 Retrieved {len(sources)} relevant sources from knowledge base")

            # Prepare system prompt with RAG context
            final_system_prompt = system_prompt or ""
            if rag_context:
                rag_instruction = """
You have access to the following relevant information from the organization's knowledge base. Use this information to provide accurate, context-aware responses.

<knowledge_base>
{rag_context}
</knowledge_base>

Please cite sources when using information from the knowledge base by referencing [Source N].
"""
                final_system_prompt = rag_instruction.format(rag_context=rag_context)
                if system_prompt:
                    final_system_prompt += f"\n\nAdditional Instructions:\n{system_prompt}"

            # Add message to conversation history
            self.conversation_history.append({"role": "user", "content": message})

            kwargs = {
                "model": self.config["model"],
                "max_tokens": self.config["max_tokens"],
                "messages": self.conversation_history.copy()
            }

            if final_system_prompt:
                kwargs["system"] = final_system_prompt

            if show_thinking:
                print("\n🤖 Claude is thinking...\n")

            response = client.messages.create(**kwargs)

            # Collect response text
            response_text = ""
            for block in response.content:
                if block.type == "text":
                    response_text += block.text
                    print(block.text)

            print("\n")

            # Show sources if RAG was used
            if sources:
                print("📎 Sources:")
                for src in sources:
                    print(f"  [{src['index']}] {src['source']} (relevance: {src['relevance']:.2f})")
                print()

            # Add assistant response to history
            self.conversation_history.append({"role": "assistant", "content": response_text})

            return response_text

        except anthropic.APIError as e:
            print(f"API Error: {e}")
            return None

    def list_mcp_servers(self):
        """List installed MCP servers"""
        servers = self.load_mcp_servers()

        if not servers.get("mcpServers"):
            print("No MCP servers installed")
            return

        print("\n📦 Installed MCP Servers:\n")
        for name, config in servers["mcpServers"].items():
            print(f"  • {name}")
            print(f"    Command: {config.get('command', 'N/A')}")
            if config.get('args'):
                print(f"    Args: {' '.join(config['args'])}")
            print()

    def install_mcp_server(self, name: str, command: str, args: List[str] = None, env: Dict = None):
        """Install an MCP server"""
        servers = self.load_mcp_servers()

        if "mcpServers" not in servers:
            servers["mcpServers"] = {}

        server_config = {
            "command": command
        }

        if args:
            server_config["args"] = args

        if env:
            server_config["env"] = env

        servers["mcpServers"][name] = server_config
        self.save_mcp_servers(servers)

        print(f"✓ MCP server '{name}' installed successfully")

    def remove_mcp_server(self, name: str):
        """Remove an MCP server"""
        servers = self.load_mcp_servers()

        if name in servers.get("mcpServers", {}):
            del servers["mcpServers"][name]
            self.save_mcp_servers(servers)
            print(f"✓ MCP server '{name}' removed successfully")
        else:
            print(f"Error: MCP server '{name}' not found")

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        print("✓ Conversation history cleared")

    def show_help(self):
        """Show help in interactive mode"""
        help_text = """
╔════════════════════════════════════════════════════════════════╗
║                      Aalap Commands                            ║
╚════════════════════════════════════════════════════════════════╝

Chat Commands:
  <message>              Send a message to Claude
  /clear                 Clear conversation history
  /history               Show conversation history
  /exit, /quit           Exit Aalap

RAG Commands:
  /rag enable            Enable RAG context
  /rag disable           Disable RAG context
  /rag status            Show RAG status and statistics
  /rag index <file>      Index a file or directory
  /rag collections       List available collections
  /rag search <query>    Search the knowledge base
  /rag threshold <0-1>   Set similarity threshold (default: 0.2, lower=more results)
  /rag clear             Clear all indexed data
  /rag db index <type> <connection> [options]
                         Index a database (sqlite, postgresql, mysql)

Database Query Commands:
  /db connect <type> <connection>
                         Connect to a database for querying
  /db query <question>   Ask natural language questions about your database
  /db status             Show active database connection
  /db disconnect         Disconnect from database

MCP Commands:
  /mcp list              List installed MCP servers
  /mcp install <name> <cmd> [--args ...] [--env {...}]
                         Install an MCP server
  /mcp remove <name>     Remove an MCP server

Config Commands:
  /config                Show current configuration
  /config apikey <key>   Set API key
  /config model <model>  Set Claude model
  /config org <org_id>   Set organization ID
  
Other:
  /help                  Show this help message
        """
        print(help_text)

    def show_history(self):
        """Show conversation history"""
        if not self.conversation_history:
            print("No conversation history")
            return

        print("\n📜 Conversation History:\n")
        for i, msg in enumerate(self.conversation_history, 1):
            role = "You" if msg["role"] == "user" else "Claude"
            content = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
            print(f"{i}. {role}: {content}\n")

    def show_config(self):
        """Show current configuration"""
        print("\n⚙️  Current Configuration:\n")
        print(f"  Organization: {self.org_id}")
        print(f"  API Key: {'*' * 20 if self.config.get('api_key') else 'Not set'}")
        print(f"  Model: {self.config['model']}")
        print(f"  Max Tokens: {self.config['max_tokens']}")
        print(f"  RAG Enabled: {'✓' if self.rag_enabled else '✗'}")
        print(f"  Config Dir: {self.config_dir}")
        print()

    def handle_rag_command(self, parts: List[str]):
        """Handle RAG-related commands"""
        if len(parts) < 2:
            print("Usage: /rag [enable|disable|status|index|collections|search|clear]")
            return

        subcmd = parts[1].lower()

        if subcmd == "enable":
            self.rag_enabled = True
            self.config["rag_enabled"] = True
            self.save_config()
            print("✓ RAG context enabled")

        elif subcmd == "disable":
            self.rag_enabled = False
            self.config["rag_enabled"] = False
            self.save_config()
            print("✓ RAG context disabled")

        elif subcmd == "status":
            stats = self.rag.get_stats()
            print("\n📊 RAG System Status:\n")
            print(f"  Status: {'Enabled' if self.rag_enabled else 'Disabled'}")
            print(f"  Organization: {stats['org_id']}")
            print(f"  Total Chunks: {stats['total_chunks']}")
            print(f"\n  Collections:")
            for name, count in stats['collections'].items():
                print(f"    • {name}: {count} chunks")
            print()

        elif subcmd == "collections":
            stats = self.rag.get_stats()
            print("\n📚 Available Collections:\n")
            if stats['collections']:
                for name, count in stats['collections'].items():
                    print(f"  • {name} ({count} chunks)")
            else:
                print("  No collections indexed yet")
            print()

        elif subcmd == "index" and len(parts) >= 3:
            file_path = " ".join(parts[2:])
            path = Path(file_path).expanduser()

            if not path.exists():
                print(f"Error: Path not found: {file_path}")
                return

            print(f"Indexing: {path}")
            # Implementation for indexing files
            self._index_path(path)

        elif subcmd == "search" and len(parts) >= 3:
            query = " ".join(parts[2:])

            # Debug: Check what collections we're searching
            stats = self.rag.get_stats()
            print(f"\n🔍 Search Results for: '{query}'")
            print(f"📚 Available collections: {list(stats['collections'].keys())}")
            print(f"📊 Total chunks: {stats['total_chunks']}\n")

            results = self.rag.retrieve(query)

            if results:
                for i, (content, metadata, score) in enumerate(results, 1):
                    print(f"{i}. [Score: {score:.2f}] {metadata.get('source', 'Unknown')}")
                    print(f"   Type: {metadata.get('type', 'unknown')}, Table: {metadata.get('table', 'unknown')}")
                    print(f"   {content[:200]}...\n")
            else:
                print("❌ No results found")
                print("\nDebugging tips:")
                print("  1. Check if data is indexed: /rag status")
                print("  2. Try searching for specific table names")
                print("  3. Check similarity threshold in RAG config")

        elif subcmd == "clear":
            confirm = input("Are you sure you want to clear all RAG data? (yes/no): ")
            if confirm.lower() == "yes":
                if self.rag.clear_all():
                    print("✓ All RAG data cleared")
                else:
                    print("✗ Failed to clear RAG data")

        elif subcmd == "threshold" and len(parts) >= 3:
            try:
                new_threshold = float(parts[2])
                if 0 <= new_threshold <= 1:
                    self.rag.rag_config["similarity_threshold"] = new_threshold
                    self.rag._save_rag_config()

                    # Invalidate the database query executor so it uses the new threshold
                    if self.db_query is not None:
                        self.db_query = None
                        print("✓ Database query executor reset to use new threshold")

                    print(f"✓ Similarity threshold set to {new_threshold}")
                    print(f"  Lower values = more permissive search")
                    print(f"  Higher values = stricter search")
                else:
                    print("Error: Threshold must be between 0 and 1")
            except ValueError:
                print("Error: Invalid threshold value")

        elif subcmd == "db":
            self._handle_db_command(parts[2:] if len(parts) > 2 else [])

        else:
            print("Usage: /rag [enable|disable|status|index|collections|search|clear|threshold|db]")

    def _index_path(self, path: Path, collection_name: str = "documents"):
        """Index a file or directory"""
        if path.is_file():
            self._index_file(path, collection_name)
        elif path.is_dir():
            for file_path in path.rglob("*"):
                if file_path.is_file():
                    self._index_file(file_path, collection_name)

    def _index_file(self, file_path: Path, collection_name: str):
        """Index a single file"""
        try:
            # Read file based on extension
            suffix = file_path.suffix.lower()

            if suffix in ['.txt', '.md', '.py', '.js', '.java', '.cpp', '.c', '.h']:
                content = file_path.read_text()
            elif suffix == '.pdf':
                # Would use PyPDF2 here
                print(f"Skipping PDF (not implemented): {file_path}")
                return
            elif suffix == '.docx':
                # Would use python-docx here
                print(f"Skipping DOCX (not implemented): {file_path}")
                return
            else:
                print(f"Skipping unsupported file type: {file_path}")
                return

            from datetime import datetime

            metadata = {
                "source": str(file_path),
                "filename": file_path.name,
                "type": suffix,
                "indexed_at": datetime.now().isoformat(),
                "file_modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
            }

            if self.rag.index_document(collection_name, content, metadata):
                print(f"  ✓ Indexed: {file_path}")
            else:
                print(f"  ✗ Failed to index: {file_path}")

        except Exception as e:
            print(f"  ✗ Error indexing {file_path}: {e}")

    def _handle_db_command(self, args: List[str]):
        """Handle database RAG commands"""
        if not args or args[0] not in ['index']:
            print("Usage: /rag db index <db_type> <connection_info> [options]")
            print("\nDatabase types:")
            print("  sqlite     - SQLite database (provide file path)")
            print("  postgresql - PostgreSQL database (provide connection string)")
            print("  mysql      - MySQL database (provide connection string)")
            print("\nOptions:")
            print("  --collection <name>    Collection name (default: 'database')")
            print("  --tables <t1,t2,...>   Specific tables to index (default: all)")
            print("  --sample-data          Include sample data rows")
            print("  --sample-rows <N>      Number of sample rows (default: 5)")
            print("\nExamples:")
            print("  /rag db index sqlite ~/company.db")
            print("  /rag db index postgresql postgresql://user:pass@localhost/mydb --sample-data")
            print("  /rag db index mysql mysql://user:pass@localhost/mydb --tables users,orders")
            return

        subcmd = args[0]

        if subcmd == "index":
            if len(args) < 3:
                print("Error: Missing database type and connection info")
                print("Usage: /rag db index <db_type> <connection_info> [options]")
                return

            db_type = args[1].lower()
            connection_info = args[2]

            # Parse options
            collection_name = "database"
            tables = None
            include_sample_data = False
            sample_rows = 5

            i = 3
            while i < len(args):
                if args[i] == '--collection' and i + 1 < len(args):
                    collection_name = args[i + 1]
                    i += 2
                elif args[i] == '--tables' and i + 1 < len(args):
                    tables = args[i + 1].split(',')
                    i += 2
                elif args[i] == '--sample-data':
                    include_sample_data = True
                    i += 1
                elif args[i] == '--sample-rows' and i + 1 < len(args):
                    sample_rows = int(args[i + 1])
                    i += 2
                else:
                    print(f"Warning: Unknown option '{args[i]}'")
                    i += 1

            # Expand user path for sqlite
            if db_type == 'sqlite':
                connection_info = str(Path(connection_info).expanduser())

                if not Path(connection_info).exists():
                    print(f"Error: SQLite database not found: {connection_info}")
                    return

            # Index the database
            print(f"\n🔄 Indexing {db_type} database...")
            print(f"   Connection: {connection_info}")
            print(f"   Collection: {collection_name}")
            if tables:
                print(f"   Tables: {', '.join(tables)}")
            else:
                print(f"   Tables: All")
            print(f"   Sample data: {'Yes' if include_sample_data else 'No'}")
            print()

            try:
                if db_type == 'sqlite':
                    stats = self.db_rag.index_sqlite_database(
                        db_path=connection_info,
                        collection_name=collection_name,
                        tables=tables,
                        include_sample_data=include_sample_data,
                        sample_rows=sample_rows
                    )
                elif db_type == 'postgresql':
                    stats = self.db_rag.index_postgres_database(
                        connection_string=connection_info,
                        collection_name=collection_name,
                        tables=tables,
                        include_sample_data=include_sample_data,
                        sample_rows=sample_rows
                    )
                elif db_type == 'mysql':
                    stats = self.db_rag.index_mysql_database(
                        connection_string=connection_info,
                        collection_name=collection_name,
                        tables=tables,
                        include_sample_data=include_sample_data,
                        sample_rows=sample_rows
                    )
                else:
                    print(f"Error: Unsupported database type '{db_type}'")
                    print("Supported types: sqlite, postgresql, mysql")
                    return

                # Display results
                print("\n✅ Database indexing complete!")
                print(f"\n📊 Statistics:")
                print(f"   Database type: {stats['database_type']}")
                print(f"   Collection: {stats['collection']}")
                print(f"   Tables indexed: {stats['tables_indexed']}")
                print(f"   Schemas indexed: {stats['schemas_indexed']}")
                if include_sample_data:
                    print(f"   Sample data rows: {stats['sample_data_rows']}")

                if stats.get('errors'):
                    print(f"\n⚠️  Errors encountered:")
                    for error in stats['errors']:
                        print(f"   • {error}")

            except ImportError as e:
                print(f"\n❌ Missing dependency: {e}")
            except Exception as e:
                print(f"\n❌ Error indexing database: {e}")
                import traceback
                traceback.print_exc()

    def _ensure_db_query_executor(self):
        """Ensure DatabaseQueryExecutor is initialized"""
        if self.db_query is None:
            if not self.config.get("api_key"):
                print("Error: API key not set. Database queries require Claude API access.")
                print("Set it with: /config apikey YOUR_KEY")
                return False

            client = anthropic.Anthropic(api_key=self.config["api_key"])
            self.db_query = DatabaseQueryExecutor(self.rag, client, self.config)
        return True

    def _handle_db_query_command(self, args: List[str]):
        """Handle /db query commands for natural language database queries"""
        if not args:
            print("Usage: /db [connect|query|disconnect|status]")
            print("\nCommands:")
            print("  /db connect <type> <connection>")
            print("      Connect to a database for querying")
            print("      Example: /db connect sqlite ~/company.db")
            print()
            print("  /db query <question>")
            print("      Ask a natural language question about your database")
            print("      Example: /db query how many customers do we have?")
            print()
            print("  /db status")
            print("      Show active database connection")
            print()
            print("  /db disconnect")
            print("      Disconnect from current database")
            return

        subcmd = args[0].lower()

        if subcmd == "connect":
            if len(args) < 3:
                print("Error: Missing database type and connection info")
                print("Usage: /db connect <type> <connection>")
                print("Example: /db connect sqlite ~/company.db")
                return

            db_type = args[1].lower()
            connection_info = args[2]

            # Expand user path for sqlite
            if db_type == "sqlite":
                connection_info = str(Path(connection_info).expanduser())
                if not Path(connection_info).exists():
                    print(f"Error: SQLite database not found: {connection_info}")
                    return

            self.active_database = {
                "type": db_type,
                "connection": connection_info
            }

            print(f"✓ Connected to {db_type} database")
            print(f"  Connection: {connection_info}")
            print("\nYou can now query this database with: /db query <your question>")

        elif subcmd == "query":
            if not self.active_database:
                print("Error: No database connected")
                print("Connect first with: /db connect <type> <connection>")
                return

            if len(args) < 2:
                print("Error: Missing query question")
                print("Usage: /db query <your question>")
                return

            if not self._ensure_db_query_executor():
                return

            question = " ".join(args[1:])

            print(f"\n🔍 Question: {question}")
            print(f"📊 Database: {self.active_database['type']} at {self.active_database['connection']}")
            print("\n" + "="*60)

            try:
                # Execute natural language query
                result = self.db_query.query(
                    question=question,
                    db_type=self.active_database["type"],
                    connection_info=self.active_database["connection"],
                    collection_name="database",
                    explain=True
                )

                if result.get("error"):
                    print(f"\n❌ Error: {result['error']}")
                    return

                # Show SQL query
                print(f"\n💡 Generated SQL:")
                print(f"   {result['sql_query']}")

                # Show results count
                print(f"\n📈 Results: {len(result['results'])} row(s)")

                # Show results (limited for readability)
                if result['results']:
                    print("\n📋 Data:")
                    max_display = 10
                    for i, row in enumerate(result['results'][:max_display], 1):
                        print(f"\n   Row {i}:")
                        for col, val in row.items():
                            print(f"      {col}: {val}")

                    if len(result['results']) > max_display:
                        print(f"\n   ... and {len(result['results']) - max_display} more rows")

                # Show insights
                print("\n" + "="*60)
                print("\n🤖 Insights:\n")
                print(result['insights'])
                print("\n" + "="*60)

                # Show sources used
                if result.get('sources'):
                    print(f"\n📚 Used {len(result['sources'])} schema sources from knowledge base")

            except Exception as e:
                print(f"\n❌ Error executing query: {e}")
                import traceback
                traceback.print_exc()

        elif subcmd == "status":
            if self.active_database:
                print(f"✓ Connected to {self.active_database['type']} database")
                print(f"  Connection: {self.active_database['connection']}")
            else:
                print("✗ No database connected")
                print("Connect with: /db connect <type> <connection>")

        elif subcmd == "disconnect":
            if self.active_database:
                db_info = self.active_database
                self.active_database = None
                print(f"✓ Disconnected from {db_info['type']} database")
            else:
                print("No database connected")

        else:
            print(f"Unknown subcommand: {subcmd}")
            print("Usage: /db [connect|query|disconnect|status]")

    def interactive_mode(self):
        """Run Aalap in interactive mode"""
        # Setup readline history
        if self.history_file.exists():
            try:
                readline.read_history_file(self.history_file)
            except:
                pass

        # Print welcome banner
        rag_status = "🟢 RAG Enabled" if self.rag_enabled else "⚪ RAG Disabled"
        print(f"""
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║     █████╗  █████╗ ██╗      █████╗ ██████╗                   ║
║    ██╔══██╗██╔══██╗██║     ██╔══██╗██╔══██╗                  ║
║    ███████║███████║██║     ███████║██████╔╝                  ║
║    ██╔══██║██╔══██║██║     ██╔══██║██╔═══╝                   ║
║    ██║  ██║██║  ██║███████╗██║  ██║██║                       ║
║    ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝                       ║
║                                                                ║
║              Interactive Claude AI Terminal                    ║
║                   {rag_status}                    ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝

Organization: {self.org_id}
Type /help for commands or start chatting!
Type /exit or /quit to leave
        """)

        # Check API key
        if not self.config.get("api_key"):
            print("⚠️  Warning: API key not configured!")
            print("Set it with: /config apikey YOUR_KEY\n")

        while True:
            try:
                user_input = input("\n💬 You: ").strip()

                if not user_input:
                    continue

                # Save to history
                try:
                    readline.write_history_file(self.history_file)
                except:
                    pass

                # Handle commands
                if user_input.startswith('/'):
                    parts = user_input[1:].split()
                    cmd = parts[0].lower()

                    if cmd in ['exit', 'quit']:
                        print("\n👋 Goodbye!\n")
                        break

                    elif cmd == 'help':
                        self.show_help()

                    elif cmd == 'clear':
                        self.clear_history()

                    elif cmd == 'history':
                        self.show_history()

                    elif cmd == 'rag':
                        self.handle_rag_command(parts)

                    elif cmd == 'config':
                        if len(parts) == 1:
                            self.show_config()
                        elif len(parts) >= 3 and parts[1] == 'apikey':
                            self.setup_api_key(parts[2])
                        elif len(parts) >= 3 and parts[1] == 'model':
                            self.config['model'] = parts[2]
                            self.save_config()
                            print(f"✓ Model set to {parts[2]}")
                        elif len(parts) >= 3 and parts[1] == 'org':
                            self.org_id = parts[2]
                            self.rag = AalapRAG(self.config_dir, org_id=self.org_id)
                            print(f"✓ Organization set to {parts[2]}")
                        else:
                            print("Usage: /config [apikey <key> | model <model> | org <org_id>]")

                    elif cmd == 'mcp':
                        if len(parts) < 2:
                            print("Usage: /mcp [list | install | remove]")
                            continue

                        subcmd = parts[1].lower()

                        if subcmd == 'list':
                            self.list_mcp_servers()

                        elif subcmd == 'install' and len(parts) >= 4:
                            name = parts[2]
                            command = parts[3]
                            args = parts[4:] if len(parts) > 4 else None
                            self.install_mcp_server(name, command, args)

                        elif subcmd == 'remove' and len(parts) >= 3:
                            self.remove_mcp_server(parts[2])

                        else:
                            print("Usage: /mcp [list | install <name> <cmd> | remove <name>]")

                    elif cmd == 'db':
                        self._handle_db_query_command(parts[1:] if len(parts) > 1 else [])

                    else:
                        print(f"Unknown command: /{cmd}. Type /help for available commands.")

                else:
                    # Regular chat message
                    self.chat(user_input, show_thinking=True)

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!\n")
                break
            except EOFError:
                print("\n\n👋 Goodbye!\n")
                break

def main():
    parser = argparse.ArgumentParser(
        description="Aalap - Interactive CLI for Claude AI with RAG",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument("--org", help="Organization ID", default="default")

    # If no arguments except possibly --org, start interactive mode
    if len(sys.argv) <= 2 and (len(sys.argv) == 1 or sys.argv[1].startswith('--org')):
        org_id = None
        if len(sys.argv) == 2:
            org_id = sys.argv[1].split('=')[1] if '=' in sys.argv[1] else "default"
        cli = AalapCLI(org_id=org_id or "default")
        cli.interactive_mode()
        return

    # Parse other commands...
    # (rest of the argument parsing code stays the same)

if __name__ == "__main__":
    main()