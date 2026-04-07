# Library System

A simple in-memory Python library checkout system with an interactive console UI, domain models, custom errors, seeded sample data, and a standalone test suite.

## Features

- Add books by ISBN, title, and author.
- Register library members.
- Check out and return books.
- Track member borrowing history.
- List available books and registered members.
- Calculate overdue fines at `$0.50` per day.
- Pay outstanding fines and return any overpayment.
- Enforce checkout rules:
  - Members can borrow up to `3` books at a time.
  - Books are due `14` days after checkout.
  - Members with more than `$10.00` in unpaid fines cannot check out new books.
  - Duplicate books and members are rejected.

## Project Structure

```text
.
|-- errors.py        # Custom exception types
|-- library.py       # Core Library domain logic
|-- main.py          # Interactive console application
|-- models.py        # Book, Member, and BorrowRecord dataclasses
|-- test_library.py  # Standalone test runner
`-- utils.py         # Formatting helpers and seed data
```

## Requirements

- Python 3.10 or newer
- No external packages are required

## Run the Console App

```powershell
python main.py
```

The app starts with seeded books, members, and borrow records so you can try checkout, return, fine calculation, history, and payment flows immediately.

## Run Tests

```powershell
$env:PYTHONUTF8='1'
python test_library.py
```

`PYTHONUTF8` is useful on Windows because the test runner prints emoji status markers. The current suite covers 25 happy-path and error-path scenarios.

## Core API Example

```python
from library import Library
from models import Book, Member

lib = Library()
lib.addBook(Book(isbn="1234567890", title="Example Book", author="Example Author"))
lib.registerMember(Member(memberId=1, name="Alice"))

record = lib.checkoutBook(1, "1234567890")
print(record.due_date)

lib.returnBook(1, "1234567890")
print(lib.calculateFine(1))
```

## Notes

- Data is stored in memory only; it resets each time the program starts.
- The console app catches validation and domain errors and prints user-friendly messages.
- Tests are plain Python functions, so no test framework installation is needed.
