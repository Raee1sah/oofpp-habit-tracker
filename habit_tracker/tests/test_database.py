"""
test_database.py

Unit tests for the Database class (database.py). Uses an in-memory
SQLite database so tests are fast and leave no files behind.
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database import Database


class TestDatabase(unittest.TestCase):

    def setUp(self):
        self.db = Database(":memory:")

    def tearDown(self):
        self.db.close()

    def test_save_and_load_habit(self):
        habit_id = self.db.save_habit("Drink water", "daily")
        habits = self.db.load_habits()

        self.assertEqual(len(habits), 1)
        self.assertEqual(habits[0]["task"], "Drink water")
        self.assertEqual(habits[0]["periodicity"], "daily")
        self.assertEqual(habits[0]["id"], habit_id)

    def test_load_habit_by_id(self):
        habit_id = self.db.save_habit("Exercise", "daily")
        row = self.db.load_habit_by_id(habit_id)

        self.assertIsNotNone(row)
        self.assertEqual(row["task"], "Exercise")

    def test_load_habit_by_id_returns_none_if_missing(self):
        row = self.db.load_habit_by_id(999)
        self.assertIsNone(row)

    def test_delete_habit_removes_habit_and_completions(self):
        habit_id = self.db.save_habit("Read", "daily")
        self.db.save_completion(habit_id)

        self.db.delete_habit(habit_id)

        self.assertIsNone(self.db.load_habit_by_id(habit_id))
        self.assertEqual(self.db.load_completions(habit_id), [])

    def test_update_habit_changes_task_only(self):
        habit_id = self.db.save_habit("Read", "daily")

        result = self.db.update_habit(habit_id, task="Read a book")

        self.assertTrue(result)
        row = self.db.load_habit_by_id(habit_id)
        self.assertEqual(row["task"], "Read a book")
        self.assertEqual(row["periodicity"], "daily")  # unchanged

    def test_update_habit_changes_periodicity_only(self):
        habit_id = self.db.save_habit("Clean", "daily")

        self.db.update_habit(habit_id, periodicity="weekly")

        row = self.db.load_habit_by_id(habit_id)
        self.assertEqual(row["task"], "Clean")  # unchanged
        self.assertEqual(row["periodicity"], "weekly")

    def test_update_habit_changes_both_fields(self):
        habit_id = self.db.save_habit("Old task", "daily")

        self.db.update_habit(habit_id, task="New task", periodicity="weekly")

        row = self.db.load_habit_by_id(habit_id)
        self.assertEqual(row["task"], "New task")
        self.assertEqual(row["periodicity"], "weekly")

    def test_update_habit_returns_false_for_missing_id(self):
        result = self.db.update_habit(999, task="Doesn't matter")
        self.assertFalse(result)

    def test_update_habit_preserves_completions(self):
        habit_id = self.db.save_habit("Read", "daily")
        self.db.save_completion(habit_id, "2026-01-01T09:00:00")

        self.db.update_habit(habit_id, task="Read more")

        self.assertEqual(self.db.load_completions(habit_id), ["2026-01-01T09:00:00"])

    def test_save_and_load_completions_in_order(self):
        habit_id = self.db.save_habit("Read", "daily")
        self.db.save_completion(habit_id, "2026-01-01T09:00:00")
        self.db.save_completion(habit_id, "2026-01-02T09:00:00")

        completions = self.db.load_completions(habit_id)

        self.assertEqual(completions, ["2026-01-01T09:00:00", "2026-01-02T09:00:00"])


if __name__ == "__main__":
    unittest.main()
