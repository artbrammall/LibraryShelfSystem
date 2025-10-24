class Shelf:
    """
    Represents the physical display shelf in the library.

    The shelf maintains a position-sensitive ordering of distinct book titles.
    Titles at the front are considered higher priority (more prominently displayed).
    When a book is borrowed, it is treated as renewed interest and moved to the front.

    Attributes:
        capacity (int): Maximum number of distinct titles the shelf can hold.
        _map (dict): Maps book_id -> node for O(1) lookup.
        _head (_Node): Sentinel node representing the front of the shelf.
        _tail (_Node): Sentinel node representing the back of the shelf.
    """

    class _Node:
        """Internal node used for doubly linked list order tracking."""
        __slots__ = ("book_id", "prev", "next")

        def __init__(self, book_id=None):
            self.book_id = book_id
            self.prev = None
            self.next = None

    def __init__(self, capacity: int):
        """
        Initialize a Shelf with a maximum capacity.

        Args:
            capacity (int): Maximum number of books the shelf can hold.
        """
        self.capacity = int(capacity)     # Maximum capacity of the shelf
        self._map = {}                    # book_id -> _Node
        self._head = self._Node()         # Sentinel node for front
        self._tail = self._Node()         # Sentinel node for back
        self._head.next = self._tail
        self._tail.prev = self._head

    def _add_front(self, node):
        """Insert node directly after head (front position)."""
        node.prev = self._head
        node.next = self._head.next
        self._head.next.prev = node
        self._head.next = node

    def _remove(self, node):
        """Detach a node from the linked list."""
        node.prev.next = node.next
        node.next.prev = node.prev

    def _pop_back(self):
        """Remove and return the node at the back (lowest priority)."""
        if self._tail.prev is self._head:
            return None
        node = self._tail.prev
        self._remove(node)
        return node

    def contains(self, book_id):
        """Return True if the book is currently on the shelf."""
        return book_id in self._map

    def move_to_front(self, book_id):
        """
        Move an existing title to the front of the shelf.
        Does nothing if the title is not on the shelf.
        """
        node = self._map.get(book_id)
        if not node:
            return
        self._remove(node)
        self._add_front(node)

    def add_to_front(self, book_id):
        """
        Add a title to the front of the shelf.
        If the shelf is full, evict the title at the back.
        If the title already exists, simply move it to the front.
        Returns the evicted book_id if one was removed, otherwise None.
        """
        if self.capacity == 0:
            return None

        if book_id in self._map:
            self.move_to_front(book_id)
            return None

        evicted = None
        if len(self._map) == self.capacity:
            back_node = self._pop_back()
            if back_node:
                evicted = back_node.book_id
                del self._map[evicted]

        node = self._Node(book_id)
        self._add_front(node)
        self._map[book_id] = node
        return evicted

    def remove_back(self):
        """Remove and return the title at the back of the shelf (lowest priority)."""
        back_node = self._pop_back()
        if not back_node:
            return None
        evicted = back_node.book_id
        del self._map[evicted]
        return evicted

    def front(self):
        """Return the book_id currently at the front of the shelf, or None if empty."""
        first_node = self._head.next
        if first_node is self._tail:
            return None
        return first_node.book_id

    def __len__(self):
        """Return the number of distinct titles currently on the shelf."""
        return len(self._map)