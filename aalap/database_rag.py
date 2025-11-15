#!/usr/bin/env python3
"""
Database RAG Integration for Aalap
Index database schemas, documentation, and sample data
"""

import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from pathlib import Path

class DatabaseRAG:
    """Index and query database content for RAG"""

    def __init__(self, rag_instance):
        """
        Initialize Database RAG

        Args:
            rag_instance: Instance of AalapRAG
        """
        self.rag = rag_instance
        self.supported_dbs = ['postgresql', 'mysql', 'sqlite', 'mongodb']

    def connect_postgres(self, connection_string: str):
        """Connect to PostgreSQL database"""
        try:
            import psycopg2
            from psycopg2 import sql
            return psycopg2.connect(connection_string)
        except ImportError:
            raise ImportError("psycopg2 not installed. Run: pip install psycopg2-binary")

    def connect_mysql(self, connection_string: str):
        """Connect to MySQL database"""
        try:
            import mysql.connector
            from urllib.parse import urlparse

            parsed = urlparse(connection_string)
            return mysql.connector.connect(
                host=parsed.hostname,
                port=parsed.port or 3306,
                user=parsed.username,
                password=parsed.password,
                database=parsed.path.lstrip('/')
            )
        except ImportError:
            raise ImportError("mysql-connector-python not installed. Run: pip install mysql-connector-python")

    def connect_sqlite(self, db_path: str):
        """Connect to SQLite database"""
        import sqlite3
        return sqlite3.connect(db_path)

    def index_postgres_database(
            self,
            connection_string: str,
            collection_name: str = "database",
            tables: Optional[List[str]] = None,
            include_sample_data: bool = False,
            sample_rows: int = 5
    ) -> Dict:
        """
        Index PostgreSQL database schema and optionally sample data

        Args:
            connection_string: PostgreSQL connection string
            collection_name: Collection name for indexing
            tables: Specific tables to index (None = all)
            include_sample_data: Whether to include sample rows
            sample_rows: Number of sample rows per table

        Returns:
            Statistics about indexing
        """
        conn = self.connect_postgres(connection_string)
        cursor = conn.cursor()

        stats = {
            "database_type": "postgresql",
            "collection": collection_name,
            "tables_indexed": 0,
            "schemas_indexed": 0,
            "sample_data_rows": 0,
            "errors": []
        }

        try:
            # Get database name
            cursor.execute("SELECT current_database();")
            db_name = cursor.fetchone()[0]

            # Get all tables if not specified
            if not tables:
                cursor.execute("""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_type = 'BASE TABLE'
                """)
                tables = [row[0] for row in cursor.fetchall()]

            # Create database overview document
            overview_content = f"# Database Overview: {db_name}\n\n"
            overview_content += f"This is a PostgreSQL database named '{db_name}'.\n\n"
            overview_content += "## All Tables in this Database:\n\n"
            for table in tables:
                overview_content += f"- **{table}**: Table containing {table} data\n"
            overview_content += f"\n**Total tables**: {len(tables)}\n\n"
            overview_content += f"**Available tables**: {', '.join(tables)}\n\n"
            overview_content += "You can query any of these tables to get information, count records, or analyze data.\n"
            overview_content += f"Database: {db_name}\n"

            # Index overview document
            overview_metadata = {
                "source": f"database:{db_name}",
                "table": "_DATABASE_OVERVIEW",
                "type": "overview",
                "database_type": "postgresql",
                "indexed_at": datetime.now().isoformat()
            }

            if self.rag.index_document(
                    collection_name,
                    overview_content,
                    overview_metadata,
                    doc_id=f"overview_postgres_{db_name}"
            ):
                stats["schemas_indexed"] += 1

            for table in tables:
                try:
                    # Get table schema
                    schema_content = self._get_postgres_table_schema(cursor, table)

                    # Index schema
                    metadata = {
                        "source": f"database:{db_name}",
                        "table": table,
                        "type": "schema",
                        "database_type": "postgresql",
                        "indexed_at": datetime.now().isoformat()
                    }

                    if self.rag.index_document(
                            collection_name,
                            schema_content,
                            metadata,
                            doc_id=f"schema_{db_name}_{table}"
                    ):
                        stats["tables_indexed"] += 1
                        stats["schemas_indexed"] += 1

                    # Index sample data if requested
                    if include_sample_data:
                        sample_content = self._get_postgres_sample_data(
                            cursor, table, sample_rows
                        )

                        if sample_content:
                            sample_metadata = {
                                "source": f"database:{db_name}",
                                "table": table,
                                "type": "sample_data",
                                "database_type": "postgresql",
                                "indexed_at": datetime.now().isoformat()
                            }

                            if self.rag.index_document(
                                    collection_name,
                                    sample_content,
                                    sample_metadata,
                                    doc_id=f"data_{db_name}_{table}"
                            ):
                                stats["sample_data_rows"] += sample_rows

                except Exception as e:
                    stats["errors"].append(f"Error indexing table {table}: {e}")

        finally:
            cursor.close()
            conn.close()

        return stats

    def _get_postgres_table_schema(self, cursor, table: str) -> str:
        """Get PostgreSQL table schema as text"""
        # Get columns
        cursor.execute("""
            SELECT 
                column_name,
                data_type,
                character_maximum_length,
                is_nullable,
                column_default
            FROM information_schema.columns
            WHERE table_name = %s
            ORDER BY ordinal_position
        """, (table,))

        columns = cursor.fetchall()

        # Get indexes
        cursor.execute("""
            SELECT indexname, indexdef
            FROM pg_indexes
            WHERE tablename = %s
        """, (table,))

        indexes = cursor.fetchall()

        # Get foreign keys
        cursor.execute("""
            SELECT
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_name = %s
        """, (table,))

        foreign_keys = cursor.fetchall()

        # Format as readable text with query-friendly context
        content = f"# Database Table: {table}\n\n"
        content += f"This table stores information about {table}. "
        content += f"You can query this table to get information about {table}, count records, or analyze data.\n\n"
        content += "## Schema\n\n"
        content += "| Column | Type | Nullable | Default |\n"
        content += "|--------|------|----------|----------|\n"

        column_names = []
        for col in columns:
            col_name, data_type, max_len, nullable, default = col
            column_names.append(col_name)
            type_str = f"{data_type}"
            if max_len:
                type_str += f"({max_len})"
            content += f"| {col_name} | {type_str} | {nullable} | {default or 'None'} |\n"

        # Add searchable column list
        content += f"\n## Available Columns\n"
        content += f"Columns in this table: {', '.join(column_names)}\n"
        content += f"\nTo count records in {table}, use: SELECT COUNT(*) FROM {table}\n"
        content += f"To query all data from {table}, use: SELECT * FROM {table}\n"

        if indexes:
            content += "\n## Indexes\n\n"
            for idx_name, idx_def in indexes:
                content += f"- {idx_name}: {idx_def}\n"

        if foreign_keys:
            content += "\n## Foreign Keys\n\n"
            for fk in foreign_keys:
                col, foreign_table, foreign_col = fk
                content += f"- {col} -> {foreign_table}.{foreign_col}\n"

        return content

    def _get_postgres_sample_data(
            self,
            cursor,
            table: str,
            limit: int
    ) -> str:
        """Get sample data from PostgreSQL table"""
        try:
            cursor.execute(f"SELECT * FROM {table} LIMIT %s", (limit,))
            rows = cursor.fetchall()

            if not rows:
                return ""

            # Get column names
            col_names = [desc[0] for desc in cursor.description]

            content = f"# Sample Data: {table}\n\n"
            content += "Sample rows from this table:\n\n"

            for row in rows:
                content += "{\n"
                for col_name, value in zip(col_names, row):
                    content += f"  {col_name}: {value}\n"
                content += "}\n\n"

            return content

        except Exception as e:
            return f"Error fetching sample data: {e}"

    def index_sqlite_database(
            self,
            db_path: str,
            collection_name: str = "database",
            tables: Optional[List[str]] = None,
            include_sample_data: bool = False,
            sample_rows: int = 5
    ) -> Dict:
        """
        Index SQLite database schema and optionally sample data

        Args:
            db_path: Path to SQLite database file
            collection_name: Collection name for indexing
            tables: Specific tables to index (None = all)
            include_sample_data: Whether to include sample rows
            sample_rows: Number of sample rows per table

        Returns:
            Statistics about indexing
        """
        conn = self.connect_sqlite(db_path)
        cursor = conn.cursor()

        stats = {
            "database_type": "sqlite",
            "database_path": db_path,
            "collection": collection_name,
            "tables_indexed": 0,
            "schemas_indexed": 0,
            "sample_data_rows": 0,
            "errors": []
        }

        try:
            # Get all tables if not specified
            if not tables:
                cursor.execute("""
                    SELECT name FROM sqlite_master
                    WHERE type='table' AND name NOT LIKE 'sqlite_%'
                """)
                tables = [row[0] for row in cursor.fetchall()]

            # Create database overview document
            db_name = Path(db_path).stem
            overview_content = f"# Database Overview: {db_name}\n\n"
            overview_content += f"This is a SQLite database located at '{db_path}'.\n\n"
            overview_content += "## All Tables in this Database:\n\n"
            for table in tables:
                overview_content += f"- **{table}**: Table containing {table} data\n"
            overview_content += f"\n**Total tables**: {len(tables)}\n\n"
            overview_content += f"**Available tables**: {', '.join(tables)}\n\n"
            overview_content += "You can query any of these tables to get information, count records, or analyze data.\n"
            overview_content += f"Database file: {db_path}\n"

            # Index overview document
            overview_metadata = {
                "source": f"database:{db_path}",
                "table": "_DATABASE_OVERVIEW",
                "type": "overview",
                "database_type": "sqlite",
                "indexed_at": datetime.now().isoformat()
            }

            if self.rag.index_document(
                    collection_name,
                    overview_content,
                    overview_metadata,
                    doc_id=f"overview_sqlite_{db_name}"
            ):
                stats["schemas_indexed"] += 1

            for table in tables:
                try:
                    # Get table schema
                    schema_content = self._get_sqlite_table_schema(cursor, table)

                    # Index schema
                    metadata = {
                        "source": f"database:{db_path}",
                        "table": table,
                        "type": "schema",
                        "database_type": "sqlite",
                        "indexed_at": datetime.now().isoformat()
                    }

                    if self.rag.index_document(
                            collection_name,
                            schema_content,
                            metadata,
                            doc_id=f"schema_sqlite_{table}"
                    ):
                        stats["tables_indexed"] += 1
                        stats["schemas_indexed"] += 1

                    # Index sample data if requested
                    if include_sample_data:
                        sample_content = self._get_sqlite_sample_data(
                            cursor, table, sample_rows
                        )

                        if sample_content:
                            sample_metadata = {
                                "source": f"database:{db_path}",
                                "table": table,
                                "type": "sample_data",
                                "database_type": "sqlite",
                                "indexed_at": datetime.now().isoformat()
                            }

                            if self.rag.index_document(
                                    collection_name,
                                    sample_content,
                                    sample_metadata,
                                    doc_id=f"data_sqlite_{table}"
                            ):
                                stats["sample_data_rows"] += sample_rows

                except Exception as e:
                    stats["errors"].append(f"Error indexing table {table}: {e}")

        finally:
            cursor.close()
            conn.close()

        return stats

    def _get_sqlite_table_schema(self, cursor, table: str) -> str:
        """Get SQLite table schema as text"""
        # Get table info
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()

        # Get indexes
        cursor.execute(f"PRAGMA index_list({table})")
        indexes = cursor.fetchall()

        # Format as readable text with query-friendly context
        content = f"# Database Table: {table}\n\n"
        content += f"This table stores information about {table}. "
        content += f"You can query this table to get information about {table}, count records, or analyze data.\n\n"
        content += "## Schema\n\n"
        content += "| Column | Type | Nullable | Default | Primary Key |\n"
        content += "|--------|------|----------|---------|-------------|\n"

        column_names = []
        for col in columns:
            cid, name, col_type, not_null, default_val, pk = col
            column_names.append(name)
            nullable = "NO" if not_null else "YES"
            is_pk = "YES" if pk else "NO"
            content += f"| {name} | {col_type} | {nullable} | {default_val or 'None'} | {is_pk} |\n"

        # Add searchable column list
        content += f"\n## Available Columns\n"
        content += f"Columns in this table: {', '.join(column_names)}\n"
        content += f"\nTo count records in {table}, use: SELECT COUNT(*) FROM {table}\n"
        content += f"To query all data from {table}, use: SELECT * FROM {table}\n"

        if indexes:
            content += "\n## Indexes\n\n"
            for idx in indexes:
                idx_seq, idx_name, is_unique, origin, partial = idx
                unique_str = "UNIQUE" if is_unique else "INDEX"
                content += f"- {idx_name} ({unique_str})\n"

        return content

    def _get_sqlite_sample_data(
            self,
            cursor,
            table: str,
            limit: int
    ) -> str:
        """Get sample data from SQLite table"""
        try:
            cursor.execute(f"SELECT * FROM {table} LIMIT ?", (limit,))
            rows = cursor.fetchall()

            if not rows:
                return ""

            # Get column names
            col_names = [desc[0] for desc in cursor.description]

            content = f"# Sample Data: {table}\n\n"
            content += "Sample rows from this table:\n\n"

            for row in rows:
                content += "{\n"
                for col_name, value in zip(col_names, row):
                    content += f"  {col_name}: {value}\n"
                content += "}\n\n"

            return content

        except Exception as e:
            return f"Error fetching sample data: {e}"

    def index_mysql_database(
            self,
            connection_string: str,
            collection_name: str = "database",
            tables: Optional[List[str]] = None,
            include_sample_data: bool = False,
            sample_rows: int = 5
    ) -> Dict:
        """
        Index MySQL database schema and optionally sample data

        Args:
            connection_string: MySQL connection string
            collection_name: Collection name for indexing
            tables: Specific tables to index (None = all)
            include_sample_data: Whether to include sample rows
            sample_rows: Number of sample rows per table

        Returns:
            Statistics about indexing
        """
        conn = self.connect_mysql(connection_string)
        cursor = conn.cursor()

        stats = {
            "database_type": "mysql",
            "collection": collection_name,
            "tables_indexed": 0,
            "schemas_indexed": 0,
            "sample_data_rows": 0,
            "errors": []
        }

        try:
            # Get database name
            cursor.execute("SELECT DATABASE()")
            db_name = cursor.fetchone()[0]

            # Get all tables if not specified
            if not tables:
                cursor.execute("SHOW TABLES")
                tables = [row[0] for row in cursor.fetchall()]

            # Create database overview document
            overview_content = f"# Database Overview: {db_name}\n\n"
            overview_content += f"This is a MySQL database named '{db_name}'.\n\n"
            overview_content += "## All Tables in this Database:\n\n"
            for table in tables:
                overview_content += f"- **{table}**: Table containing {table} data\n"
            overview_content += f"\n**Total tables**: {len(tables)}\n\n"
            overview_content += f"**Available tables**: {', '.join(tables)}\n\n"
            overview_content += "You can query any of these tables to get information, count records, or analyze data.\n"
            overview_content += f"Database: {db_name}\n"

            # Index overview document
            overview_metadata = {
                "source": f"database:{db_name}",
                "table": "_DATABASE_OVERVIEW",
                "type": "overview",
                "database_type": "mysql",
                "indexed_at": datetime.now().isoformat()
            }

            if self.rag.index_document(
                    collection_name,
                    overview_content,
                    overview_metadata,
                    doc_id=f"overview_mysql_{db_name}"
            ):
                stats["schemas_indexed"] += 1

            for table in tables:
                try:
                    # Get table schema
                    cursor.execute(f"DESCRIBE {table}")
                    columns = cursor.fetchall()

                    # Format schema with query-friendly context
                    content = f"# Database Table: {table}\n\n"
                    content += f"This table stores information about {table}. "
                    content += f"You can query this table to get information about {table}, count records, or analyze data.\n\n"
                    content += "## Schema\n\n"
                    content += "| Column | Type | Nullable | Key | Default | Extra |\n"
                    content += "|--------|------|----------|-----|---------|-------|\n"

                    column_names = []
                    for col in columns:
                        field, col_type, null, key, default, extra = col
                        column_names.append(field)
                        content += f"| {field} | {col_type} | {null} | {key or 'None'} | {default or 'None'} | {extra or 'None'} |\n"

                    # Add searchable column list
                    content += f"\n## Available Columns\n"
                    content += f"Columns in this table: {', '.join(column_names)}\n"
                    content += f"\nTo count records in {table}, use: SELECT COUNT(*) FROM {table}\n"
                    content += f"To query all data from {table}, use: SELECT * FROM {table}\n"

                    # Index schema
                    metadata = {
                        "source": f"database:{db_name}",
                        "table": table,
                        "type": "schema",
                        "database_type": "mysql",
                        "indexed_at": datetime.now().isoformat()
                    }

                    if self.rag.index_document(
                            collection_name,
                            content,
                            metadata,
                            doc_id=f"schema_{db_name}_{table}"
                    ):
                        stats["tables_indexed"] += 1
                        stats["schemas_indexed"] += 1

                    # Index sample data if requested
                    if include_sample_data:
                        cursor.execute(f"SELECT * FROM {table} LIMIT {sample_rows}")
                        rows = cursor.fetchall()

                        if rows:
                            # Get column names
                            col_names = [desc[0] for desc in cursor.description]

                            sample_content = f"# Sample Data: {table}\n\n"
                            sample_content += "Sample rows from this table:\n\n"

                            for row in rows:
                                sample_content += "{\n"
                                for col_name, value in zip(col_names, row):
                                    sample_content += f"  {col_name}: {value}\n"
                                sample_content += "}\n\n"

                            sample_metadata = {
                                "source": f"database:{db_name}",
                                "table": table,
                                "type": "sample_data",
                                "database_type": "mysql",
                                "indexed_at": datetime.now().isoformat()
                            }

                            if self.rag.index_document(
                                    collection_name,
                                    sample_content,
                                    sample_metadata,
                                    doc_id=f"data_{db_name}_{table}"
                            ):
                                stats["sample_data_rows"] += sample_rows

                except Exception as e:
                    stats["errors"].append(f"Error indexing table {table}: {e}")

        finally:
            cursor.close()
            conn.close()

        return stats