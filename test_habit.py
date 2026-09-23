"""
test_habit.py

Unit tests for the Habit class (habit.py), using the built-in
unittest framework.
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from habit import Habit
from database import Database


class TestHabit(unittest.TestCase):

    def setUp(self):
        """Provide a fresh in-memory SQLite database for each test."""
        self.db = Database(":memory:")

    def tearDown(self):
        self.db.close()

    def test_habit_creation_sets_attributes(self):
        habit = Habit("Drink water", "daily")
        self.assertEqual(habit.task, "Drink water")
        self.assertEqual(habit.periodicity, "daily")
        self.assertIsNone(habit.id)
        self.assertIsNotNone(habit.created_at)

    def test_habit_rejects_invalid_periodicity(self):
        with self.assertRaises(ValueError):
            Habit("Invalid habit", "monthly")

    def test_mark_complete_without_id_raises(self):
        habit = Habit("Read", "daily")
        with self.assertRaises(ValueError):
            habit.mark_complete(self.db)

    def test_mark_complete_records_completion(self):
        habit = Habit("Read", "daily")
        habit.id = self.db.save_habit(habit.task, habit.periodicity, habit.created_at)

        habit.mark_complete(self.db)

        completions = self.db.load_completions(habit.id)
        self.assertEqual(len(completions), 1)


if __name__ == "__main__":
    unittest.main()
