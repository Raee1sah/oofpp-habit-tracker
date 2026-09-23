"""
analytics.py

Functional analytics module for the habit tracker application.

Every function here is pure: it accepts data (habits and/or completion
timestamps) as input and returns a result, without mutating any
application state or touching the database directly. This keeps the
analytics logic reusable, predictable, and easy to unit test in
isolation from the OOP components and the persistence layer.

The four required analytical functions are:
  - get_all_habits
  - get_same_periodicity
  - longest_streak
  - overall_longest_streak
"""

from datetime import datetime, timedelta


def get_all_habits(habits):
    """
    Return a list of all currently tracked habits.

    :param habits: list of Habit objects.
    :return: list of Habit objects (identical to input; provided as an
             explicit analytics entry point per the assignment spec).
    """
    return list(habits)


def get_same_periodicity(habits, periodicity):
    """
    Return all habits that share the given periodicity.

    :param habits: list of Habit objects.
    :param periodicity: "daily" or "weekly".
    :return: list of Habit objects matching the given periodicity.
    """
    return [h for h in habits if h.periodicity == periodicity]


def _expected_interval(periodicity):
    """Return the timedelta representing one period for the given periodicity."""
    if periodicity == "daily":
        return timedelta(days=1)
    elif periodicity == "weekly":
        return timedelta(weeks=1)
    raise ValueError("periodicity must be 'daily' or 'weekly'")


def longest_streak(completions, periodicity):
    """
    Calculate the longest run of consecutive periods (without a break)
    for a single habit, given its completion timestamps.

    A streak continues as long as consecutive completions fall within
    one expected period (1 day for daily habits, 7 days for weekly
    habits) of each other. Multiple completions within the same period
    do not extend the streak further than one step.

    :param completions: list of ISO datetime strings (unordered allowed).
    :param periodicity: "daily" or "weekly".
    :return: integer length of the longest streak (0 if no completions).
    """
    if not completions:
        return 0

    dates = sorted(datetime.fromisoformat(ts) for ts in completions)
    interval = _expected_interval(periodicity)

    # Allow a small grace window so timestamps taken slightly late/early
    # on the same day/week still count as consecutive.
    tolerance = timedelta(hours=12) if periodicity == "daily" else timedelta(days=1)

    longest = 1
    current = 1

    for previous, current_date in zip(dates, dates[1:]):
        gap = current_date - previous
        if gap <= interval + tolerance:
            current += 1
        else:
            current = 1
        longest = max(longest, current)

    return longest


def overall_longest_streak(habits, completions_by_habit_id):
    """
    Calculate the longest streak across all recorded habits.

    :param habits: list of Habit objects.
    :param completions_by_habit_id: dict mapping habit.id -> list of
           ISO datetime strings for that habit's completions.
    :return: integer length of the single longest streak found across
             all habits (0 if there are no habits or no completions).
    """
    if not habits:
        return 0

    streaks = [
        longest_streak(completions_by_habit_id.get(h.id, []), h.periodicity)
        for h in habits
    ]
    return max(streaks, default=0)
