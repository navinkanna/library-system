from datetime import date, timedelta

from library import Library
from models import Book, Member, BorrowRecord


def format_date(d: date) -> str:
    """Format date as YYYY-MM-DD."""
    return d.strftime('%Y-%m-%d')


def format_currency(amount: float) -> str:
    """Format amount as currency."""
    return f"${amount:.2f}"


def seed_data(lib: Library) -> None:
    # Create books with all attributes
    lib.books['9780451524935'] = Book(isbn='9780451524935', title='1984', author='George Orwell', isAvailable=True)
    lib.books['9780060935467'] = Book(isbn='9780060935467', title='To Kill a Mockingbird', author='Harper Lee', isAvailable=False)
    lib.books['9781593279288'] = Book(isbn='9781593279288', title='Python Crash Course', author='Eric Matthes', isAvailable=False)
    lib.books['9780439708180'] = Book(isbn='9780439708180', title='Harry Potter and the Sorcerer\'s Stone', author='J.K. Rowling', isAvailable=False)
    lib.books['9780545010221'] = Book(isbn='9780545010221', title='Harry Potter and the Chamber of Secrets', author='J.K. Rowling', isAvailable=False)
    lib.books['9780439136365'] = Book(isbn='9780439136365', title='Harry Potter and the Prisoner of Azkaban', author='J.K. Rowling', isAvailable=False)
    lib.books['9780439139601'] = Book(isbn='9780439139601', title='Harry Potter and the Goblet of Fire', author='J.K. Rowling', isAvailable=False)
    lib.books['9780439358071'] = Book(isbn='9780439358071', title='Harry Potter and the Order of the Phoenix', author='J.K. Rowling', isAvailable=True)
    lib.books['9780439785969'] = Book(isbn='9780439785969', title='Harry Potter and the Half-Blood Prince', author='J.K. Rowling', isAvailable=True)
    lib.books['9780545139700'] = Book(isbn='9780545139700', title='Harry Potter and the Deathly Hallows', author='J.K. Rowling', isAvailable=True)
    lib.books['9780141439518'] = Book(isbn='9780141439518', title='Pride and Prejudice', author='Jane Austen', isAvailable=True)

    # Create members with all attributes
    # Member 1: No fines, 2 books borrowed
    lib.members[1] = Member(memberId=1, name='Alice', borrowedBooks=['9780060935467', '9781593279288'], fineBalance=0.0)

    # Member 2: Unpaid fine under $10, 1 book borrowed
    lib.members[2] = Member(memberId=2, name='Bob', borrowedBooks=['9780439708180'], fineBalance=5.0)

    # Member 3: Unpaid fine over $10, no books borrowed (can't borrow more)
    lib.members[3] = Member(memberId=3, name='Charlie', borrowedBooks=[], fineBalance=14.50)

    # Member 4: At borrow limit (3 books), no fines
    lib.members[4] = Member(memberId=4, name='Diana', borrowedBooks=['9780545010221', '9780439136365', '9780439139601'], fineBalance=0.0)

    # Create borrow records with various scenarios
    today = date.today()  # March 29, 2026

    # Alice's records - all on time or recently returned
    lib.borrow_records.append(BorrowRecord(
        memberId=1, isbn='9780060935467',
        checkout_date=today - timedelta(days=10),
        due_date=today - timedelta(days=10) + timedelta(days=14),
        return_date=None, fine_charged=0.0, fine_paid=0.0
    ))
    lib.borrow_records.append(BorrowRecord(
        memberId=1, isbn='9781593279288',
        checkout_date=today - timedelta(days=5),
        due_date=today - timedelta(days=5) + timedelta(days=14),
        return_date=None, fine_charged=0.0, fine_paid=0.0
    ))

    # Bob's record - overdue, fine charged but not paid
    checkout_date = today - timedelta(days=20)
    due_date = checkout_date + timedelta(days=14)
    return_date = today - timedelta(days=2)  # Returned 2 days ago
    overdue_days = (return_date - due_date).days  # 4 days overdue
    fine = overdue_days * 0.5  # $2.00
    lib.borrow_records.append(BorrowRecord(
        memberId=2, isbn='9780439708180',
        checkout_date=checkout_date, due_date=due_date,
        return_date=return_date, fine_charged=fine, fine_paid=0.0
    ))

    # Charlie's records - multiple overdue returns, total fine $15
    # First book: 10 days overdue
    checkout1 = today - timedelta(days=30)
    due1 = checkout1 + timedelta(days=14)
    return1 = today - timedelta(days=5)
    fine1 = ((return1 - due1).days) * 0.5  # 11 days * 0.5 = $5.50
    lib.borrow_records.append(BorrowRecord(
        memberId=3, isbn='9780451524935',
        checkout_date=checkout1, due_date=due1,
        return_date=return1, fine_charged=fine1, fine_paid=0.0
    ))

    # Second book: 15 days overdue
    checkout2 = today - timedelta(days=35)
    due2 = checkout2 + timedelta(days=14)
    return2 = today - timedelta(days=3)
    fine2 = ((return2 - due2).days) * 0.5  # 18 days * 0.5 = $9.00
    lib.borrow_records.append(BorrowRecord(
        memberId=3, isbn='9780060935467',
        checkout_date=checkout2, due_date=due2,
        return_date=return2, fine_charged=fine2, fine_paid=0.0
    ))

    # Diana's records - at limit, all on time
    lib.borrow_records.append(BorrowRecord(
        memberId=4, isbn='9780545010221',
        checkout_date=today - timedelta(days=7),
        due_date=today - timedelta(days=7) + timedelta(days=14),
        return_date=None, fine_charged=0.0, fine_paid=0.0
    ))
    lib.borrow_records.append(BorrowRecord(
        memberId=4, isbn='9780439136365',
        checkout_date=today - timedelta(days=3),
        due_date=today - timedelta(days=3) + timedelta(days=14),
        return_date=None, fine_charged=0.0, fine_paid=0.0
    ))
    lib.borrow_records.append(BorrowRecord(
        memberId=4, isbn='9780439139601',
        checkout_date=today - timedelta(days=1),
        due_date=today - timedelta(days=1) + timedelta(days=14),
        return_date=None, fine_charged=0.0, fine_paid=0.0
    ))