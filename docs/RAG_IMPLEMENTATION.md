# RAG Implementation Guide for Aalap

## Overview

Aalap now supports Retrieval-Augmented Generation (RAG) for organization-specific knowledge management. This enables Claude to access and utilize your organization's private data while maintaining complete data privacy and security.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Aalap with RAG                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  User Query → RAG Pipeline → Context Retrieval → Claude    │
│                    ↓                                        │
│              Vector Store                                   │
│              (Local/Private)                                │
│                    ↓                                        │
│         ┌──────────────────────┐                           │
│         │   Data Sources via   │                           │
│         │    MCP Servers       │                           │
│         ├──────────────────────┤                           │
│         │  • File Systems      │                           │
│         │  • Databases         │                           │
│         │  • Git Repos         │                           │
│         │  • Confluence        │                           │
│         │  • SharePoint        │                           │
│         │  • Slack/Teams       │                           │
│         └──────────────────────┘                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Key Features

### 1. **Complete Data Privacy**
- All embeddings and vector storage are **local** (ChromaDB)
- Organization data never leaves your infrastructure except for:
    - Query text (user's question)
    - Retrieved context (sanitized chunks sent to Claude API)
- No training data used by Anthropic
- Full control over data retention

### 2. **Organization Isolation**
- Multi-tenancy support via `org_id`
- Each organization has isolated:
    - Vector databases
    - Configuration
    - Security settings
    - Encryption keys

### 3. **MCP Integration**
- Automatically index content from MCP servers
- Supported sources:
    - Filesystem
    - Databases (PostgreSQL, MySQL, etc.)
    - GitHub repositories
    - Confluence
    - SharePoint
    - Slack/Teams archives

### 4. **Security Features**
- Encryption at rest for sensitive data
- Access control per collection
- Audit logging
- Metadata sanitization before external API calls
- IP whitelisting support

## Installation

### 1. Install RAG Dependencies

```bash
pip install sentence-transformers chromadb PyPDF2 python-docx cryptography
```

### 2. Update Aalap

```bash
cd aalap
git pull
pip install -e .
```

## Quick Start

### 1. Initialize RAG for Your Organization

```bash
aalap --org=your_company_id
```

### 2. Enable RAG

```bash
💬 You: /rag enable
✓ RAG context enabled
```

### 3. Index Your First Documents

```bash
# Index a directory
💬 You: /rag index ~/Documents/company_docs

# Index from MCP server
💬 You: /rag mcp index filesystem
```

### 4. Start Chatting with Context

```bash
💬 You: What is our company's vacation policy?

🤖 Claude is thinking...
📚 Retrieved 3 relevant sources from knowledge base

Based on your company's HR documentation...
[Response with citations]

📎 Sources:
  [1] employee_handbook.pdf (relevance: 0.89)
  [2] hr_policies.md (relevance: 0.76)
  [3] benefits_guide.docx (relevance: 0.68)
```

## Configuration

### RAG Settings

Edit `~/.aalap/rag/<org_id>/rag_config.json`:

```json
{
  "max_context_tokens": 3000,
  "top_k_results": 5,
  "similarity_threshold": 0.3,
  "chunk_size": 500,
  "chunk_overlap": 50,
  "enabled_sources": ["filesystem", "confluence"],
  "auto_index": false,
  "rerank": true
}
```

### Security Settings

Edit `~/.aalap/security/<org_id>/access_control.json`:

```json
{
  "org_id": "your_company",
  "allowed_users": ["user1", "user2"],
  "restricted_collections": ["hr_confidential"],
  "data_retention_days": 90,
  "require_authentication": true,
  "allowed_ips": ["10.0.0.0/8"]
}
```

## Usage Guide

### Indexing Content

#### Index Files/Directories

```bash
# Single file
/rag index ~/docs/handbook.pdf

# Entire directory (recursive)
/rag index ~/company_docs

# Specific file types
/rag index ~/code --extensions .py .js .md
```

#### Index from MCP Servers

```bash
# List available MCP servers
/mcp list

# Install filesystem server
/mcp install company_docs npx @modelcontextprotocol/server-filesystem ~/company_docs

# Index from MCP server
/rag mcp index company_docs

# Auto-index all MCP servers
/rag mcp auto-index
```

### Managing Collections

```bash
# List collections
/rag collections

# Create new collection
/rag collection create engineering_docs

# Delete collection
/rag collection delete old_docs

# Restrict collection (require special access)
/rag collection restrict hr_confidential
```

### Searching

```bash
# Search knowledge base
/rag search "product roadmap Q4"

# Search specific collections
/rag search "API documentation" --collections engineering_docs,api_docs

# Advanced search with filters
/rag search "security policy" --filter type:pdf --min-score 0.7
```

### RAG Status and Statistics

```bash
# View RAG status
/rag status

# Output:
📊 RAG System Status:

  Status: Enabled
  Organization: your_company
  Total Chunks: 15,482
  
  Collections:
    • company_docs: 8,234 chunks
    • engineering: 5,123 chunks
    • hr_policies: 2,125 chunks
```

## Supported Document Types

| Type | Extensions | Processor |
|------|-----------|-----------|
| Text | .txt, .md | Built-in |
| PDF | .pdf | PyPDF2 |
| Word | .docx | python-docx |
| Code | .py, .js, .java, etc. | Built-in |
| JSON | .json | Built-in |

## MCP Integration Details

### Filesystem Server

```bash
# Install
/mcp install docs npx @modelcontextprotocol/server-filesystem ~/Documents

# Index
/rag mcp index docs
```

### Database Server

```bash
# Install PostgreSQL server
/mcp install company_db npx @modelcontextprotocol/server-postgres \
  --env '{"DATABASE_URL":"postgresql://localhost/company"}'

# Index database schema and documentation
/rag mcp index company_db
```

### GitHub Server

```bash
# Install
/mcp install github npx @modelcontextprotocol/server-github \
  --env '{"GITHUB_TOKEN":"ghp_xxxxx"}'

# Index repositories
/rag mcp index github --repos company/backend,company/frontend
```

## Privacy and Security

### What Data is Stored Locally?

✅ **Stored Locally:**
- Original documents
- Document embeddings
- Vector indices
- Metadata
- Configuration
- Encryption keys

❌ **NOT Stored Locally:**
- Nothing - all RAG data is local

### What Data is Sent to Anthropic?

When RAG is enabled, Aalap sends to Claude API:

1. **User's Query**: The question you ask
2. **Retrieved Context**: Relevant chunks from your documents (sanitized)
3. **System Prompt**: Instructions to use the context

**Sanitization Process:**
- File paths → filenames only
- Internal IDs → removed
- Sensitive fields (email, phone, etc.) → removed
- Employee data → redacted

**NOT Sent:**
- Original documents
- Full file paths
- Internal system information
- Embeddings or vectors
- Database credentials

### Data Retention

Configure retention in access control:

```json
{
  "data_retention_days": 90
}
```

Documents older than specified days can be automatically purged.

### Encryption

All sensitive data is encrypted at rest using Fernet (symmetric encryption):

- Encryption keys: `~/.aalap/security/<org_id>/encryption.key`
- Permissions: 600 (owner read/write only)

### Access Control

```bash
# Require authentication
/rag security require-auth

# Add authorized user
/rag security add-user alice@company.com

# Remove user
/rag security remove-user bob@company.com

# Restrict collection
/rag security restrict hr_confidential

# Audit log
/rag security audit-log
```

## Best Practices

### 1. **Organization Isolation**

Always use unique `org_id` per organization:

```bash
aalap --org=acme_corp
```

### 2. **Incremental Indexing**

Index new content regularly:

```bash
# Daily cron job
0 2 * * * aalap --org=acme --batch-index ~/new_docs
```

### 3. **Collection Organization**

Structure collections by domain:

- `engineering_docs` - Technical documentation
- `product_specs` - Product requirements
- `hr_policies` - HR documents
- `legal` - Legal documents (restricted)
- `sales_materials` - Sales collateral

### 4. **Chunking Strategy**

Adjust chunk size based on document types:

```json
{
  "chunk_size": 500,      // For general docs
  "chunk_size": 1000,     // For technical docs
  "chunk_size": 200,      // For FAQs
  "chunk_overlap": 50     // Maintain context
}
```

### 5. **Regular Audits**

Review audit logs regularly:

```bash
/rag security audit-log --since 2025-01-01
```

### 6. **Backup Strategy**

Backup RAG data:

```bash
# Backup script
tar -czf aalap_rag_backup_$(date +%Y%m%d).tar.gz ~/.aalap/rag/
```

## Troubleshooting

### Issue: RAG not finding relevant documents

**Solution:**
1. Check similarity threshold: `/rag config similarity_threshold 0.2`
2. Increase top_k: `/rag config top_k 10`
3. Re-index with smaller chunks: `/rag config chunk_size 300`

### Issue: Slow query performance

**Solution:**
1. Use collection filters: `/rag search "query" --collections engineering`
2. Reduce top_k results
3. Consider using FAISS instead of ChromaDB for large datasets

### Issue: Out of memory errors

**Solution:**
1. Reduce batch size during indexing
2. Process documents in smaller batches
3. Increase system RAM or use pagination

### Issue: Access denied errors

**Solution:**
1. Check user authorization: `/rag security list-users`
2. Verify collection permissions: `/rag collections --show-restrictions`
3. Check org_id is correct

## Performance Optimization

### 1. **Use FAISS for Large Datasets**

For >100K documents, switch to FAISS:

```bash
pip install faiss-cpu
```

Update `rag_config.json`:
```json
{
  "vector_store": "faiss"
}
```

### 2. **Batch Indexing**

```bash
/rag index ~/docs --batch-size 100 --parallel 4
```

### 3. **Caching**

Enable query caching:

```json
{
  "cache_queries": true,
  "cache_ttl": 3600
}
```

## API Reference

### RAG Commands

| Command | Description |
|---------|-------------|
| `/rag enable` | Enable RAG context |
| `/rag disable` | Disable RAG context |
| `/rag status` | Show system status |
| `/rag index <path>` | Index files/directories |
| `/rag collections` | List collections |
| `/rag search <query>` | Search knowledge base |
| `/rag clear` | Clear all data |
| `/rag config <key> <value>` | Update configuration |

### Security Commands

| Command | Description |
|---------|-------------|
| `/rag security require-auth` | Enable authentication |
| `/rag security add-user <id>` | Add authorized user |
| `/rag security remove-user <id>` | Remove user |
| `/rag security restrict <collection>` | Restrict collection |
| `/rag security audit-log` | View audit log |
| `/rag security privacy-summary` | Show privacy settings |

## Advanced Topics

### Custom Embedding Models

Use different embedding models:

```python
# In rag.py
self.embedding_model = SentenceTransformer('all-mpnet-base-v2')  # More accurate
# or
self.embedding_model = SentenceTransformer('paraphrase-MiniLM-L3-v2')  # Faster
```

### Hybrid Search

Combine semantic and keyword search:

```json
{
  "search_strategy": "hybrid",
  "semantic_weight": 0.7,
  "keyword_weight": 0.3
}
```

### Custom Reranking

Implement domain-specific reranking:

```python
def custom_rerank(query, results):
    # Your reranking logic
    return reranked_results
```

## Compliance and Regulations

### GDPR Compliance

- ✅ Data stored locally
- ✅ User consent required
- ✅ Right to erasure supported (`/rag clear`)
- ✅ Data portability (export functionality)
- ✅ Audit logs maintained

### HIPAA Compliance

- ✅ Encryption at rest
- ✅ Access controls
- ✅ Audit trails
- ⚠️ Ensure BAA with Anthropic for Claude API usage

### SOC 2

- ✅ Access controls
- ✅ Encryption
- ✅ Monitoring and logging
- ✅ Change management

## Support

For issues or questions:
- GitHub Issues: https://github.com/caltycs/aalap/issues
- Email: info.caltycs@gmail.com
- Documentation: https://github.com/caltycs/aalap/wiki

## Roadmap

- [ ] Multi-modal support (images, audio)
- [ ] Real-time incremental indexing
- [ ] Advanced analytics and insights
- [ ] Federated search across multiple orgs
- [ ] GraphRAG for relationship-aware retrieval
- [ ] Fine-tuned embedding models per domain