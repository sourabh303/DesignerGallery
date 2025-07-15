import sqlite3
import os
from typing import Optional, Tuple
from contextlib import closing

class DesignStatusDB:
    """Handles design status tracking using SQLite."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or os.path.join(os.path.dirname(__file__), 'design_status.db')
        self._init_db()

    def _init_db(self):
        with closing(sqlite3.connect(self.db_path)) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS image_status (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    designer_name TEXT NOT NULL,
                    image_name TEXT NOT NULL,
                    suit_status TEXT NOT NULL DEFAULT 'pending',
                    dupatta_status TEXT NOT NULL DEFAULT 'pending',
                    UNIQUE (designer_name, image_name)
                )
            ''')
            conn.commit()

    def get_status(self, designer: str, image: str) -> Tuple[str, str]:
        with closing(sqlite3.connect(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute('''
                SELECT suit_status, dupatta_status FROM image_status
                WHERE designer_name = ? AND image_name = ?
            ''', (designer, image))
            row = cur.fetchone()
            return (row['suit_status'], row['dupatta_status']) if row else ('pending', 'pending')

    def update_status(self, designer: str, image: str, suit_status: str, dupatta_status: str):
        with closing(sqlite3.connect(self.db_path)) as conn:
            conn.execute('''
                INSERT INTO image_status (designer_name, image_name, suit_status, dupatta_status)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(designer_name, image_name) DO UPDATE SET
                    suit_status = excluded.suit_status,
                    dupatta_status = excluded.dupatta_status
            ''', (designer, image, suit_status, dupatta_status))
            conn.commit()
db = DesignStatusDB()
