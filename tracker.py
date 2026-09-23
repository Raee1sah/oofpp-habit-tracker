"""
tracker.py

Defines the HabitTracker class, which acts as the central controller
of the application. It coordinates between the Habit objects, the
user, and the Database persistence layer.
"""

from habit import Habit, validate_periodicity


class HabitTracker:
    """
    Manages a collection of Habit objects and coordinates their
    creation, editing, deletion, completion, and retrieval via the
    Database.
    """

    def __init__(self, database):
        """
        :param database: a Database instance used for persistence.
        """
        self.database = database

    def add_habit(self, task, periodicity):
        """
        Create a new habit, persist it, and return the Habit object.

        :param task: description of the habit.
        :param periodicity: "daily" or "weekly".
        :return: the newly created Habit instance (with its id set).
        """
        habit = Habit(task, periodicity)
        habit.id = self.database.save_habit(habit.task, habit.periodicity, habit.created_at)
        return habit

    def update_habit(self, habit_id, task=None, periodicity=None):
        """
        Edit an existing habit's task and/or periodicity. Only the
        fields provided are changed; omitted fields keep their current
        value. Existing completion history is untouched.

        :param habit_id: the id of the habit to edit.
        :param task: new task description, or None to leave unchanged.
        :param periodicity: new periodicity ("daily"/"weekly"), or None
               to leave unchanged.
        :return: the updated Habit instance, or None if no habit with
                 that id exists.
        :raises ValueError: if periodicity is provided but invalid.
        """
        if periodicity is not None:
            validate_periodicity(periodicity)

        updated = self.database.update_habit(habit_id, task, periodicity)
        if not updated:
            return None
        return self.get_habit(habit_id)

    def delete_habit(self, habit_id):
        """
        Remove a habit and its completion history.

        :param habit_id: the id of the habit to delete.
        """
        self.database.delete_habit(habit_id)

    def complete_habit(self, habit_id, timestamp=None):
        """
        Record a completion event for the given habit id.

        :param habit_id: the id of the habit being completed.
        :param timestamp: ISO datetime string; defaults to now.
        """
        self.database.save_completion(habit_id, timestamp)

    def list_habits(self):
        """
        Retrieve all habits currently tracked, as Habit objects.

        :return: list of Habit instances.
        """
        rows = self.database.load_habits()
        return [
            Habit(row["task"], row["periodicity"], row["created_at"], row["id"])
            for row in rows
        ]

    def get_habit(self, habit_id):
        """
        Retrieve a single habit by id, as a Habit object.

        :param habit_id: the id of the habit.
        :return: Habit instance, or None if not found.
        """
        row = self.database.load_habit_by_id(habit_id)
        if row is None:
            return None
        return Habit(row["task"], row["periodicity"], row["created_at"], row["id"])
