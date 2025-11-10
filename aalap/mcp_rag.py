#!/usr/bin/env python3
"""
MCP Integration for RAG
Automatically index content from MCP servers
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from .rag import AalapRAG
from .document_processor import DocumentProcessor

class MCPRAGIntegration:
    """Integration between MCP servers and RAG system"""

    def __init__(self, rag: AalapRAG, mcp_config_file: Path):
        self.rag = rag
        self.mcp_config_file = mcp_config_file
        self.load_mcp_config()

    def load_mcp_config(self):
        """Load MCP server configuration"""
        if self.mcp_config_file.exists():
            with open(self.mcp_config_file, 'r') as f:
                self.mcp_config = json.load(f)
        else:
            self.mcp_config = {"mcpServers": {}}

    def index_filesystem_server(
            self,
            server_name: str,
            collection_name: Optional[str] = None
    ) -> Dict:
        """
        Index content from a filesystem MCP server

        Args:
            server_name: Name of the MCP server
            collection_name: Target collection (defaults to server_name)

        Returns:
            Statistics about indexing
        """
        if server_name not in self.mcp_config.get("mcpServers", {}):
            return {"error": f"Server '{server_name}' not found"}

        server_config = self.mcp_config["mcpServers"][server_name]

        # Extract path from server args
        if "args" not in server_config or len(server_config["args"]) < 2:
            return {"error": "Invalid filesystem server configuration"}

        # Assuming args format: [@modelcontextprotocol/server-filesystem, /path]
        base_path = Path(server_config["args"][-1]).expanduser()

        if not base_path.exists():
            return {"error": f"Path not found: {base_path}"}

        collection = collection_name or server_name

        # Process and index all files
        processor = DocumentProcessor()
        results = processor.process_directory(base_path, recursive=True)

        stats = {
            "server": server_name,
            "collection": collection,
            "path": str(base_path),
            "processed": 0,
            "indexed": 0,
            "failed": 0
        }

        for file_path, content, metadata in results:
            stats["processed"] += 1

            # Add server info to metadata
            metadata["mcp_server"] = server_name
            metadata["indexed_via"] = "mcp"

            if self.rag.index_document(collection, content, metadata, doc_id=str(file_path)):
                stats["indexed"] += 1
            else:
                stats["failed"] += 1

        return stats

    def index_database_server(
            self,
            server_name: str,
            tables: Optional[List[str]] = None,
            collection_name: Optional[str] = None
    ) -> Dict:
        """
        Index content from a database MCP server

        Args:
            server_name: Name of the MCP server
            tables: Specific tables to index (None = all)
            collection_name: Target collection

        Returns:
            Statistics about indexing
        """
        # This would integrate with database MCP servers
        # to fetch and index database schema, documentation, etc.

        stats = {
            "server": server_name,
            "collection": collection_name or server_name,
            "tables_indexed": 0,
            "error": "Database indexing not yet implemented"
        }

        return stats

    def index_github_server(
            self,
            server_name: str,
            repos: Optional[List[str]] = None,
            collection_name: Optional[str] = None
    ) -> Dict:
        """
        Index content from a GitHub MCP server

        Args:
            server_name: Name of the MCP server
            repos: Specific repos to index (None = all accessible)
            collection_name: Target collection

        Returns:
            Statistics about indexing
        """
        # This would integrate with GitHub MCP server
        # to fetch and index README files, documentation, issues, etc.

        stats = {
            "server": server_name,
            "collection": collection_name or server_name,
            "repos_indexed": 0,
            "error": "GitHub indexing not yet implemented"
        }

        return stats

    def auto_index_all_servers(self) -> Dict[str, Dict]:
        """
        Automatically index content from all configured MCP servers

        Returns:
            Dictionary mapping server names to indexing statistics
        """
        results = {}

        for server_name, server_config in self.mcp_config.get("mcpServers", {}).items():
            command = server_config.get("command", "")
            args = server_config.get("args", [])

            # Determine server type
            if args and "@modelcontextprotocol/server-filesystem" in " ".join(args):
                results[server_name] = self.index_filesystem_server(server_name)
            elif args and "@modelcontextprotocol/server-postgres" in " ".join(args):
                results[server_name] = self.index_database_server(server_name)
            elif args and "@modelcontextprotocol/server-github" in " ".join(args):
                results[server_name] = self.index_github_server(server_name)
            else:
                results[server_name] = {
                    "error": "Unknown or unsupported MCP server type"
                }

        return results

    def get_indexed_sources(self) -> Dict[str, List[str]]:
        """
        Get list of indexed sources from MCP servers

        Returns:
            Dictionary mapping collection names to source lists
        """
        stats = self.rag.get_stats()
        sources = {}

        for collection_name in stats["collections"].keys():
            # Query collection for MCP-indexed documents
            # This is a simplified version
            sources[collection_name] = []

        return sources