"""
habit.py

Defines the Habit class, which represents a single habit and its
properties. This class is intentionally lightweight: it knows about
its own task, periodicity, and creation date, but does not know how
it is persisted or how it is analysed. Those responsibilities belong
to Database and the analytics module respectively.
"""

from datetime import datetime

VALID_PERIODICITIES = ("daily", "weekly")


def validate_periodicity(periodicity):
    """
    Raise ValueError if periodicity isn't one of the supported values.

    :param periodicity: the value to check.
    """
    if periodicity not in VALID_PERIODICITIES:
        raise ValueError("periodicity must be 'daily' or 'weekly'")


class Habit:
    """
    Represents a single habit tracked by the user.

    Attributes:
        id (int or None): database id, set once the habit is persisted.
        task (str): description of the habit, e.g. "Read for 20 minutes".
        periodicity (str): "daily" or "weekly".
        created_at (str): ISO datetime string of when the habit was created.
    """

    def __init__(self, task, periodicity, created_at=None, habit_id=None):
        """
        Create a new Habit instance.

        :param task: description of the habit.
        :param periodicity: "daily" or "weekly".
        :param created_at: ISO datetime string; defaults to now.
        :param habit_id: database id, if already persisted.
        """
        validate_periodicity(periodicity)

        self.id = habit_id
        self.task = task
        self.periodicity = periodicity
        self.created_at = created_at or datetime.now().isoformat()

    def mark_complete(self, database, timestamp=None):
        """
        Record a completion event for this habit via the database layer.

        :param database: a Database instance used to persist the event.
        :param timestamp: ISO datetime string; defaults to now.
        """
        if self.id is None:
            raise ValueError("Cannot mark complete a habit with no id "
                              "(has it been saved yet?)")
        database.save_completion(self.id, timestamp)

    def __repr__(self):
        return f"Habit(id={self.id}, task={self.task!r}, periodicity={self.periodicity!r})"
