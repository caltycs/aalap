# Aalap Standard Operating Procedures (SOP) Manual

**Version:** 1.0
**Last Updated:** 2024
**Document Owner:** Aalap Development Team

---

## Table of Contents

1. [Introduction](#introduction)
2. [System Architecture](#system-architecture)
3. [Installation & Setup](#installation--setup)
4. [Core Operations](#core-operations)
5. [RAG System Operations](#rag-system-operations)
6. [Database Query Operations](#database-query-operations)
7. [MCP Server Management](#mcp-server-management)
8. [Troubleshooting Guide](#troubleshooting-guide)
9. [Maintenance Procedures](#maintenance-procedures)
10. [Security Procedures](#security-procedures)
11. [Backup & Recovery](#backup--recovery)

---

## 1. Introduction

### 1.1 Purpose
This Standard Operating Procedures (SOP) manual provides detailed, step-by-step instructions for operating Aalap - an intelligent command-line interface for Claude AI with RAG, Database Querying, and MCP server support.

### 1.2 Scope
This manual covers all operational aspects of Aalap including:
- Installation and configuration
- RAG (Retrieval-Augmented Generation) operations
- Database querying and indexing
- MCP server management
- Troubleshooting and maintenance

### 1.3 Intended Audience
- System Administrators
- DevOps Engineers
- Data Analysts
- Software Developers
- Technical Support Personnel

### 1.4 Prerequisites
- Basic command-line knowledge
- Understanding of databases (for database query features)
- Python 3.8 or higher installed
- Anthropic API key

---

## 2. System Architecture

### 2.1 Component Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Aalap CLI                             │
├─────────────────────────────────────────────────────────┤
│  Interactive Terminal  │  Command Processor             │
├────────────────────────┼────────────────────────────────┤
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  RAG Engine  │  │  DB Query    │  │  MCP Manager │  │
│  │              │  │  Executor    │  │              │  │
│  │  - ChromaDB  │  │  - Text2SQL  │  │  - Servers   │  │
│  │  - Embeddings│  │  - Insights  │  │  - Tools     │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                          │
├─────────────────────────────────────────────────────────┤
│              Anthropic Claude API                        │
└─────────────────────────────────────────────────────────┘

Storage:
~/.aalap/
├── config.json           # Configuration
├── rag/{org}/           # Knowledge bases
│   ├── chroma/          # Vector store
│   └── rag_config.json  # RAG settings
└── mcp_servers.json     # MCP configs
```

### 2.2 Data Flow

#### RAG-Enhanced Query Flow
```
User Query → RAG Retrieval → Context Building → Claude API → Response
                ↑
        Vector Database
```

#### Database Query Flow
```
Natural Language → Schema Retrieval → SQL Generation → Query Execution →
                                                             ↓
                                                        Insights Generation
```

---

## 3. Installation & Setup

### 3.1 Initial Installation

**Procedure ID:** INSTALL-001
**Frequency:** One-time
**Estimated Time:** 5-10 minutes

#### Steps:

1. **Verify Python Version**
   ```bash
   python3 --version
   # Expected: Python 3.8.0 or higher
   ```

2. **Install Aalap**
   ```bash
   # Method 1: Using pip
   pip install git+https://github.com/caltycs/aalap

   # Method 2: From source
   git clone https://github.com/caltycs/aalap.git
   cd aalap
   pip install -e .
   ```

3. **Verify Installation**
   ```bash
   aalap --version
   # Expected output: aalap version x.x.x
   ```

4. **Install Optional Dependencies**
   ```bash
   # For PostgreSQL support
   pip install psycopg2-binary

   # For MySQL support
   pip install mysql-connector-python

   # For PDF support (optional)
   pip install PyPDF2

   # For DOCX support (optional)
   pip install python-docx
   ```

**Success Criteria:**
- ✓ Aalap command is available
- ✓ Version displays correctly
- ✓ Optional dependencies installed (if needed)

---

### 3.2 API Key Configuration

**Procedure ID:** CONFIG-001
**Frequency:** One-time (or when key rotates)
**Estimated Time:** 2 minutes

#### Steps:

1. **Obtain API Key**
   - Navigate to https://console.anthropic.com/
   - Create or copy your API key
   - Format: `sk-ant-api03-...`

2. **Configure API Key**
   ```bash
   # Method 1: Interactive mode
   aalap
   /config apikey sk-ant-api03-YOUR_KEY_HERE

   # Method 2: Environment variable (recommended for CI/CD)
   export ANTHROPIC_API_KEY=sk-ant-api03-YOUR_KEY_HERE
   ```

3. **Verify Configuration**
   ```bash
   aalap
   /config
   # Expected: Shows masked API key and settings
   ```

4. **Set Secure Permissions**
   ```bash
   chmod 600 ~/.aalap/config.json
   ls -la ~/.aalap/config.json
   # Expected: -rw------- (600 permissions)
   ```

**Success Criteria:**
- ✓ API key is stored securely
- ✓ Configuration displays correctly
- ✓ File permissions are restrictive

---

## 4. Core Operations

### 4.1 Starting Aalap

**Procedure ID:** CORE-001
**Frequency:** As needed
**Estimated Time:** < 1 minute

#### Steps:

1. **Launch Interactive Mode**
   ```bash
   aalap
   ```

2. **Verify Successful Start**
   - ASCII art banner displays
   - Prompt shows: `💬 You:`
   - No error messages

3. **Check Configuration**
   ```
   /config
   ```
   - Verify API key is set
   - Check model version
   - Note organization ID

**Expected Output:**
```
╔════════════════════════════════════════════════════════════════╗
║              Interactive Claude AI Terminal                    ║
╚════════════════════════════════════════════════════════════════╝

Organization: default
Type /help for commands or start chatting!

💬 You:
```

---

### 4.2 Basic Chat Operations

**Procedure ID:** CORE-002
**Frequency:** Regular usage
**Estimated Time:** Varies

#### Steps:

1. **Send Message**
   - Type your question or message
   - Press Enter
   - Wait for Claude's response

2. **View Conversation History**
   ```
   /history
   ```

3. **Clear Context (Start Fresh)**
   ```
   /clear
   ```

4. **Exit Aalap**
   ```
   /exit
   # or
   /quit
   ```

**Best Practices:**
- Clear context when switching topics
- Use `/history` to review previous questions
- Keep questions focused and specific

---

## 5. RAG System Operations

### 5.1 Enabling RAG

**Procedure ID:** RAG-001
**Frequency:** Once per session or organization
**Estimated Time:** < 1 minute

#### Steps:

1. **Enable RAG Context**
   ```
   /rag enable
   ```
   Expected: `✓ RAG context enabled`

2. **Verify RAG Status**
   ```
   /rag status
   ```
   Expected output:
   ```
   📊 RAG System Status:
     Status: Enabled
     Organization: default
     Total Chunks: X
     Collections: [list of collections]
   ```

3. **Configure Auto-Context (Optional)**
   - Edit `~/.aalap/config.json`
   - Set `"rag_auto_context": true`

**Success Criteria:**
- ✓ RAG status shows "Enabled"
- ✓ System ready to use indexed knowledge

---

### 5.2 Indexing Documents

**Procedure ID:** RAG-002
**Frequency:** As needed when adding documentation
**Estimated Time:** Varies (depends on document size)

#### Steps:

1. **Index Single File**
   ```
   /rag index /path/to/document.md
   ```

2. **Index Directory (Recursive)**
   ```
   /rag index /path/to/documentation/
   ```

3. **Monitor Indexing Progress**
   - Watch for `✓ Indexed: filename` messages
   - Note any errors (files skipped)

4. **Verify Indexing**
   ```
   /rag status
   # Check that Total Chunks increased

   /rag collections
   # Verify collection exists with chunks
   ```

5. **Test Retrieval**
   ```
   /rag search <relevant keyword>
   # Should return indexed content
   ```

**Supported File Types:**
- Text: `.txt`, `.md`
- Code: `.py`, `.js`, `.java`, `.cpp`, `.c`, `.h`
- Documents: `.pdf`, `.docx` (with optional dependencies)

**Troubleshooting:**
- If files are skipped, check file permissions
- For unsupported types, install optional dependencies
- If no results in search, adjust similarity threshold

---

### 5.3 Managing Collections

**Procedure ID:** RAG-003
**Frequency:** As needed
**Estimated Time:** 1-2 minutes

#### Steps:

1. **List All Collections**
   ```
   /rag collections
   ```
   Expected output:
   ```
   📚 Available Collections:
     • documents (45 chunks)
     • code (123 chunks)
     • database (12 chunks)
   ```

2. **Search Within Collections**
   ```
   /rag search <query>
   ```
   - Reviews all collections by default
   - Returns ranked results with relevance scores

3. **Clear All Collections**
   ```
   /rag clear
   ```
   - Confirmation prompt appears
   - Type `yes` to confirm
   - **Warning:** This deletes all indexed data

**Best Practices:**
- Regularly review collections to avoid redundancy
- Use meaningful organization IDs for different projects
- Back up RAG data before clearing

---

### 5.4 Adjusting Search Sensitivity

**Procedure ID:** RAG-004
**Frequency:** As needed for tuning
**Estimated Time:** < 1 minute

#### Steps:

1. **Check Current Threshold**
   ```
   /rag status
   ```
   Look for similarity_threshold value

2. **Set New Threshold**
   ```
   /rag threshold 0.0
   ```
   - **0.0**: Accept all results (most permissive)
   - **0.3**: Medium filtering
   - **0.7**: Strict filtering (only very relevant)

3. **Test with Search**
   ```
   /rag search test query
   ```
   - Note how many results are filtered
   - Adjust threshold accordingly

4. **Monitor Filtering**
   - Output shows: `Note: X results filtered out`
   - If too many filtered: lower threshold
   - If too many irrelevant results: raise threshold

**Recommended Settings:**
- **Default**: 0.0 (recommended for most use cases)
- **Strict projects**: 0.3-0.5
- **Very specific queries**: 0.5-0.7

---

### 5.5 Organization Management

**Procedure ID:** RAG-005
**Frequency:** When working with multiple clients/projects
**Estimated Time:** < 1 minute

#### Steps:

1. **Set Organization ID**
   ```
   /config org project-alpha
   ```
   Expected: `✓ Organization set to project-alpha`

2. **Verify Isolation**
   ```
   /rag status
   ```
   - Organization should show "project-alpha"
   - Separate knowledge base from other orgs

3. **Switch Organizations**
   ```
   /config org client-beta
   ```
   - All RAG data now isolated to client-beta
   - Previous org data not accessible

4. **List Organization Data**
   ```bash
   # In terminal (outside Aalap)
   ls ~/.aalap/rag/
   # Shows all organization IDs
   ```

**Use Cases:**
- **Multiple clients**: Separate org per client
- **Project isolation**: Different org per project
- **Environment separation**: dev, staging, prod

---

## 6. Database Query Operations

### 6.1 Database Schema Indexing

**Procedure ID:** DB-001
**Frequency:** Once per database (or when schema changes)
**Estimated Time:** 1-5 minutes

#### Steps:

1. **Prepare Database Connection String**
   - SQLite: `/path/to/database.db`
   - PostgreSQL: `postgresql://user:password@host:port/database`
   - MySQL: `mysql://user:password@host:port/database`

2. **Index Database Schema**
   ```
   /rag db index <type> <connection> [options]
   ```

   Examples:
   ```
   # SQLite (basic)
   /rag db index sqlite ~/company.db

   # With sample data
   /rag db index sqlite ~/company.db --sample-data --sample-rows 5

   # Specific tables only
   /rag db index sqlite ~/company.db --tables customers,orders,products

   # PostgreSQL
   /rag db index postgresql postgresql://user:pass@localhost/mydb --sample-data

   # MySQL with custom collection
   /rag db index mysql mysql://user:pass@localhost/mydb --collection production
   ```

3. **Monitor Indexing Progress**
   Expected output:
   ```
   🔄 Indexing sqlite database...
      Connection: /path/to/db
      Collection: database
      Tables: All
      Sample data: Yes

   ✅ Database indexing complete!

   📊 Statistics:
      Database type: sqlite
      Collection: database
      Tables indexed: 5
      Schemas indexed: 6
      Sample data rows: 25
   ```

4. **Verify Indexing**
   ```
   /rag collections
   # Should show 'database' collection with chunks

   /rag search table
   # Should return database schema information
   ```

**Index Options:**
- `--collection <name>`: Custom collection name (default: "database")
- `--tables <t1,t2>`: Specific tables only (default: all)
- `--sample-data`: Include sample rows for context
- `--sample-rows <N>`: Number of sample rows (default: 5)

**Success Criteria:**
- ✓ All tables indexed successfully
- ✓ Schema searchable in RAG
- ✓ No errors in statistics output

---

### 6.2 Connecting to Database

**Procedure ID:** DB-002
**Frequency:** Once per session
**Estimated Time:** < 1 minute

#### Steps:

1. **Connect to Database**
   ```
   /db connect <type> <connection>
   ```

   Examples:
   ```
   /db connect sqlite ~/company.db
   /db connect postgresql postgresql://user:pass@localhost/mydb
   /db connect mysql mysql://user:pass@localhost/mydb
   ```

2. **Verify Connection**
   Expected output:
   ```
   ✓ Connected to sqlite database
     Connection: /path/to/database.db

   You can now query this database with: /db query <your question>
   ```

3. **Check Connection Status**
   ```
   /db status
   ```
   Expected:
   ```
   ✓ Connected to sqlite database
     Connection: /path/to/database.db
   ```

**Security Note:**
- Connection credentials are NOT stored permanently
- Re-enter connection string for each new session
- Use read-only database users when possible

---

### 6.3 Querying Database

**Procedure ID:** DB-003
**Frequency:** Regular usage
**Estimated Time:** Varies

#### Steps:

1. **Ensure Prerequisites**
   - ✓ Database schema is indexed (`/rag db index`)
   - ✓ Connected to database (`/db connect`)
   - ✓ RAG threshold is appropriate (recommend: 0.0)

2. **Ask Natural Language Question**
   ```
   /db query <your question>
   ```

   Examples:
   ```
   /db query how many customers do we have?
   /db query what are the top 10 products by revenue?
   /db query show me all orders from last month
   /db query what is the average order value by customer segment?
   ```

3. **Review Output**
   Expected format:
   ```
   🔍 Question: how many customers do we have?
   📊 Database: sqlite at /path/to/db
   ============================================================
      🔍 Searching for schema in 'database' collection...
      ✓ Found 2 relevant schema sources

   💡 Generated SQL:
      SELECT COUNT(*) FROM customers

   📈 Results: 1 row(s)

   📋 Data:
      Row 1:
         COUNT(*): 1,247

   ============================================================

   🤖 Insights:

   Your database currently contains 1,247 customers...

   ============================================================

   📚 Used 2 schema sources from knowledge base
   ```

4. **Validate Results**
   - Review generated SQL for correctness
   - Check results make sense
   - If SQL is wrong, rephrase question or check schema indexing

**Query Types Supported:**
- **Count queries**: "how many...", "count of..."
- **Aggregations**: "average", "sum", "max", "min"
- **Filtering**: "where", "from last month", "active users"
- **Sorting**: "top 10", "highest", "lowest"
- **Grouping**: "by category", "per customer"
- **Joins**: Complex multi-table queries

**Troubleshooting:**
- **No SQL generated**: Check database is indexed and RAG enabled
- **Wrong SQL**: Rephrase question or re-index with sample data
- **SQL syntax error**: Check database type matches connection
- **No results**: Verify database has data

---

### 6.4 Disconnecting from Database

**Procedure ID:** DB-004
**Frequency:** End of session or switching databases
**Estimated Time:** < 1 minute

#### Steps:

1. **Disconnect from Current Database**
   ```
   /db disconnect
   ```
   Expected: `✓ Disconnected from <type> database`

2. **Verify Disconnection**
   ```
   /db status
   ```
   Expected: `✗ No database connected`

3. **Connect to Different Database (Optional)**
   ```
   /db connect <type> <new_connection>
   ```

---

## 7. MCP Server Management

### 7.1 Installing MCP Server

**Procedure ID:** MCP-001
**Frequency:** As needed
**Estimated Time:** 2-5 minutes

#### Steps:

1. **Install MCP Server**
   ```
   /mcp install <name> <command> [--args ...] [--env {...}]
   ```

   Examples:
   ```
   # Filesystem access
   /mcp install filesystem npx --args @modelcontextprotocol/server-filesystem ~/Documents

   # GitHub integration
   /mcp install github npx --args @modelcontextprotocol/server-github \
     --env '{"GITHUB_TOKEN":"ghp_xxxxx"}'

   # Database access
   /mcp install postgres npx --args @modelcontextprotocol/server-postgres \
     --env '{"DATABASE_URL":"postgresql://localhost/mydb"}'
   ```

2. **Verify Installation**
   ```
   /mcp list
   ```
   Expected output shows installed server with command and args

**Success Criteria:**
- ✓ Server appears in `/mcp list`
- ✓ Configuration saved to `~/.aalap/mcp_servers.json`

---

### 7.2 Managing MCP Servers

**Procedure ID:** MCP-002
**Frequency:** As needed
**Estimated Time:** 1-2 minutes

#### Steps:

1. **List Installed Servers**
   ```
   /mcp list
   ```

2. **Remove MCP Server**
   ```
   /mcp remove <name>
   ```
   Expected: `✓ MCP server '<name>' removed successfully`

3. **Verify Removal**
   ```
   /mcp list
   # Server should no longer appear
   ```

---

## 8. Troubleshooting Guide

### 8.1 RAG Issues

#### Issue: "No results found" when searching

**Procedure ID:** TROUBLESHOOT-001

**Diagnosis Steps:**
1. Check if data is indexed:
   ```
   /rag status
   # Verify Total Chunks > 0
   ```

2. Check similarity threshold:
   ```
   /rag threshold 0.0
   # Lower threshold to accept more results
   ```

3. Search with different keywords:
   ```
   /rag search <different keyword>
   ```

**Resolution:**
- If Total Chunks = 0: Re-index documents
- If results filtered: Lower threshold
- If still no results: Check file paths and permissions

---

#### Issue: "RAG context not appearing in responses"

**Procedure ID:** TROUBLESHOOT-002

**Diagnosis Steps:**
1. Check if RAG is enabled:
   ```
   /rag status
   # Status should show "Enabled"
   ```

2. Enable if disabled:
   ```
   /rag enable
   ```

3. Verify auto-context setting:
   - Check `~/.aalap/config.json`
   - Ensure `"rag_auto_context": true`

**Resolution:**
- Enable RAG if disabled
- Set `rag_auto_context` to true in config
- Restart Aalap session

---

### 8.2 Database Query Issues

#### Issue: "Could not generate SQL query"

**Procedure ID:** TROUBLESHOOT-003

**Diagnosis Steps:**
1. Verify database is indexed:
   ```
   /rag status
   # Check for 'database' collection
   ```

2. Test schema search:
   ```
   /rag search table
   # Should return database schema
   ```

3. Check RAG threshold:
   ```
   /rag threshold 0.0
   ```

4. Verify RAG enabled:
   ```
   /rag status
   ```

**Resolution:**
- If not indexed: Run `/rag db index`
- If search fails: Lower similarity threshold
- If RAG disabled: Run `/rag enable`
- Reset database query executor: Change threshold to reset

---

#### Issue: "SQL syntax error" when executing query

**Procedure ID:** TROUBLESHOOT-004

**Diagnosis Steps:**
1. Review generated SQL carefully
2. Verify database type matches connection
3. Check if table/column names are correct

**Resolution:**
- Rephrase question more clearly
- Re-index with sample data for better context:
  ```
  /rag db index <type> <connection> --sample-data
  ```
- Manually verify table names in database

---

### 8.3 Connection Issues

#### Issue: "API Error" or authentication failures

**Procedure ID:** TROUBLESHOOT-005

**Diagnosis Steps:**
1. Verify API key:
   ```
   /config
   # Check if API key is set
   ```

2. Test API key externally (optional):
   ```bash
   curl https://api.anthropic.com/v1/messages \
     -H "x-api-key: $ANTHROPIC_API_KEY" \
     -H "anthropic-version: 2023-06-01"
   ```

**Resolution:**
- If key missing: Set with `/config apikey <key>`
- If key invalid: Obtain new key from Anthropic console
- If network issues: Check firewall/proxy settings

---

## 9. Maintenance Procedures

### 9.1 Regular Maintenance

**Procedure ID:** MAINT-001
**Frequency:** Monthly
**Estimated Time:** 15-30 minutes

#### Tasks:

1. **Review and Clean RAG Data**
   ```bash
   # Check RAG data size
   du -sh ~/.aalap/rag/

   # List organizations
   ls ~/.aalap/rag/

   # Remove unused organizations
   rm -rf ~/.aalap/rag/old-org-id/
   ```

2. **Update Aalap**
   ```bash
   pip install --upgrade git+https://github.com/caltycs/aalap
   ```

3. **Review Configuration**
   ```bash
   cat ~/.aalap/config.json
   # Verify settings are current
   ```

4. **Update Database Schemas** (if changed)
   ```
   # In Aalap
   /rag db index <type> <connection>
   ```

5. **Test Core Functionality**
   - Test basic chat
   - Test RAG search
   - Test database query

---

### 9.2 Performance Optimization

**Procedure ID:** MAINT-002
**Frequency:** As needed
**Estimated Time:** 10-15 minutes

#### Steps:

1. **Optimize RAG Chunk Size**
   - Edit `~/.aalap/rag/{org}/rag_config.json`
   - Adjust `chunk_size` (default: 500)
   - Smaller chunks = more precise, larger storage
   - Larger chunks = less precise, smaller storage

2. **Adjust Context Token Limit**
   - Edit `rag_config.json`
   - Set `max_context_tokens` (default: 3000)
   - Higher = more context, slower responses
   - Lower = less context, faster responses

3. **Tune Similarity Threshold**
   ```
   /rag threshold <value>
   ```
   - Find optimal balance between recall and precision

4. **Clean ChromaDB**
   ```bash
   # Warning: Deletes all RAG data
   rm -rf ~/.aalap/rag/{org}/chroma/
   # Re-index after cleaning
   ```

---

## 10. Security Procedures

### 10.1 API Key Rotation

**Procedure ID:** SECURITY-001
**Frequency:** Every 90 days (recommended)
**Estimated Time:** 5 minutes

#### Steps:

1. **Generate New API Key**
   - Login to https://console.anthropic.com/
   - Create new API key
   - Copy key securely

2. **Update Configuration**
   ```
   /config apikey sk-ant-api03-NEW_KEY_HERE
   ```

3. **Test New Key**
   ```
   Hello, can you respond?
   # Verify Claude responds normally
   ```

4. **Revoke Old Key**
   - In Anthropic console
   - Delete or disable old key

5. **Secure File Permissions**
   ```bash
   chmod 600 ~/.aalap/config.json
   ```

---

### 10.2 Data Privacy Audit

**Procedure ID:** SECURITY-002
**Frequency:** Quarterly
**Estimated Time:** 15-20 minutes

#### Checklist:

1. **Review Indexed Data**
   ```bash
   # Check what's indexed
   ls -lah ~/.aalap/rag/*/
   ```
   - Identify sensitive data
   - Remove if necessary

2. **Verify File Permissions**
   ```bash
   ls -la ~/.aalap/
   # All files should be -rw------- (600)
   ```

3. **Check Database Connection Logs**
   - Verify credentials not stored in logs
   - Review connection strings used

4. **Review Sample Data Indexing**
   - Ensure no PII in sample data
   - Re-index without `--sample-data` if needed

5. **Audit Organization Isolation**
   ```bash
   # Verify orgs are separate
   du -sh ~/.aalap/rag/*/
   ```

---

## 11. Backup & Recovery

### 11.1 Backing Up RAG Data

**Procedure ID:** BACKUP-001
**Frequency:** Weekly (or before major changes)
**Estimated Time:** 5-10 minutes

#### Steps:

1. **Create Backup Directory**
   ```bash
   mkdir -p ~/aalap-backups/$(date +%Y%m%d)
   ```

2. **Backup RAG Data**
   ```bash
   cp -r ~/.aalap/rag ~/aalap-backups/$(date +%Y%m%d)/
   ```

3. **Backup Configuration**
   ```bash
   cp ~/.aalap/config.json ~/aalap-backups/$(date +%Y%m%d)/
   cp ~/.aalap/mcp_servers.json ~/aalap-backups/$(date +%Y%m%d)/
   ```

4. **Compress Backup**
   ```bash
   cd ~/aalap-backups
   tar -czf aalap-backup-$(date +%Y%m%d).tar.gz $(date +%Y%m%d)/
   ```

5. **Verify Backup**
   ```bash
   tar -tzf aalap-backup-$(date +%Y%m%d).tar.gz | head
   # Should list files
   ```

---

### 11.2 Restoring from Backup

**Procedure ID:** RECOVERY-001
**Frequency:** As needed
**Estimated Time:** 5-10 minutes

#### Steps:

1. **Stop Aalap** (if running)

2. **Extract Backup**
   ```bash
   cd ~/aalap-backups
   tar -xzf aalap-backup-YYYYMMDD.tar.gz
   ```

3. **Restore RAG Data**
   ```bash
   cp -r ~/aalap-backups/YYYYMMDD/rag ~/.aalap/
   ```

4. **Restore Configuration**
   ```bash
   cp ~/aalap-backups/YYYYMMDD/config.json ~/.aalap/
   cp ~/aalap-backups/YYYYMMDD/mcp_servers.json ~/.aalap/
   ```

5. **Set Permissions**
   ```bash
   chmod 600 ~/.aalap/config.json
   chmod -R 700 ~/.aalap/rag/
   ```

6. **Verify Restoration**
   ```bash
   aalap
   /rag status
   # Should show restored data
   ```

**Success Criteria:**
- ✓ RAG data restored
- ✓ Configuration functional
- ✓ Permissions secure

---

## Appendix A: Command Reference

### Core Commands
| Command | Purpose | Example |
|---------|---------|---------|
| `/help` | Show help | `/help` |
| `/clear` | Clear history | `/clear` |
| `/history` | View history | `/history` |
| `/config` | View/set config | `/config apikey <key>` |
| `/exit` | Exit Aalap | `/exit` |

### RAG Commands
| Command | Purpose | Example |
|---------|---------|---------|
| `/rag enable` | Enable RAG | `/rag enable` |
| `/rag disable` | Disable RAG | `/rag disable` |
| `/rag status` | Show status | `/rag status` |
| `/rag index` | Index file/dir | `/rag index ~/docs/` |
| `/rag collections` | List collections | `/rag collections` |
| `/rag search` | Search RAG | `/rag search auth` |
| `/rag threshold` | Set threshold | `/rag threshold 0.0` |
| `/rag clear` | Clear data | `/rag clear` |
| `/rag db index` | Index database | `/rag db index sqlite ~/db.db` |

### Database Commands
| Command | Purpose | Example |
|---------|---------|---------|
| `/db connect` | Connect to DB | `/db connect sqlite ~/db` |
| `/db query` | Query database | `/db query how many users?` |
| `/db status` | Connection status | `/db status` |
| `/db disconnect` | Disconnect | `/db disconnect` |

### MCP Commands
| Command | Purpose | Example |
|---------|---------|---------|
| `/mcp list` | List servers | `/mcp list` |
| `/mcp install` | Install server | `/mcp install fs npx ...` |
| `/mcp remove` | Remove server | `/mcp remove fs` |

---

## Appendix B: Error Codes

| Code | Meaning | Resolution |
|------|---------|------------|
| `API-001` | Invalid API key | Reset API key |
| `RAG-001` | Index not found | Re-index documents |
| `RAG-002` | Threshold too high | Lower threshold |
| `DB-001` | Connection failed | Check credentials |
| `DB-002` | SQL generation failed | Re-index schema |
| `DB-003` | Query execution error | Review SQL syntax |

---

## Appendix C: Configuration Parameters

### config.json Parameters
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `api_key` | string | - | Anthropic API key |
| `model` | string | claude-sonnet-4-20250514 | Claude model |
| `max_tokens` | number | 4096 | Max response tokens |
| `rag_enabled` | boolean | false | Enable RAG |
| `rag_auto_context` | boolean | true | Auto-inject context |
| `rag_collections` | array | [] | Collections to search |

### rag_config.json Parameters
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_context_tokens` | number | 3000 | Max RAG context |
| `top_k_results` | number | 5 | Results to retrieve |
| `similarity_threshold` | number | 0.0 | Similarity cutoff |
| `chunk_size` | number | 500 | Document chunk size |
| `chunk_overlap` | number | 50 | Chunk overlap |
| `rerank` | boolean | true | Re-rank results |

---

## Document Control

**Version History:**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2024 | Aalap Team | Initial release |

**Review Schedule:** Quarterly

**Next Review Date:** [To be determined]

---

**END OF SOP MANUAL**
