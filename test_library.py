#!/usr/bin/env python3
"""
Comprehensive test suite for the Library Checkout System.
Tests all happy paths and negative paths.
"""

import sys
from datetime import date, timedelta

from library import Library
from models import Book, Member, BorrowRecord
from errors import (
    LibraryError, BookNotFoundError, MemberNotFoundError,
    AlreadyCheckedOutError, NotCheckedOutError, BorrowingLimitExceededError,
    UnpaidFineError, DuplicateBookError, DuplicateMemberError
)
from utils import seed_data, format_date, format_currency


def run_test(test_name, test_func):
    """Run a single test and report results."""
    print(f"🧪 {test_name}")
    try:
        test_func()
        print("✅ PASSED")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def test_add_book_happy():
    lib = Library()
    book = Book(isbn='1234567890', title='Test Book', author='Test Author')
    lib.addBook(book)
    assert book.isbn in lib.books


def test_add_book_duplicate():
    lib = Library()
    book1 = Book(isbn='1234567890', title='Test Book 1', author='Author 1')
    book2 = Book(isbn='1234567890', title='Test Book 2', author='Author 2')
    lib.addBook(book1)
    try:
        lib.addBook(book2)
        assert False
    except DuplicateBookError:
        pass


def test_register_member_happy():
    lib = Library()
    member = Member(memberId=100, name='Test Member')
    lib.registerMember(member)
    assert member.memberId in lib.members


def test_register_member_duplicate():
    lib = Library()
    member1 = Member(memberId=100, name='Member 1')
    member2 = Member(memberId=100, name='Member 2')
    lib.registerMember(member1)
    try:
        lib.registerMember(member2)
        assert False
    except DuplicateMemberError:
        pass


def test_checkout_book_happy():
    lib = Library()
    book = Book(isbn='1234567890', title='Test Book', author='Test Author')
    member = Member(memberId=100, name='Test Member')
    lib.addBook(book)
    lib.registerMember(member)
    record = lib.checkoutBook(100, '1234567890')
    assert not book.isAvailable
    assert '1234567890' in member.borrowedBooks


def test_checkout_book_not_found():
    lib = Library()
    member = Member(memberId=100, name='Test Member')
    lib.registerMember(member)
    try:
        lib.checkoutBook(100, 'nonexistent')
        assert False
    except BookNotFoundError:
        pass


def test_checkout_member_not_found():
    lib = Library()
    book = Book(isbn='1234567890', title='Test Book', author='Test Author')
    lib.addBook(book)
    try:
        lib.checkoutBook(999, '1234567890')
        assert False
    except MemberNotFoundError:
        pass


def test_checkout_already_checked_out():
    lib = Library()
    book = Book(isbn='1234567890', title='Test Book', author='Test Author')
    member1 = Member(memberId=100, name='Member 1')
    member2 = Member(memberId=101, name='Member 2')
    lib.addBook(book)
    lib.registerMember(member1)
    lib.registerMember(member2)
    lib.checkoutBook(100, '1234567890')
    try:
        lib.checkoutBook(101, '1234567890')
        assert False
    except AlreadyCheckedOutError:
        pass


def test_checkout_borrow_limit():
    lib = Library()
    member = Member(memberId=100, name='Test Member',
                   borrowedBooks=['book1', 'book2', 'book3'])
    lib.registerMember(member)
    book = Book(isbn='1234567890', title='Test Book', author='Test Author')
    lib.addBook(book)
    try:
        lib.checkoutBook(100, '1234567890')
        assert False
    except BorrowingLimitExceededError:
        pass


def test_checkout_unpaid_fine():
    lib = Library()
    member = Member(memberId=100, name='Test Member')
    lib.registerMember(member)
    # Add an overdue borrow record that creates fines over $10
    record = BorrowRecord(
        memberId=100, isbn='oldbook',
        checkout_date=date.today() - timedelta(days=39),
        due_date=date.today() - timedelta(days=25),
        return_date=date.today(), fine_charged=0.0, fine_paid=0.0
    )
    lib.borrow_records.append(record)
    # Calculate fine to sync balance
    lib.calculateFine(100)
    book = Book(isbn='1234567890', title='Test Book', author='Test Author')
    lib.addBook(book)
    try:
        lib.checkoutBook(100, '1234567890')
        assert False
    except UnpaidFineError:
        pass


def test_return_book_happy():
    lib = Library()
    book = Book(isbn='1234567890', title='Test Book', author='Test Author')
    member = Member(memberId=100, name='Test Member')
    lib.addBook(book)
    lib.registerMember(member)
    lib.checkoutBook(100, '1234567890')
    record = lib.returnBook(100, '1234567890')
    assert book.isAvailable
    assert '1234567890' not in member.borrowedBooks


def test_return_book_not_checked_out():
    lib = Library()
    book = Book(isbn='1234567890', title='Test Book', author='Test Author')
    member1 = Member(memberId=100, name='Member 1')
    member2 = Member(memberId=101, name='Member 2')
    lib.addBook(book)
    lib.registerMember(member1)
    lib.registerMember(member2)
    lib.checkoutBook(100, '1234567890')
    try:
        lib.returnBook(101, '1234567890')
        assert False
    except NotCheckedOutError:
        pass


def test_return_book_not_found():
    lib = Library()
    member = Member(memberId=100, name='Test Member')
    lib.registerMember(member)
    try:
        lib.returnBook(100, 'nonexistent')
        assert False
    except BookNotFoundError:
        pass


def test_return_member_not_found():
    lib = Library()
    book = Book(isbn='1234567890', title='Test Book', author='Test Author')
    lib.addBook(book)
    try:
        lib.returnBook(999, '1234567890')
        assert False
    except MemberNotFoundError:
        pass


def test_calculate_fine_happy():
    lib = Library()
    member = Member(memberId=100, name='Test Member')
    lib.registerMember(member)
    record = BorrowRecord(
        memberId=100, isbn='1234567890',
        checkout_date=date.today() - timedelta(days=20),
        due_date=date.today() - timedelta(days=6),
        return_date=date.today(), fine_charged=0.0, fine_paid=0.0
    )
    lib.borrow_records.append(record)
    total_fine = lib.calculateFine(100)
    assert total_fine == 3.0  # 6 days overdue * $0.5


def test_calculate_fine_member_not_found():
    lib = Library()
    try:
        lib.calculateFine(999)
        assert False
    except MemberNotFoundError:
        pass


def test_pay_fine_happy():
    lib = Library()
    member = Member(memberId=100, name='Test Member', fineBalance=3.0)
    lib.registerMember(member)
    record = BorrowRecord(
        memberId=100, isbn='1234567890',
        checkout_date=date.today() - timedelta(days=20),
        due_date=date.today() - timedelta(days=6),
        return_date=date.today(), fine_charged=3.0, fine_paid=0.0
    )
    lib.borrow_records.append(record)
    remaining = lib.payFine(100, 3.0)
    assert remaining == 0.0
    assert record.fine_paid == 3.0
    assert member.fineBalance == 0.0  # calculateFine recalculates based on dates (6 days * 0.5 = 3.0)


def test_pay_fine_member_not_found():
    lib = Library()
    try:
        lib.payFine(999, 10.0)
        assert False
    except MemberNotFoundError:
        pass


def test_pay_fine_negative():
    lib = Library()
    member = Member(memberId=100, name='Test Member')
    lib.registerMember(member)
    try:
        lib.payFine(100, -5.0)
        assert False
    except ValueError:
        pass


def test_pay_fine_no_fines():
    lib = Library()
    member = Member(memberId=100, name='Test Member', fineBalance=0.0)
    lib.registerMember(member)
    remaining = lib.payFine(100, 10.0)
    assert remaining == 10.0


def test_get_available_books():
    lib = Library()
    book1 = Book(isbn='1', title='Book 1', author='Author 1', isAvailable=True)
    book2 = Book(isbn='2', title='Book 2', author='Author 2', isAvailable=False)
    book3 = Book(isbn='3', title='Book 3', author='Author 3', isAvailable=True)
    lib.addBook(book1)
    lib.addBook(book2)
    lib.addBook(book3)
    available = lib.getAvailableBooks()
    assert len(available) == 2


def test_get_member_history_happy():
    lib = Library()
    member = Member(memberId=100, name='Test Member')
    lib.registerMember(member)
    record1 = BorrowRecord(memberId=100, isbn='1',
                          checkout_date=date.today(),
                          due_date=date.today() + timedelta(days=14))
    record2 = BorrowRecord(memberId=100, isbn='2',
                          checkout_date=date.today() - timedelta(days=10),
                          due_date=date.today() - timedelta(days=10) + timedelta(days=14),
                          return_date=date.today())
    lib.borrow_records.extend([record1, record2])
    history = lib.getMemberBorrowingHistory(100)
    assert len(history) == 2


def test_get_member_history_member_not_found():
    lib = Library()
    try:
        lib.getMemberBorrowingHistory(999)
        assert False
    except MemberNotFoundError:
        pass


def test_list_members():
    lib = Library()
    member1 = Member(memberId=100, name='Member 1')
    member2 = Member(memberId=101, name='Member 2')
    lib.registerMember(member1)
    lib.registerMember(member2)
    members = lib.listMembers()
    assert len(members) == 2


def test_seed_data_integration():
    lib = Library()
    seed_data(lib)
    available = lib.getAvailableBooks()
    assert len(available) > 0
    alice_history = lib.getMemberBorrowingHistory(1)
    assert len(alice_history) == 2
    bob_fine = lib.calculateFine(2)
    assert bob_fine == 2.0  # 4 days overdue * $0.50/day
    charlie_fine = lib.calculateFine(3)
    assert charlie_fine == 14.50  # 11 days + 18 days overdue * $0.50/day


def main():
    print("🚀 Starting Comprehensive Library System Test Suite")
    print("=" * 60)

    tests = [
        ("Add Book - Happy Path", test_add_book_happy),
        ("Add Book - Duplicate", test_add_book_duplicate),
        ("Register Member - Happy Path", test_register_member_happy),
        ("Register Member - Duplicate", test_register_member_duplicate),
        ("Checkout Book - Happy Path", test_checkout_book_happy),
        ("Checkout Book - Book Not Found", test_checkout_book_not_found),
        ("Checkout Book - Member Not Found", test_checkout_member_not_found),
        ("Checkout Book - Already Checked Out", test_checkout_already_checked_out),
        ("Checkout Book - Borrow Limit Exceeded", test_checkout_borrow_limit),
        ("Checkout Book - Unpaid Fine", test_checkout_unpaid_fine),
        ("Return Book - Happy Path", test_return_book_happy),
        ("Return Book - Not Checked Out", test_return_book_not_checked_out),
        ("Return Book - Book Not Found", test_return_book_not_found),
        ("Return Book - Member Not Found", test_return_member_not_found),
        ("Calculate Fine - Happy Path", test_calculate_fine_happy),
        ("Calculate Fine - Member Not Found", test_calculate_fine_member_not_found),
        ("Pay Fine - Happy Path", test_pay_fine_happy),
        ("Pay Fine - Member Not Found", test_pay_fine_member_not_found),
        ("Pay Fine - Negative Amount", test_pay_fine_negative),
        ("Pay Fine - No Fines", test_pay_fine_no_fines),
        ("Get Available Books", test_get_available_books),
        ("Get Member History - Happy Path", test_get_member_history_happy),
        ("Get Member History - Member Not Found", test_get_member_history_member_not_found),
        ("List Members", test_list_members),
        ("Seed Data Integration", test_seed_data_integration),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        if run_test(test_name, test_func):
            passed += 1
        else:
            failed += 1
        print()

    print("=" * 60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("🎉 All tests passed! The library system is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please review the errors above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)