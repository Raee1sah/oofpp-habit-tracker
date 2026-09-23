"""
test_analytics.py

Unit tests for the functional analytics module (analytics.py). These
tests use hand-built Habit objects and known completion timestamps
(dummy data) so that expected streak lengths can be verified exactly,
independent of the database or current date.
"""

import sys
import os
import unittest
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from habit import Habit
from analytics import (
    get_all_habits,
    get_same_periodicity,
    longest_streak,
    overall_longest_streak,
)


def iso_days_ago(days):
    return (datetime.now() - timedelta(days=days)).isoformat()


def iso_weeks_ago(weeks):
    return (datetime.now() - timedelta(weeks=weeks)).isoformat()


class TestAnalytics(unittest.TestCase):

    def test_get_all_habits_returns_all(self):
        habits = [Habit("A", "daily", habit_id=1), Habit("B", "weekly", habit_id=2)]
        result = get_all_habits(habits)
        self.assertEqual(result, habits)

    def test_get_same_periodicity_filters_correctly(self):
        daily = Habit("A", "daily", habit_id=1)
        weekly = Habit("B", "weekly", habit_id=2)
        habits = [daily, weekly]

        result = get_same_periodicity(habits, "daily")

        self.assertEqual(result, [daily])

    def test_longest_streak_with_no_completions_is_zero(self):
        self.assertEqual(longest_streak([], "daily"), 0)

    def test_longest_streak_daily_perfect_run(self):
        # 5 consecutive daily completions -> streak of 5
        completions = [iso_days_ago(i) for i in range(5)]
        self.assertEqual(longest_streak(completions, "daily"), 5)

    def test_longest_streak_daily_with_a_break(self):
        # Days ago: 10, 9, 8 (streak of 3), gap, then 4, 3, 2, 1, 0 (streak of 5)
        completions = [iso_days_ago(d) for d in [10, 9, 8, 4, 3, 2, 1, 0]]
        self.assertEqual(longest_streak(completions, "daily"), 5)

    def test_longest_streak_weekly_perfect_run(self):
        completions = [iso_weeks_ago(w) for w in range(4)]
        self.assertEqual(longest_streak(completions, "weekly"), 4)

    def test_overall_longest_streak_across_multiple_habits(self):
        habit_a = Habit("A", "daily", habit_id=1)
        habit_b = Habit("B", "weekly", habit_id=2)
        habits = [habit_a, habit_b]

        completions_by_id = {
            1: [iso_days_ago(i) for i in range(3)],   # streak of 3
            2: [iso_weeks_ago(w) for w in range(6)],  # streak of 6
        }

        self.assertEqual(overall_longest_streak(habits, completions_by_id), 6)

    def test_overall_longest_streak_with_no_habits_is_zero(self):
        self.assertEqual(overall_longest_streak([], {}), 0)


if __name__ == "__main__":
    unittest.main()
