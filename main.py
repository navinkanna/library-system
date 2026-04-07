from datetime import date, timedelta

from library import Library
from models import Book, Member, BorrowRecord
from errors import LibraryError
from utils import seed_data, format_date, format_currency


def print_menu() -> None:
    print_section('Library Checkout System')
    print('1. Add Book')
    print('2. Register Member')
    print('3. Checkout Book')
    print('4. Return Book')
    print('5. Calculate Fine')
    print('6. Show Available Books')
    print('7. Member Borrowing History')
    print('8. List Members')
    print('9. Pay Fine')
    print('0. Quit')

def print_section(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"{title}")
    print(f"{'=' * 60}")

def add_book(lib: Library) -> None:
    print_section('Add Book')
    isbn = input('ISBN: ').strip()
    title = input('Title: ').strip()
    author = input('Author: ').strip()
    book = Book(isbn=isbn, title=title, author=author, isAvailable=True)
    lib.addBook(book)
    print(f"Book '{title}' added.")


def register_member(lib: Library) -> None:
    print_section('Register Member')
    member_id = int(input('Member ID: ').strip())
    name = input('Name: ').strip()
    member = Member(memberId=member_id, name=name, borrowedBooks=[], fineBalance=0.0)
    lib.registerMember(member)
    print(f"Member '{name}' registered.")


def checkout_book(lib: Library) -> None:
    print_section('Checkout Book')
    member_id = int(input('Member ID: ').strip())
    isbn = input('ISBN: ').strip()
    record = lib.checkoutBook(member_id, isbn)
    print(f"Checked out '{isbn}' to member {member_id}. Due on {format_date(record.due_date)}")


def return_book(lib: Library) -> None:
    print_section('Return Book')
    member_id = int(input('Member ID: ').strip())
    isbn = input('ISBN: ').strip()
    record = lib.returnBook(member_id, isbn)
    if record.fine_charged > 0:
        print(f"Returned '{isbn}' with fine {format_currency(record.fine_charged)}")
    else:
        print(f"Returned '{isbn}' successfully")


def calculate_fine(lib: Library) -> None:
    print_section('Calculate Fine')
    member_id = int(input('Member ID: ').strip())
    fine = lib.calculateFine(member_id)
    print(f"Outstanding fine for member {member_id}: {format_currency(fine)}")


def show_available_books(lib: Library) -> None:
    available = lib.getAvailableBooks()
    print_section('Available Books')
    if not available:
        print('No available books.')
    else:
        for book in available:
            print(f"{book.isbn}: {book.title} by {book.author}")


def member_history(lib: Library) -> None:
    print_section('Member Borrowing History')
    member_id = int(input('Member ID: ').strip())
    history = lib.getMemberBorrowingHistory(member_id)
    if not history:
        print('No borrowing records found.')
    else:
        for r in history:
            status = 'returned' if r.return_date else 'borrowed'
            return_date_str = format_date(r.return_date) if r.return_date else 'N/A'
            print(
                f"- {r.isbn} | checkout: {format_date(r.checkout_date)} | due: {format_date(r.due_date)} | return: {return_date_str} | status: {status} | fine accrued: {format_currency(r.fine_charged)} | fine paid: {format_currency(r.fine_paid)}"
            )


def list_members(lib: Library) -> None:
    members = lib.listMembers()
    print_section('Library Members')
    for m in members:
        print(f" - {m.memberId}: {m.name} | "
              f"Borrowed books: {len(m.borrowedBooks)} | "
              f"Fine Balance: {format_currency(m.fineBalance)}"
              )


def pay_fine(lib: Library) -> None:
    print_section('Pay Fine')
    member_id = int(input('Member ID: ').strip())

    # Show current total fine
    current_fine = lib.calculateFine(member_id)

    if current_fine <= 0:
        print("No outstanding fines to pay.")
        return
    print(f"Current outstanding fine: {format_currency(current_fine)}")
  
    amount = float(input('Payment amount: ').strip())
    if amount <= 0:
        print("Payment amount must be positive.")
        return
    remainder = lib.payFine(member_id, amount)
    paid_amount = amount - remainder
    new_balance = current_fine - paid_amount

    if remainder > 0:
        print(f"Payment processed. Remaining balance: {format_currency(new_balance)}")
        print(f"Refund amount: {format_currency(remainder)}")
    else:
        print(f"Payment processed. Remaining balance: {format_currency(new_balance)}")


def quit(lib: Library) -> bool:
    print_section('Exit')
    print('Goodbye!')
    return True


def invalid_choice(lib: Library) -> None:
    print_section('Invalid Selection')
    print('Invalid selection. Please choose a valid number.')


def run_console() -> None:
    lib = Library()
    seed_data(lib)

    actions = {
        '1': add_book,
        '2': register_member,
        '3': checkout_book,
        '4': return_book,
        '5': calculate_fine,
        '6': show_available_books,
        '7': member_history,
        '8': list_members,
        '9': pay_fine,
        '0': quit,
    }

    while True:
        print_menu()
        choice = input('Choose an option: ').strip()

        action = actions.get(choice, invalid_choice)

        try:
            if action == quit and action(lib):
                break
            else:
                action(lib)

        except ValueError:
            print('Invalid input. Please enter numeric values for IDs and amounts.')
        except LibraryError as e:
            print(f'Error: {e}')


if __name__ == '__main__':
    run_console()
