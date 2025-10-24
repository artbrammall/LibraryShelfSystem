from collections import deque

class BookState:
    """
    Represents the state of a single book title in the library system.

    Attributes:
        total (int): Total number of copies of this title.
        borrowed_count (int): Number of copies currently borrowed.
        reservations (deque): Queue (FIFO) of student IDs waiting for this title.
        borrowers (dict): Maps student_id -> number of copies currently borrowed by that student.
    """

    def __init__(self):
        """
        Initialize a new BookState with default values.
        """
        self.total = 0           # Total copies held by the library
        self.borrowed_count = 0        # Copies currently lent out
        self.reservations = deque()     # Pending reservations in FIFO order
        self.borrowers = {}             # student_id -> count of borrowed copies