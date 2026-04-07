from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional


@dataclass
class Book:
    isbn: str
    title: str
    author: str
    isAvailable: bool = True


@dataclass
class Member:
    memberId: int
    name: str
    borrowedBooks: List[str] = field(default_factory=list)
    fineBalance: float = 0.0


@dataclass
class BorrowRecord:
    memberId: int
    isbn: str
    checkout_date: date
    due_date: date
    return_date: Optional[date] = None
    fine_charged: float = 0.0
    fine_paid: float = 0.0

    @property
    def is_returned(self) -> bool:
        return self.return_date is not None
