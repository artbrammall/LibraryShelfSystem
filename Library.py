from BookState import BookState
from Shelf import Shelf


class Library:
    """
    Core library management system for tracking books, borrowers, and shelf display order..
    """

    def __init__(self, shelf_capacity: int):
        """
        Initialize the library system.

        Args:
            shelf_capacity (int): Maximum number of books the shelf can display at once.
        """
        self._books = {}                # Maps book_id -> BookState
        self._shelf = Shelf(shelf_capacity)

    def _touch_book(self, book_id: str) -> BookState:
        """
        Retrieve or create the BookState object for the given title.

        Args:
            book_id (str): Unique identifier for the book.

        Returns:
            BookState: The corresponding BookState object, newly created if absent.
        """
        book_state = self._books.get(book_id)
        if book_state is None:
            book_state = BookState()
            self._books[book_id] = book_state
        return book_state

    def _available_copies(self, book_id: str) -> int:
        """
        Compute the number of currently available (non-borrowed) copies of a book.

        Args:
            book_id (str): Unique identifier for the book.

        Returns:
            int: The number of available copies. Returns 0 if the book is unknown.
        """
        book_state = self._books.get(book_id)
        if not book_state:
            return 0
        return book_state.total - book_state.borrowed_count

    def _shelf_contains(self, book_id: str) -> bool:
        """
        Check whether a given book is currently displayed on the shelf.

        Args:
            book_id (str): Unique identifier for the book.

        Returns:
            bool: True if the book is on the shelf, otherwise False.
        """
        return self._shelf.contains(book_id)

    def _shelf_move_to_front(self, book_id: str) -> None:
        """
        Move an existing book on the shelf to the front position,
        marking it as the most recently interacted-with title.

        Args:
            book_id (str): Unique identifier for the book.
        """
        self._shelf.move_to_front(book_id)

    def _shelf_add_to_front(self, book_id: str) -> str | None:
        """
        Add a book to the front of the shelf, evicting the least recent one if capacity is full.

        Args:
            book_id (str): Unique identifier for the book.

        Returns:
            str | None: The ID of any evicted book, or None if none was removed.
        """
        return self._shelf.add_to_front(book_id)

    def _shelf_front(self) -> str | None:
        """
        Retrieve the book currently at the front of the shelf.

        Returns:
            str | None: The book_id at the highest-priority position, or None if the shelf is empty.
        """
        return self._shelf.front()

    def add_books(self, add_list: list[tuple[str, int]]) -> None:
        """
        Increase stock for the given titles.
        Input: A list of (book_id, q), where q represents the number of copies to be added (q ≥ 0).
        Output: None.
        """
        for book_id, q in add_list:
            if q < 0:
                continue

            book_state = self._touch_book(book_id)
            book_state.total += q

            while book_state.reservations and self._available_copies(book_id) >= 2:
                student_id = book_state.reservations.popleft()
                book_state.borrowed_count += 1
                book_state.borrowers[student_id] = book_state.borrowers.get(student_id, 0) + 1
                if self._shelf_contains(book_id):
                    self._shelf_move_to_front(book_id)
                else:
                    self._shelf_add_to_front(book_id)

    def query_book_inventory(self) -> list[tuple[str, int]]:
        """
        Report current holdings per title.
        Input: None.
        Output: A list of (book_id, total) for all known titles.
        """
        book_inventory = [
            (book_id, self._books[book_id].total)
            for book_id in self._books
        ]
        book_inventory.sort(key=lambda x: x[0])
        return book_inventory

    def is_available(self, book_id: str) -> bool:
        """
        Determine whether one copy of a title can be lent now without violating policy.
        Input: book_id.
        Output: True if lending one copy at this moment is allowed, otherwise False.
        """
        book_state = self._books.get(book_id)
        if not book_state:
            return False
        if book_state.reservations:
            return False
        return self._available_copies(book_id) >= 2

    def borrow_book(self, book_id: str, student_id: str) -> bool:
        """
        Request to borrow one copy of a title.
        Input: book_id, student_id.
        Output: True if the request is fulfilled immediately,
        otherwise False and put the reservation on hold.
        """
        book_state = self._touch_book(book_id)
        if self.is_available(book_id):
            book_state.borrowed_count += 1
            book_state.borrowers[student_id] = book_state.borrowers.get(student_id, 0) + 1
            self._shelf_add_to_front(book_id)
            return True

        book_state.reservations.append(student_id)
        return False

    def return_book(self, book_id: str, student_id: str) -> bool:
        """
        Request to return one copy of a title.
        Input: book_id, student_id.
        Output: True if the request is fulfilled, False otherwise.
        """
        book_state = self._books.get(book_id)
        if not book_state:
            return False

        held = book_state.borrowers.get(student_id, 0)
        if held <= 0:
            return False

        if held == 1:
            del book_state.borrowers[student_id]
        else:
            book_state.borrowers[student_id] = held - 1

        book_state.borrowed_count -= 1

        while book_state.reservations and self._available_copies(book_id) >= 2:
            next_student = book_state.reservations.popleft()
            book_state.borrowed_count += 1
            book_state.borrowers[next_student] = book_state.borrowers.get(next_student, 0) + 1
            self._shelf_add_to_front(book_id)

        return True

    def check_book_on_shelf(self, book_id: str) -> bool:
        """
        Determine whether a title is currently displayed on the shelf.
        Input: book_id.
        Output: True if the title is on the shelf; otherwise False.
        """
        return self._shelf_contains(book_id)

    def check_highest_priority_book_on_shelf(self):
        """
        Identify the title currently displayed in the front shelf position.
        Input: None.
        Output: The book_id at the highest-priority shelf position,
        or None if the shelf is empty.
        """
        return self._shelf_front()