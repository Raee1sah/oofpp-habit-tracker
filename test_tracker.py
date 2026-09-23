"""
test_tracker.py

Unit tests for the HabitTracker class (tracker.py).
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database import Database
from tracker import HabitTracker


class TestHabitTracker(unittest.TestCase):

    def setUp(self):
        self.database = Database(":memory:")
        self.tracker = HabitTracker(self.database)

    def tearDown(self):
        self.database.close()

    def test_add_habit_returns_habit_with_id(self):
        habit = self.tracker.add_habit("Drink water", "daily")
        self.assertIsNotNone(habit.id)
        self.assertEqual(habit.task, "Drink water")

    def test_list_habits_returns_all_added_habits(self):
        self.tracker.add_habit("Drink water", "daily")
        self.tracker.add_habit("Weekly grocery shop", "weekly")

        habits = self.tracker.list_habits()

        self.assertEqual(len(habits), 2)
        tasks = {h.task for h in habits}
        self.assertEqual(tasks, {"Drink water", "Weekly grocery shop"})

    def test_get_habit_returns_none_for_missing_id(self):
        self.assertIsNone(self.tracker.get_habit(999))

    def test_delete_habit_removes_it_from_list(self):
        habit = self.tracker.add_habit("Read", "daily")
        self.tracker.delete_habit(habit.id)

        self.assertEqual(self.tracker.list_habits(), [])

    def test_update_habit_changes_task(self):
        habit = self.tracker.add_habit("Read", "daily")

        updated = self.tracker.update_habit(habit.id, task="Read fiction")

        self.assertEqual(updated.task, "Read fiction")
        self.assertEqual(updated.periodicity, "daily")  # unchanged

    def test_update_habit_changes_periodicity(self):
        habit = self.tracker.add_habit("Clean", "daily")

        updated = self.tracker.update_habit(habit.id, periodicity="weekly")

        self.assertEqual(updated.periodicity, "weekly")

    def test_update_habit_rejects_invalid_periodicity(self):
        habit = self.tracker.add_habit("Read", "daily")

        with self.assertRaises(ValueError):
            self.tracker.update_habit(habit.id, periodicity="monthly")

    def test_update_habit_returns_none_for_missing_id(self):
        result = self.tracker.update_habit(999, task="Doesn't exist")
        self.assertIsNone(result)

    def test_update_habit_reflected_in_list_habits(self):
        habit = self.tracker.add_habit("Old name", "daily")
        self.tracker.update_habit(habit.id, task="New name")

        habits = self.tracker.list_habits()

        self.assertEqual(habits[0].task, "New name")

    def test_complete_habit_records_completion(self):
        habit = self.tracker.add_habit("Read", "daily")
        self.tracker.complete_habit(habit.id)

        completions = self.tracker.database.load_completions(habit.id)
        self.assertEqual(len(completions), 1)


if __name__ == "__main__":
    unittest.main()
