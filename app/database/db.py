"""Database management and initialization."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Generator

from app.exceptions import DatabaseError
from app.logger import get_logger

logger = get_logger(__name__)


class DatabaseManager:
    """Manages database connections and schema initialization."""

    def __init__(self, db_path: Path) -> None:
        """Initialize database manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self._db_path = db_path

    def init_db(self) -> None:
        """Initialize database schema and create tables if they don't exist.
        
        Raises:
            DatabaseError: If schema initialization fails
        """
        try:
            with sqlite3.connect(self._db_path) as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS expenses(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT NOT NULL,
                        amount REAL NOT NULL,
                        category TEXT NOT NULL,
                        subcategory TEXT DEFAULT '',
                        note TEXT DEFAULT '',
                        usd_amount REAL DEFAULT NULL,
                        original_currency TEXT DEFAULT NULL
                    )
                    """
                )
                conn.commit()
                logger.info(f"Database initialized at {self._db_path}")
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to initialize database: {e}") from e

    def get_connection(self) -> sqlite3.Connection:
        """Get a database connection.
        
        Returns:
            SQLite connection object
            
        Raises:
            DatabaseError: If connection fails
        """
        try:
            conn = sqlite3.connect(self._db_path)
            conn.row_factory = sqlite3.Row  # Return rows as dictionaries
            return conn
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to connect to database: {e}") from e

    def execute_query(
        self, query: str, params: tuple = ()
    ) -> list[dict]:
        """Execute a SELECT query and return results.
        
        Args:
            query: SQL SELECT query
            params: Query parameters
            
        Returns:
            List of result rows as dictionaries
            
        Raises:
            DatabaseError: If query execution fails
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise DatabaseError(f"Query execution failed: {e}") from e

    def execute_insert(self, query: str, params: tuple = ()) -> int:
        """Execute an INSERT query and return the last inserted row ID.
        
        Args:
            query: SQL INSERT query
            params: Query parameters
            
        Returns:
            Last inserted row ID
            
        Raises:
            DatabaseError: If insert fails
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(query, params)
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            raise DatabaseError(f"Insert failed: {e}") from e
