#!/usr/bin/env python3
"""
RAG (Retrieval-Augmented Generation) implementation for Aalap
Supports private, organization-specific knowledge bases
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import tiktoken
from datetime import datetime

class AalapRAG:
    """
    RAG system for Aalap with organization-specific knowledge management
    """

    def __init__(self, config_dir: Path, org_id: str = "default"):
        """
        Initialize RAG system

        Args:
            config_dir: Configuration directory path
            org_id: Organization identifier for data isolation
        """
        self.config_dir = config_dir
        self.org_id = org_id
        self.rag_dir = config_dir / "rag" / org_id
        self.rag_dir.mkdir(parents=True, exist_ok=True)

        # Initialize vector store (ChromaDB - local and persistent)
        self.chroma_client = chromadb.PersistentClient(
            path=str(self.rag_dir / "chroma"),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        # Initialize embedding model (runs locally)
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

        # Initialize tokenizer for token counting
        self.tokenizer = tiktoken.get_encoding("cl100k_base")

        # Load or create collections
        self.collections = {}
        self._load_collections()

        # RAG configuration
        self.rag_config = self._load_rag_config()

    def _load_rag_config(self) -> Dict:
        """Load RAG configuration"""
        config_file = self.rag_dir / "rag_config.json"
        if config_file.exists():
            with open(config_file, 'r') as f:
                return json.load(f)

        # Default configuration
        default_config = {
            "max_context_tokens": 3000,
            "top_k_results": 5,
            "similarity_threshold": 0.3,
            "chunk_size": 500,
            "chunk_overlap": 50,
            "enabled_sources": [],
            "auto_index": False,
            "rerank": True
        }

        with open(config_file, 'w') as f:
            json.dump(default_config, f, indent=2)

        return default_config

    def _save_rag_config(self):
        """Save RAG configuration"""
        config_file = self.rag_dir / "rag_config.json"
        with open(config_file, 'w') as f:
            json.dump(self.rag_config, f, indent=2)

    def _load_collections(self):
        """Load existing collections"""
        try:
            for collection in self.chroma_client.list_collections():
                self.collections[collection.name] = collection
        except Exception as e:
            print(f"Warning: Could not load collections: {e}")

    def create_collection(self, name: str, metadata: Dict = None) -> bool:
        """
        Create a new collection for a data source

        Args:
            name: Collection name (e.g., 'docs', 'code', 'confluence')
            metadata: Additional metadata

        Returns:
            True if successful
        """
        try:
            collection = self.chroma_client.create_collection(
                name=name,
                metadata=metadata or {}
            )
            self.collections[name] = collection
            return True
        except Exception as e:
            print(f"Error creating collection '{name}': {e}")
            return False

    def delete_collection(self, name: str) -> bool:
        """Delete a collection"""
        try:
            self.chroma_client.delete_collection(name)
            if name in self.collections:
                del self.collections[name]
            return True
        except Exception as e:
            print(f"Error deleting collection '{name}': {e}")
            return False

    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into chunks for embedding

        Args:
            text: Input text

        Returns:
            List of text chunks
        """
        chunk_size = self.rag_config["chunk_size"]
        chunk_overlap = self.rag_config["chunk_overlap"]

        words = text.split()
        chunks = []

        for i in range(0, len(words), chunk_size - chunk_overlap):
            chunk = " ".join(words[i:i + chunk_size])
            if chunk:
                chunks.append(chunk)

        return chunks

    def index_document(
            self,
            collection_name: str,
            content: str,
            metadata: Dict,
            doc_id: Optional[str] = None
    ) -> bool:
        """
        Index a document into a collection

        Args:
            collection_name: Target collection
            content: Document content
            metadata: Document metadata (source, title, date, etc.)
            doc_id: Unique document ID

        Returns:
            True if successful
        """
        if collection_name not in self.collections:
            if not self.create_collection(collection_name):
                return False

        collection = self.collections[collection_name]

        try:
            # Chunk the content
            chunks = self.chunk_text(content)

            # Generate embeddings
            embeddings = self.embedding_model.encode(chunks).tolist()

            # Prepare IDs and metadata
            doc_id = doc_id or f"{collection_name}_{datetime.now().timestamp()}"
            ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]

            # Add chunk index to metadata
            metadatas = [
                {**metadata, "chunk_index": i, "doc_id": doc_id}
                for i in range(len(chunks))
            ]

            # Add to collection
            collection.add(
                embeddings=embeddings,
                documents=chunks,
                metadatas=metadatas,
                ids=ids
            )

            return True

        except Exception as e:
            print(f"Error indexing document: {e}")
            return False

    def index_from_mcp(
            self,
            mcp_server: str,
            resource_uri: str,
            collection_name: str
    ) -> bool:
        """
        Index content from an MCP server

        Args:
            mcp_server: MCP server name
            resource_uri: Resource URI to index
            collection_name: Target collection

        Returns:
            True if successful
        """
        # This would integrate with MCP servers to fetch and index content
        # Implementation depends on MCP server capabilities
        pass

    def retrieve(
            self,
            query: str,
            collections: Optional[List[str]] = None,
            top_k: Optional[int] = None,
            filters: Optional[Dict] = None
    ) -> List[Tuple[str, Dict, float]]:
        """
        Retrieve relevant documents for a query

        Args:
            query: Search query
            collections: List of collections to search (None = all)
            top_k: Number of results to return
            filters: Metadata filters

        Returns:
            List of (content, metadata, score) tuples
        """
        if not self.collections:
            return []

        top_k = top_k or self.rag_config["top_k_results"]
        search_collections = collections or list(self.collections.keys())

        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])[0].tolist()

        all_results = []

        for coll_name in search_collections:
            if coll_name not in self.collections:
                continue

            collection = self.collections[coll_name]

            try:
                # Query the collection
                results = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=top_k,
                    where=filters
                )

                # Process results
                for i in range(len(results['documents'][0])):
                    content = results['documents'][0][i]
                    metadata = results['metadatas'][0][i]
                    distance = results['distances'][0][i]

                    # Convert distance to similarity score
                    similarity = 1 - distance

                    if similarity >= self.rag_config["similarity_threshold"]:
                        all_results.append((content, metadata, similarity))

            except Exception as e:
                print(f"Error querying collection '{coll_name}': {e}")

        # Sort by similarity
        all_results.sort(key=lambda x: x[2], reverse=True)

        # Optionally rerank results
        if self.rag_config.get("rerank"):
            all_results = self._rerank_results(query, all_results)

        return all_results[:top_k]

    def _rerank_results(
            self,
            query: str,
            results: List[Tuple[str, Dict, float]]
    ) -> List[Tuple[str, Dict, float]]:
        """
        Rerank results using cross-encoder for better relevance

        Args:
            query: Original query
            results: Initial results

        Returns:
            Reranked results
        """
        # Simple reranking based on keyword overlap
        # In production, use a cross-encoder model
        query_terms = set(query.lower().split())

        reranked = []
        for content, metadata, score in results:
            content_terms = set(content.lower().split())
            overlap = len(query_terms & content_terms)
            # Boost score based on keyword overlap
            boosted_score = score * (1 + overlap * 0.1)
            reranked.append((content, metadata, boosted_score))

        reranked.sort(key=lambda x: x[2], reverse=True)
        return reranked

    def build_context(
            self,
            query: str,
            collections: Optional[List[str]] = None,
            max_tokens: Optional[int] = None
    ) -> Tuple[str, List[Dict]]:
        """
        Build context for Claude from retrieved documents

        Args:
            query: User query
            collections: Collections to search
            max_tokens: Maximum context tokens

        Returns:
            (context_string, sources_list)
        """
        max_tokens = max_tokens or self.rag_config["max_context_tokens"]

        # Retrieve relevant documents
        results = self.retrieve(query, collections)

        if not results:
            return "", []

        # Build context within token limit
        context_parts = []
        sources = []
        current_tokens = 0

        for i, (content, metadata, score) in enumerate(results):
            # Estimate tokens
            chunk_tokens = len(self.tokenizer.encode(content))

            if current_tokens + chunk_tokens > max_tokens:
                break

            # Format context entry
            source_info = metadata.get('source', 'Unknown')
            context_parts.append(f"[Source {i+1}: {source_info}]\n{content}\n")

            sources.append({
                "index": i + 1,
                "source": source_info,
                "metadata": metadata,
                "relevance": score
            })

            current_tokens += chunk_tokens

        context = "\n---\n".join(context_parts)

        return context, sources

    def get_stats(self) -> Dict:
        """Get RAG system statistics"""
        stats = {
            "org_id": self.org_id,
            "collections": {},
            "total_documents": 0,
            "total_chunks": 0
        }

        for name, collection in self.collections.items():
            count = collection.count()
            stats["collections"][name] = count
            stats["total_chunks"] += count

        return stats

    def clear_all(self) -> bool:
        """Clear all indexed data"""
        try:
            for name in list(self.collections.keys()):
                self.delete_collection(name)
            return True
        except Exception as e:
            print(f"Error clearing RAG data: {e}")
            return False