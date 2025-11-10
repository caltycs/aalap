#!/usr/bin/env python3
"""
Aalap - Interactive CLI for Claude AI with MCP server support
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

# Configuration paths
CONFIG_DIR = Path.home() / ".aalap"
CONFIG_FILE = CONFIG_DIR / "config.json"
MCP_CONFIG_FILE = CONFIG_DIR / "mcp_servers.json"
HISTORY_FILE = CONFIG_DIR / "history"

class AalapCLI:
    def __init__(self):
        self.config_dir = CONFIG_DIR
        self.config_file = CONFIG_FILE
        self.mcp_config_file = MCP_CONFIG_FILE
        self.history_file = HISTORY_FILE
        self.ensure_config_dir()
        self.load_config()
        self.conversation_history = []

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
                "max_tokens": 4096
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
        """Send a message to Claude"""
        if not self.config.get("api_key"):
            print("Error: API key not set. Run: aalap config --api-key YOUR_KEY")
            return None

        try:
            client = anthropic.Anthropic(api_key=self.config["api_key"])

            # Add message to conversation history
            self.conversation_history.append({"role": "user", "content": message})

            kwargs = {
                "model": self.config["model"],
                "max_tokens": self.config["max_tokens"],
                "messages": self.conversation_history.copy()
            }

            if system_prompt:
                kwargs["system"] = system_prompt

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

MCP Commands:
  /mcp list              List installed MCP servers
  /mcp install <name> <cmd> [--args ...] [--env {...}]
                         Install an MCP server
  /mcp remove <name>     Remove an MCP server

Config Commands:
  /config                Show current configuration
  /config apikey <key>   Set API key
  /config model <model>  Set Claude model
  
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
        print(f"  API Key: {'*' * 20 if self.config.get('api_key') else 'Not set'}")
        print(f"  Model: {self.config['model']}")
        print(f"  Max Tokens: {self.config['max_tokens']}")
        print(f"  Config Dir: {self.config_dir}")
        print()

    def interactive_mode(self):
        """Run Aalap in interactive mode"""
        # Setup readline history
        if self.history_file.exists():
            try:
                readline.read_history_file(self.history_file)
            except:
                pass

        # Print welcome banner
        print("""
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
║                                                                ║
╚════════════════════════════════════════════════════════════════╝

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

                    elif cmd == 'config':
                        if len(parts) == 1:
                            self.show_config()
                        elif len(parts) >= 3 and parts[1] == 'apikey':
                            self.setup_api_key(parts[2])
                        elif len(parts) >= 3 and parts[1] == 'model':
                            self.config['model'] = parts[2]
                            self.save_config()
                            print(f"✓ Model set to {parts[2]}")
                        else:
                            print("Usage: /config [apikey <key> | model <model>]")

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
    # If no arguments, start interactive mode
    if len(sys.argv) == 1:
        cli = AalapCLI()
        cli.interactive_mode()
        return

    # Otherwise parse arguments for command-line usage
    parser = argparse.ArgumentParser(
        description="Aalap - Interactive CLI for Claude AI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Config command
    config_parser = subparsers.add_parser("config", help="Configure Aalap")
    config_parser.add_argument("--api-key", help="Set Anthropic API key")
    config_parser.add_argument("--model", help="Set Claude model")
    config_parser.add_argument("--max-tokens", type=int, help="Set max tokens")

    # Chat command
    chat_parser = subparsers.add_parser("chat", help="Chat with Claude")
    chat_parser.add_argument("message", nargs="?", help="Message to send to Claude")
    chat_parser.add_argument("--system", help="System prompt")

    # MCP commands
    mcp_parser = subparsers.add_parser("mcp", help="Manage MCP servers")
    mcp_subparsers = mcp_parser.add_subparsers(dest="mcp_command")

    mcp_list = mcp_subparsers.add_parser("list", help="List MCP servers")

    mcp_install = mcp_subparsers.add_parser("install", help="Install MCP server")
    mcp_install.add_argument("name", help="Server name")
    mcp_install.add_argument("command", help="Command to run")
    mcp_install.add_argument("--args", nargs="+", help="Command arguments")
    mcp_install.add_argument("--env", help="Environment variables (JSON)")

    mcp_remove = mcp_subparsers.add_parser("remove", help="Remove MCP server")
    mcp_remove.add_argument("name", help="Server name")

    args = parser.parse_args()

    cli = AalapCLI()

    if args.command == "config":
        if args.api_key:
            cli.setup_api_key(args.api_key)
        if args.model:
            cli.config["model"] = args.model
            cli.save_config()
            print(f"✓ Model set to {args.model}")
        if args.max_tokens:
            cli.config["max_tokens"] = args.max_tokens
            cli.save_config()
            print(f"✓ Max tokens set to {args.max_tokens}")

        if not any([args.api_key, args.model, args.max_tokens]):
            cli.show_config()

    elif args.command == "chat":
        if args.message:
            cli.chat(args.message, args.system)
        else:
            # Read from stdin
            message = sys.stdin.read().strip()
            if message:
                cli.chat(message, args.system)
            else:
                print("Error: No message provided")

    elif args.command == "mcp":
        if args.mcp_command == "list":
            cli.list_mcp_servers()
        elif args.mcp_command == "install":
            env = json.loads(args.env) if args.env else None
            cli.install_mcp_server(args.name, args.command, args.args, env)
        elif args.mcp_command == "remove":
            cli.remove_mcp_server(args.name)
        else:
            mcp_parser.print_help()

if __name__ == "__main__":
    main()