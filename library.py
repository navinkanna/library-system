from datetime import date, timedelta
from typing import Dict, List

from models import Book, Member, BorrowRecord
from errors import (
    BookNotFoundError,
    AlreadyCheckedOutError,
    NotCheckedOutError,
    MemberNotFoundError,
    BorrowingLimitExceededError,
    UnpaidFineError,
    DuplicateBookError,
    DuplicateMemberError,
)


class Library:
    """Domain class for library checkout system."""

    BORROW_LIMIT = 3
    CHECKOUT_DURATION_DAYS = 14
    FINE_PER_DAY = 0.5
    MAX_UNPAID_FINE = 10.0

    def __init__(self):
        self.books: Dict[str, Book] = {}
        self.members: Dict[int, Member] = {}
        self.borrow_records: List[BorrowRecord] = []

    def addBook(self, book: Book) -> None:
        if book.isbn in self.books:
            raise DuplicateBookError(f"Book with ISBN {book.isbn} already exists")
        self.books[book.isbn] = book

    def registerMember(self, member: Member) -> None:
        if member.memberId in self.members:
            raise DuplicateMemberError(f"Member with ID {member.memberId} already exists")
        self.members[member.memberId] = member

    def checkoutBook(self, memberId: int, isbn: str) -> BorrowRecord:
        if memberId not in self.members:
            raise MemberNotFoundError(f"Member {memberId} not found")
        if isbn not in self.books:
            raise BookNotFoundError(f"Book with ISBN {isbn} not found")

        member = self.members[memberId]
        book = self.books[isbn]

        if not book.isAvailable:
            raise AlreadyCheckedOutError(f"Book {isbn} is already checked out")

        # Sync the member's fine before validation
        current_fine = self.calculateFine(memberId)
        if current_fine > self.MAX_UNPAID_FINE:
            raise UnpaidFineError(
                f"Member {memberId} has unpaid fine ${current_fine:.2f}, cannot checkout." 
            )

        if len(member.borrowedBooks) >= self.BORROW_LIMIT:
            raise BorrowingLimitExceededError(
                f"Member {memberId} has reached borrowing limit of {self.BORROW_LIMIT}" 
            )

        # Perform checkout
        book.isAvailable = False
        member.borrowedBooks.append(isbn)

        checkout_date = date.today()
        due_date = checkout_date + timedelta(days=self.CHECKOUT_DURATION_DAYS)

        record = BorrowRecord(
            memberId=memberId,
            isbn=isbn,
            checkout_date=checkout_date,
            due_date=due_date,
            return_date=None,
            fine_charged=0.0,
            fine_paid=0.0,
        )

        self.borrow_records.append(record)
        return record

    def returnBook(self, memberId: int, isbn: str) -> BorrowRecord:
        if memberId not in self.members:
            raise MemberNotFoundError(f"Member {memberId} not found")
        if isbn not in self.books:
            raise BookNotFoundError(f"Book with ISBN {isbn} not found")

        member = self.members[memberId]
        book = self.books[isbn]

        if isbn not in member.borrowedBooks:
            raise NotCheckedOutError(f"Book {isbn} is not checked out by member {memberId}")

        # Find the active borrow record
        active_record = None
        for record in self.borrow_records:
            if record.memberId == memberId and record.isbn == isbn and record.return_date is None:
                active_record = record
                break

        if active_record is None:
            raise NotCheckedOutError(f"No active borrow record for member {memberId} and book {isbn}")

        # Perform return
        return_date = date.today()
        active_record.return_date = return_date

        # Update book and member state
        book.isAvailable = True
        member.borrowedBooks.remove(isbn)

        # Update member's fine balance (this will also calculate final fine for the returned record)
        self.calculateFine(memberId)

        return active_record

    def _calculate_record_fine(self, record: BorrowRecord) -> float:
        """Calculate and update fine_charged for a borrow record."""
        if record.return_date is not None:
            # Returned book: calculate final fine
            overdue_days = (record.return_date - record.due_date).days
            if overdue_days > 0:
                record.fine_charged = round(overdue_days * self.FINE_PER_DAY, 2)
            else:
                record.fine_charged = 0.0
        else:
            # Active book: update ongoing fine
            overdue_days = (date.today() - record.due_date).days
            if overdue_days > 0:
                current_fine = round(overdue_days * self.FINE_PER_DAY, 2)
                record.fine_charged = max(record.fine_charged, current_fine)
            # If not overdue, fine_charged remains 0

        return record.fine_charged

    def calculateFine(self, memberId: int) -> float:
        if memberId not in self.members:
            raise MemberNotFoundError(f"Member {memberId} not found")

        member = self.members[memberId]
        total_outstanding = 0.0

        for record in self.borrow_records:
            if record.memberId != memberId:
                continue

            self._calculate_record_fine(record)
            outstanding = max(0.0, record.fine_charged - record.fine_paid)
            total_outstanding += outstanding

        member.fineBalance = round(total_outstanding, 2)
        return member.fineBalance

    def getAvailableBooks(self) -> List[Book]:
        return [book for book in self.books.values() if book.isAvailable]

    def getMemberBorrowingHistory(self, memberId: int) -> List[BorrowRecord]:
        if memberId not in self.members:
            raise MemberNotFoundError(f"Member {memberId} not found")
        return [record for record in self.borrow_records if record.memberId == memberId]

    def listMembers(self) -> List[Member]:
        return list(self.members.values())

    def payFine(self, memberId: int, amount: float) -> float:
        if memberId not in self.members:
            raise MemberNotFoundError(f"Member {memberId} not found")

        if amount <= 0:
            raise ValueError("Payment amount must be positive")

        # Ensure fines are up to date
        current_total = self.calculateFine(memberId)

        if current_total <= 0:
            return amount  # No fines to pay, return full amount

        member = self.members[memberId]

        # Get records with outstanding fines, sorted by checkout_date (oldest first)
        records_with_fines = [
            record for record in self.borrow_records
            if record.memberId == memberId and (record.fine_charged - record.fine_paid) > 0
        ]
        records_with_fines.sort(key=lambda r: r.checkout_date)

        remaining_amount = amount
        for record in records_with_fines:
            if remaining_amount <= 0:
                break

            outstanding = record.fine_charged - record.fine_paid
            pay_amount = min(remaining_amount, outstanding)
            record.fine_paid += pay_amount
            remaining_amount -= pay_amount

        # Update member's fine balance
        self.calculateFine(memberId)

        return round(remaining_amount, 2)

