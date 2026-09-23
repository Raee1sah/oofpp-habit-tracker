"""
database.py

Handles all persistence operations for the habit tracker application.
Wraps the sqlite3 standard library module and isolates all SQL/database
concerns away from the business logic in tracker.py.
"""

import sqlite3
from datetime import datetime


class Database:
    """
    Manages the SQLite connection and all read/write operations for
    habits and their completion events.

    Two tables are used:
      - habits: id, task, periodicity, created_at
      - completions: id, habit_id, timestamp
    """

    def __init__(self, db_path="habits.db"):
        """
        Open (or create) the SQLite database file at db_path and ensure
        the required tables exist.

        :param db_path: path to the SQLite database file.
        """
        self.connection = sqlite3.connect(db_path)
        self.connection.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        """Create the habits and completions tables if they don't exist."""
        cursor = self.connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT NOT NULL,
                periodicity TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS completions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                habit_id INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (habit_id) REFERENCES habits (id)
            )
        """)
        self.connection.commit()

    def save_habit(self, task, periodicity, created_at=None):
        """
        Insert a new habit into the habits table.

        :param task: description of the habit (e.g. "Drink water").
        :param periodicity: "daily" or "weekly".
        :param created_at: ISO datetime string; defaults to now.
        :return: the id of the newly created habit.
        """
        created_at = created_at or datetime.now().isoformat()
        cursor = self.connection.cursor()
        cursor.execute(
            "INSERT INTO habits (task, periodicity, created_at) VALUES (?, ?, ?)",
            (task, periodicity, created_at)
        )
        self.connection.commit()
        return cursor.lastrowid

    def load_habits(self):
        """
        Retrieve all habits from the database.

        :return: list of sqlite3.Row objects, each representing a habit.
        """
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM habits")
        return cursor.fetchall()

    def load_habit_by_id(self, habit_id):
        """
        Retrieve a single habit by its id.

        :param habit_id: the id of the habit to retrieve.
        :return: sqlite3.Row or None if not found.
        """
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM habits WHERE id = ?", (habit_id,))
        return cursor.fetchone()

    def update_habit(self, habit_id, task=None, periodicity=None):
        """
        Update the task and/or periodicity of an existing habit.
        Only the fields provided (not None) are changed.

        :param habit_id: the id of the habit to update.
        :param task: new task description, or None to leave unchanged.
        :param periodicity: new periodicity ("daily"/"weekly"), or None
               to leave unchanged.
        :return: True if a row was updated, False if no habit with that
                 id exists.
        """
        existing = self.load_habit_by_id(habit_id)
        if existing is None:
            return False

        new_task = task if task is not None else existing["task"]
        new_periodicity = periodicity if periodicity is not None else existing["periodicity"]

        cursor = self.connection.cursor()
        cursor.execute(
            "UPDATE habits SET task = ?, periodicity = ? WHERE id = ?",
            (new_task, new_periodicity, habit_id)
        )
        self.connection.commit()
        return True

    def delete_habit(self, habit_id):
        """
        Delete a habit and all of its associated completion events.

        :param habit_id: the id of the habit to delete.
        """
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM completions WHERE habit_id = ?", (habit_id,))
        cursor.execute("DELETE FROM habits WHERE id = ?", (habit_id,))
        self.connection.commit()

    def save_completion(self, habit_id, timestamp=None):
        """
        Record a completion event for a given habit.

        :param habit_id: the id of the habit being completed.
        :param timestamp: ISO datetime string; defaults to now.
        """
        timestamp = timestamp or datetime.now().isoformat()
        cursor = self.connection.cursor()
        cursor.execute(
            "INSERT INTO completions (habit_id, timestamp) VALUES (?, ?)",
            (habit_id, timestamp)
        )
        self.connection.commit()

    def load_completions(self, habit_id):
        """
        Retrieve all completion timestamps for a given habit, ordered
        chronologically.

        :param habit_id: the id of the habit.
        :return: list of ISO datetime strings.
        """
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT timestamp FROM completions WHERE habit_id = ? ORDER BY timestamp",
            (habit_id,)
        )
        return [row["timestamp"] for row in cursor.fetchall()]

    def close(self):
        """Close the database connection."""
        self.connection.close()
