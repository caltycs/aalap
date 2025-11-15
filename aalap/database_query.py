#!/usr/bin/env python3
"""
Database Query System for Aalap
Natural language to SQL conversion and execution with insights
"""

import json
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import sqlite3


class DatabaseQueryExecutor:
    """Execute natural language queries against databases"""

    def __init__(self, rag_instance, claude_client, config):
        """
        Initialize Database Query Executor

        Args:
            rag_instance: Instance of AalapRAG
            claude_client: Anthropic Claude client
            config: Configuration dict
        """
        self.rag = rag_instance
        self.claude = claude_client
        self.config = config
        self.active_connections = {}  # Store active database connections

    def register_database(self, name: str, db_type: str, connection_info: str):
        """
        Register a database for querying

        Args:
            name: Database alias/name
            db_type: Database type (sqlite, postgresql, mysql)
            connection_info: Connection string or path
        """
        self.active_connections[name] = {
            "type": db_type,
            "connection": connection_info
        }

    def natural_language_to_sql(
            self,
            question: str,
            database_name: Optional[str] = None,
            collection_name: str = "database"
    ) -> Tuple[str, List[Dict]]:
        """
        Convert natural language question to SQL query using RAG context

        Args:
            question: Natural language question
            database_name: Specific database name (for multi-db setups)
            collection_name: RAG collection to search

        Returns:
            (sql_query, sources) - Generated SQL and RAG sources used
        """
        # Retrieve relevant database schema from RAG
        print(f"   🔍 Searching for schema in '{collection_name}' collection...")
        rag_context, sources = self.rag.build_context(
            question,
            collections=[collection_name],
            max_tokens=4000
        )

        if not rag_context:
            print(f"   ⚠️  No schema found in RAG. Please check:")
            print(f"      1. Database is indexed: /rag db index sqlite <path>")
            print(f"      2. RAG has data: /rag status")
            print(f"      3. Search works: /rag search tables")
            return None, []

        print(f"   ✓ Found {len(sources)} relevant schema sources")

        # Create prompt for Claude to generate SQL
        system_prompt = """You are a SQL expert. Given database schema information and a natural language question, generate the appropriate SQL query.

CRITICAL RULES:
1. Output ONLY the SQL query - absolutely NO explanations, NO commentary, NO markdown
2. Do NOT start with phrases like "Based on", "Here's", "The query", etc.
3. Start immediately with SELECT, INSERT, UPDATE, DELETE, or other SQL keywords
4. Use proper SQL syntax for the database type
5. Be precise and efficient
6. Handle edge cases (NULL values, case sensitivity, etc.)
7. For counting queries, use COUNT(*)
8. For listing queries, use SELECT with appropriate columns
9. Add LIMIT clause for safety if listing all records

CORRECT: SELECT COUNT(*) FROM customers
WRONG: Based on the schema, the query is: SELECT COUNT(*) FROM customers

Output format: Just the raw SQL query, starting with a SQL keyword."""

        user_prompt = f"""Database Schema:
{rag_context}

Question: {question}

Generate the SQL query to answer this question:"""

        # Call Claude to generate SQL
        response = self.claude.messages.create(
            model=self.config.get("model", "claude-sonnet-4-20250514"),
            max_tokens=1000,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )

        # Extract SQL from response
        sql_query = ""
        for block in response.content:
            if block.type == "text":
                sql_query = block.text.strip()
                # Remove markdown code blocks if present
                if sql_query.startswith("```sql"):
                    sql_query = sql_query[6:]
                elif sql_query.startswith("```"):
                    sql_query = sql_query[3:]
                if sql_query.endswith("```"):
                    sql_query = sql_query[:-3]
                sql_query = sql_query.strip()

        # Extract only the SQL query (remove any explanatory text)
        # Look for common SQL keywords at the start
        sql_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'ALTER', 'DROP', 'WITH']
        lines = sql_query.split('\n')

        # Find the first line that starts with a SQL keyword
        for i, line in enumerate(lines):
            line_upper = line.strip().upper()
            if any(line_upper.startswith(keyword) for keyword in sql_keywords):
                # Join from this line to the end (or until we hit explanatory text)
                sql_query = '\n'.join(lines[i:])
                break

        # Remove any trailing explanation (text after the query)
        # SQL queries typically end with a semicolon or the last closing parenthesis
        if ';' in sql_query:
            sql_query = sql_query.split(';')[0] + ';'

        sql_query = sql_query.strip()

        return sql_query, sources

    def execute_query(
            self,
            sql_query: str,
            db_type: str,
            connection_info: str
    ) -> Tuple[List[Dict], List[str], Optional[str]]:
        """
        Execute SQL query against database

        Args:
            sql_query: SQL query to execute
            db_type: Database type
            connection_info: Connection string/path

        Returns:
            (results, columns, error) - Query results, column names, and any error
        """
        try:
            if db_type == "sqlite":
                return self._execute_sqlite(sql_query, connection_info)
            elif db_type == "postgresql":
                return self._execute_postgres(sql_query, connection_info)
            elif db_type == "mysql":
                return self._execute_mysql(sql_query, connection_info)
            else:
                return [], [], f"Unsupported database type: {db_type}"
        except Exception as e:
            return [], [], str(e)

    def _execute_sqlite(
            self,
            sql_query: str,
            db_path: str
    ) -> Tuple[List[Dict], List[str], Optional[str]]:
        """Execute query on SQLite database"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(sql_query)

            # Get column names
            columns = [desc[0] for desc in cursor.description] if cursor.description else []

            # Fetch results
            rows = cursor.fetchall()

            # Convert to list of dicts
            results = []
            for row in rows:
                result_dict = {}
                for i, col in enumerate(columns):
                    result_dict[col] = row[i]
                results.append(result_dict)

            conn.close()
            return results, columns, None

        except Exception as e:
            conn.close()
            return [], [], str(e)

    def _execute_postgres(
            self,
            sql_query: str,
            connection_string: str
    ) -> Tuple[List[Dict], List[str], Optional[str]]:
        """Execute query on PostgreSQL database"""
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor

            conn = psycopg2.connect(connection_string)
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            cursor.execute(sql_query)

            # Get column names
            columns = [desc[0] for desc in cursor.description] if cursor.description else []

            # Fetch results
            rows = cursor.fetchall()

            # Convert to list of dicts
            results = [dict(row) for row in rows]

            cursor.close()
            conn.close()

            return results, columns, None

        except ImportError:
            return [], [], "psycopg2 not installed. Run: pip install psycopg2-binary"
        except Exception as e:
            return [], [], str(e)

    def _execute_mysql(
            self,
            sql_query: str,
            connection_string: str
    ) -> Tuple[List[Dict], List[str], Optional[str]]:
        """Execute query on MySQL database"""
        try:
            import mysql.connector
            from urllib.parse import urlparse

            parsed = urlparse(connection_string)
            conn = mysql.connector.connect(
                host=parsed.hostname,
                port=parsed.port or 3306,
                user=parsed.username,
                password=parsed.password,
                database=parsed.path.lstrip('/')
            )

            cursor = conn.cursor(dictionary=True)
            cursor.execute(sql_query)

            # Get column names
            columns = cursor.column_names if cursor.column_names else []

            # Fetch results
            results = cursor.fetchall()

            cursor.close()
            conn.close()

            return results, list(columns), None

        except ImportError:
            return [], [], "mysql-connector-python not installed. Run: pip install mysql-connector-python"
        except Exception as e:
            return [], [], str(e)

    def generate_insights(
            self,
            question: str,
            sql_query: str,
            results: List[Dict],
            columns: List[str]
    ) -> str:
        """
        Generate insights from query results using Claude

        Args:
            question: Original question
            sql_query: SQL query that was executed
            results: Query results
            columns: Column names

        Returns:
            Insights and analysis
        """
        # Format results for Claude
        results_text = self._format_results_for_analysis(results, columns)

        system_prompt = """You are a data analyst. Given a question, SQL query, and results, provide clear insights and analysis.

Your response should:
1. Directly answer the original question
2. Highlight key findings from the data
3. Provide relevant statistics or patterns
4. Be clear and concise
5. Use bullet points for multiple insights
6. Avoid repeating the raw data unless necessary for context"""

        user_prompt = f"""Question: {question}

SQL Query: {sql_query}

Results:
{results_text}

Provide insights and analysis:"""

        response = self.claude.messages.create(
            model=self.config.get("model", "claude-sonnet-4-20250514"),
            max_tokens=2000,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )

        insights = ""
        for block in response.content:
            if block.type == "text":
                insights += block.text

        return insights

    def _format_results_for_analysis(
            self,
            results: List[Dict],
            columns: List[str],
            max_rows: int = 100
    ) -> str:
        """Format query results for Claude analysis"""
        if not results:
            return "No results found."

        # Limit rows for token efficiency
        limited_results = results[:max_rows]

        # Format as table
        text = f"Total rows: {len(results)}\n"
        if len(results) > max_rows:
            text += f"(Showing first {max_rows} rows)\n"
        text += "\n"

        # Create simple table format
        for i, row in enumerate(limited_results, 1):
            text += f"Row {i}:\n"
            for col in columns:
                text += f"  {col}: {row.get(col, 'NULL')}\n"
            text += "\n"

        return text

    def query(
            self,
            question: str,
            db_type: str,
            connection_info: str,
            collection_name: str = "database",
            explain: bool = False
    ) -> Dict[str, Any]:
        """
        Complete workflow: Natural language to SQL, execute, and provide insights

        Args:
            question: Natural language question
            db_type: Database type
            connection_info: Connection string/path
            collection_name: RAG collection name
            explain: Whether to show SQL query and execution details

        Returns:
            Dict with query, results, insights, and metadata
        """
        result = {
            "question": question,
            "sql_query": None,
            "results": [],
            "columns": [],
            "insights": None,
            "error": None,
            "sources": []
        }

        # Step 1: Convert natural language to SQL
        sql_query, sources = self.natural_language_to_sql(
            question,
            collection_name=collection_name
        )

        if not sql_query:
            result["error"] = "Could not generate SQL query. Make sure the database is indexed."
            return result

        result["sql_query"] = sql_query
        result["sources"] = sources

        # Step 2: Execute query
        results, columns, error = self.execute_query(
            sql_query,
            db_type,
            connection_info
        )

        if error:
            result["error"] = error
            return result

        result["results"] = results
        result["columns"] = columns

        # Step 3: Generate insights
        insights = self.generate_insights(
            question,
            sql_query,
            results,
            columns
        )

        result["insights"] = insights

        return result
