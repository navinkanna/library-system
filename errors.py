class LibraryError(Exception):
    """Base class for library checkout errors."""


class BookNotFoundError(LibraryError):
    """Raised when a book cannot be found in the catalog."""
    pass


class MemberNotFoundError(LibraryError):
    """Raised when a member cannot be found in the system."""
    pass


class AlreadyCheckedOutError(LibraryError):
    """Raised when attempting to check out an already checked out book."""
    pass


class NotCheckedOutError(LibraryError):
    """Raised when attempting to return a book that is not checked out."""
    pass


class BorrowingLimitExceededError(LibraryError):
    """Raised when member has reached the limit of borrowed books."""
    pass


class UnpaidFineError(LibraryError):
    """Raised when member has unpaid fines above allowed threshold."""
    pass


class DuplicateBookError(LibraryError):
    """Raised when attempting to add a book with duplicate ISBN."""
    pass


class DuplicateMemberError(LibraryError):
    """Raised when attempting to register a member with duplicate memberId."""
    pass
