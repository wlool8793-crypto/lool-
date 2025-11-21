"""
Global ID and UUID Generator for Universal Legal Documents
Generates unique identifiers across the entire system
"""

import uuid
import sqlite3
from typing import Optional, Tuple
from pathlib import Path
import threading


class IDGenerator:
    """
    Generates unique identifiers for legal documents.

    Supports:
    - Global sequential IDs (ULEGAL-0000000001)
    - UUID v4 for distributed systems
    - Yearly sequences per country/category
    """

    _instance = None
    _lock = threading.Lock()

    def __init__(self, db_path: str = None):
        """
        Initialize ID generator.

        Args:
            db_path: Path to database (for sequence tracking)
        """
        if db_path is None:
            db_path = 'data/universal_legal.db'

        self.db_path = db_path
        self._ensure_database()

    @classmethod
    def get_instance(cls, db_path: str = None):
        """Get singleton instance (thread-safe)"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls(db_path)
        return cls._instance

    def _ensure_database(self):
        """Ensure database and sequence_tracker table exist"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create sequence_tracker if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sequence_tracker (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sequence_type TEXT NOT NULL,
                country_code TEXT,
                doc_category TEXT,
                year INTEGER,
                last_value INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(sequence_type, country_code, doc_category, year)
            )
        """)

        # Initialize global sequence if not exists
        cursor.execute("""
            INSERT OR IGNORE INTO sequence_tracker (sequence_type, last_value)
            VALUES ('GLOBAL', 0)
        """)

        conn.commit()
        conn.close()

    def generate_global_id(self) -> Tuple[int, str]:
        """
        Generate next global sequential ID.

        Returns:
            Tuple of (numeric_id, formatted_id)
            e.g., (1, 'ULEGAL-0000000001')
        """
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get and increment global sequence
            cursor.execute("""
                UPDATE sequence_tracker
                SET last_value = last_value + 1,
                    updated_at = CURRENT_TIMESTAMP
                WHERE sequence_type = 'GLOBAL'
            """)

            cursor.execute("""
                SELECT last_value FROM sequence_tracker
                WHERE sequence_type = 'GLOBAL'
            """)

            result = cursor.fetchone()
            conn.commit()
            conn.close()

            if result:
                seq_id = result[0]
                formatted_id = f"ULEGAL-{seq_id:010d}"
                return seq_id, formatted_id
            else:
                raise RuntimeError("Failed to get global sequence")

    def generate_uuid(self) -> str:
        """
        Generate UUID v4.

        Returns:
            UUID string (lowercase, with hyphens)
            e.g., '550e8400-e29b-41d4-a716-446655440000'
        """
        return str(uuid.uuid4())

    def get_next_yearly_sequence(
        self,
        country_code: str,
        doc_category: str,
        year: int
    ) -> int:
        """
        Get next sequence number for a specific country/category/year.

        Args:
            country_code: Two-letter country code (e.g., 'BD', 'IN')
            doc_category: Document category (e.g., 'ACT', 'CASE')
            year: Year (e.g., 1860, 2023)

        Returns:
            Next sequence number (1-based)
        """
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Try to insert or update
            cursor.execute("""
                INSERT INTO sequence_tracker (
                    sequence_type, country_code, doc_category, year, last_value
                )
                VALUES ('YEARLY', ?, ?, ?, 1)
                ON CONFLICT(sequence_type, country_code, doc_category, year)
                DO UPDATE SET
                    last_value = last_value + 1,
                    updated_at = CURRENT_TIMESTAMP
            """, (country_code, doc_category, year))

            # Get the value
            cursor.execute("""
                SELECT last_value FROM sequence_tracker
                WHERE sequence_type = 'YEARLY'
                  AND country_code = ?
                  AND doc_category = ?
                  AND year = ?
            """, (country_code, doc_category, year))

            result = cursor.fetchone()
            conn.commit()
            conn.close()

            if result:
                return result[0]
            else:
                return 1

    def get_current_yearly_sequence(
        self,
        country_code: str,
        doc_category: str,
        year: int
    ) -> int:
        """
        Get current sequence number without incrementing.

        Args:
            country_code: Two-letter country code
            doc_category: Document category
            year: Year

        Returns:
            Current sequence number (0 if not initialized)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT last_value FROM sequence_tracker
            WHERE sequence_type = 'YEARLY'
              AND country_code = ?
              AND doc_category = ?
              AND year = ?
        """, (country_code, doc_category, year))

        result = cursor.fetchone()
        conn.close()

        return result[0] if result else 0

    def reset_sequence(
        self,
        sequence_type: str,
        country_code: Optional[str] = None,
        doc_category: Optional[str] = None,
        year: Optional[int] = None
    ):
        """
        Reset a sequence to 0 (USE WITH CAUTION!).

        Args:
            sequence_type: 'GLOBAL' or 'YEARLY'
            country_code: Required for YEARLY
            doc_category: Required for YEARLY
            year: Required for YEARLY
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if sequence_type == 'GLOBAL':
            cursor.execute("""
                UPDATE sequence_tracker
                SET last_value = 0, updated_at = CURRENT_TIMESTAMP
                WHERE sequence_type = 'GLOBAL'
            """)
        elif sequence_type == 'YEARLY':
            cursor.execute("""
                UPDATE sequence_tracker
                SET last_value = 0, updated_at = CURRENT_TIMESTAMP
                WHERE sequence_type = 'YEARLY'
                  AND country_code = ?
                  AND doc_category = ?
                  AND year = ?
            """, (country_code, doc_category, year))

        conn.commit()
        conn.close()

    def get_stats(self) -> dict:
        """
        Get statistics about sequences.

        Returns:
            Dictionary with sequence statistics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Global sequence
        cursor.execute("""
            SELECT last_value FROM sequence_tracker
            WHERE sequence_type = 'GLOBAL'
        """)
        global_seq = cursor.fetchone()

        # Yearly sequences
        cursor.execute("""
            SELECT
                country_code,
                doc_category,
                year,
                last_value
            FROM sequence_tracker
            WHERE sequence_type = 'YEARLY'
            ORDER BY country_code, doc_category, year
        """)
        yearly_seqs = cursor.fetchall()

        conn.close()

        return {
            'global_sequence': global_seq[0] if global_seq else 0,
            'yearly_sequences': [
                {
                    'country': row[0],
                    'category': row[1],
                    'year': row[2],
                    'count': row[3]
                }
                for row in yearly_seqs
            ],
            'total_yearly_sequences': len(yearly_seqs)
        }


if __name__ == "__main__":
    # Test ID generator
    print("Testing ID Generator...")

    gen = IDGenerator('data/test_ids.db')

    # Generate global IDs
    print("\nGlobal IDs:")
    for i in range(5):
        numeric_id, formatted_id = gen.generate_global_id()
        print(f"  {numeric_id}: {formatted_id}")

    # Generate UUIDs
    print("\nUUIDs:")
    for i in range(3):
        print(f"  {gen.generate_uuid()}")

    # Generate yearly sequences
    print("\nYearly Sequences:")
    print(f"  BD/ACT/1860: {gen.get_next_yearly_sequence('BD', 'ACT', 1860)}")
    print(f"  BD/ACT/1860: {gen.get_next_yearly_sequence('BD', 'ACT', 1860)}")
    print(f"  BD/ACT/1860: {gen.get_next_yearly_sequence('BD', 'ACT', 1860)}")
    print(f"  IN/CASE/2023: {gen.get_next_yearly_sequence('IN', 'CASE', 2023)}")
    print(f"  IN/CASE/2023: {gen.get_next_yearly_sequence('IN', 'CASE', 2023)}")

    # Get stats
    print("\nStatistics:")
    stats = gen.get_stats()
    print(f"  Global sequence: {stats['global_sequence']}")
    print(f"  Yearly sequences: {stats['total_yearly_sequences']}")
    for seq in stats['yearly_sequences']:
        print(f"    {seq['country']}/{seq['category']}/{seq['year']}: {seq['count']}")
