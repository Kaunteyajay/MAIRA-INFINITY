"""
Database Management

SQLite database with async support and automatic migrations.
"""

import logging
import aiosqlite
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Async SQLite database manager."""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._db: Optional[aiosqlite.Connection] = None
    
    async def initialize(self) -> None:
        """Initialize database connection and create tables."""
        logger.info(f"Initializing database: {self.db_path}")
        
        # Ensure parent directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Connect with WAL mode for better concurrency
        self._db = await aiosqlite.connect(
            self.db_path,
            isolation_level=None  # Autocommit mode
        )
        
        # Enable WAL mode and foreign keys
        await self._db.execute("PRAGMA journal_mode=WAL")
        await self._db.execute("PRAGMA foreign_keys=ON")
        
        # Create tables
        await self._create_tables()
        
        logger.info("Database initialized successfully")
    
    async def close(self) -> None:
        """Close database connection."""
        if self._db:
            await self._db.close()
            self._db = None
            logger.info("Database connection closed")
    
    async def _create_tables(self) -> None:
        """Create database tables."""
        
        # Conversations table
        await self._db.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                module TEXT NOT NULL DEFAULT 'chat',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Messages table
        await self._db.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('system', 'user', 'assistant', 'tool')),
                content TEXT NOT NULL,
                tool_calls_json TEXT,
                tokens INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations (id) ON DELETE CASCADE
            )
        """)
        
        # Tasks table
        await self._db.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                task_type TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                progress REAL DEFAULT 0.0,
                started_at TIMESTAMP,
                finished_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Activity log table
        await self._db.execute("""
            CREATE TABLE IF NOT EXISTS activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                action TEXT NOT NULL,
                status TEXT NOT NULL,
                details_json TEXT,
                icon TEXT
            )
        """)
        
        # Permissions table
        await self._db.execute("""
            CREATE TABLE IF NOT EXISTS permissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tool_name TEXT NOT NULL,
                scope TEXT NOT NULL,
                tier TEXT NOT NULL CHECK (tier IN ('off', 'ask', 'allow')),
                granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(tool_name, scope)
            )
        """)
        
        # Workflows table
        await self._db.execute("""
            CREATE TABLE IF NOT EXISTS workflows (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                trigger_json TEXT NOT NULL,
                actions_json TEXT NOT NULL,
                enabled BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Learning progress table
        await self._db.execute("""
            CREATE TABLE IF NOT EXISTS learning_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT NOT NULL,
                topic TEXT NOT NULL,
                score REAL,
                next_review TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(subject, topic)
            )
        """)
        
        # Create indexes for performance
        await self._db.execute("CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages (conversation_id)")
        await self._db.execute("CREATE INDEX IF NOT EXISTS idx_activity_timestamp ON activity (timestamp)")
        await self._db.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks (status)")
        
        await self._db.commit()
    
    @property
    def connection(self) -> aiosqlite.Connection:
        """Get database connection."""
        if not self._db:
            raise RuntimeError("Database not initialized")
        return self._db