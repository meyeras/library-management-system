
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.auth import get_current_user
from app.database import get_db
from app.models import User, Copy, Book, Borrow, Author
from sqlalchemy.sql.operators import is_
from datetime import datetime
from app.routers.utils import borrowed_record_for_user_and_book, count_available_copies, get_available_copy, get_available_copies
from app.schemas import BorrowResponse, BorrowsListResponse
from datetime import datetime, timedelta
from typing import List


router = APIRouter()
# TODO: Move these parameters to some environment file
MAX_BORROWS = 10
MAX_BORROW_TIME = 14
BORROW_FINE_PER_OVERDUE_DAY = 0.10
  
@router.post("/books/{book_id}/borrow")
def borrow_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if the user has reached the maximum number of borrows
    num_borrows = db.query(Borrow).filter_by(user_id=current_user.id, return_date=None).count()
    if num_borrows >= MAX_BORROWS:
        raise HTTPException(status_code=400, detail="Maximum number of borrows reached")

    # Check if the book exists and there are available copies
    book = db.query(Book).filter_by(id=book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    available_copies = count_available_copies(book_id,db)
    if available_copies == 0:
        raise HTTPException(status_code=400, detail="No copies available for borrowing")

    # Check if the user has already borrowed a copy of the same book
    existing_borrow = borrowed_record_for_user_and_book(current_user.id, book_id, db)
    if existing_borrow:
        raise HTTPException(status_code=400, detail="You have already borrowed this book")

    # Get available copy
    available_copies = [copy.id for copy in get_available_copies(book_id, db)]
    available_copy = get_available_copy(book_id, db)
    borrow = Borrow(
        copy_id=available_copy.id,
        user_id=current_user.id,
        borrow_date=datetime.now(),
        return_date=None
    )

    # Add the new Borrow object to the session
    db.add(borrow)

    # Update the borrowed status of the Copy
    available_copy.borrowed = True

    # Commit the changes as a transaction
    db.commit()
 
    return {"message": "Book borrowed successfully"}

@router.post("/books/{book_id}/return")
def return_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if the book exists
    book = db.query(Book).filter_by(id=book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    borrow = borrowed_record_for_user_and_book(current_user.id, book_id, db)
   # If no borrowed copy found, raise an exception
    if not borrow:
        raise HTTPException(status_code=400, detail="You have not borrowed this book")

    # Set the return date for the borrow record
    borrow.return_date = datetime.now()

    # Update the copy's borrowed flag to False
    borrowed_copy = borrow.copy
    borrowed_copy.borrowed = False

    db.commit()

    return {"message": "Book returned successfully"}



# Shared method to get the list of borrows for a user
def get_user_borrows(user_id: int, current_user: User, db: Session) -> BorrowsListResponse:
    if not current_user.is_admin and user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not have permission to access this resource")

    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    borrows = (
        db.query(Borrow)
        .join(Copy)
        .join(Book)
        .join(Author)
        .options(joinedload(Borrow.copy).joinedload(Copy.book).joinedload(Book.author))
        .filter(Borrow.user_id == user_id, Borrow.return_date.is_(None))
        .all()
    )

    borrow_list = []
    total_fine_amount = 0
    for borrow in borrows:
        # Calculate max return date based on borrow date and remaining days (in case of overdue, it will be negative)
        if isinstance(borrow.borrow_date, str):
            borrow.borrow_date = datetime.strptime(borrow.borrow_date, "%Y-%m-%d %H:%M:%S.%f")

        max_return_date = borrow.borrow_date + timedelta(days=MAX_BORROW_TIME) 
        remaining_days = (max_return_date.date() - datetime.now().date()).days
    
        # Calculate fine
        fine_amount = 0
        if remaining_days < 0:
            fine_amount = -remaining_days * BORROW_FINE_PER_OVERDUE_DAY
            total_fine_amount = total_fine_amount + fine_amount



        # Create BorrowResponse instance
        borrow_response = BorrowResponse(
            book_id=borrow.copy.book.id,
            book_title=borrow.copy.book.title,
            author=borrow.copy.book.author.name,
            borrow_date=borrow.borrow_date,
            remaining_days=remaining_days,
            fine_amount=fine_amount
        )

        borrow_list.append(borrow_response)

    return BorrowsListResponse(borrows=borrow_list, count=len(borrow_list),total_fine_amount=total_fine_amount)


# API to get the list of borrows for the currently logged-in user
@router.get("/users/me/borrows", response_model=BorrowsListResponse)
def get_current_user_borrows(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_user_borrows(current_user.id, current_user, db)

# API to get the list of borrows for a specific user (admin restricted)
@router.get("/users/{user_id}/borrows", response_model=BorrowsListResponse)
def get_some_user_borrows(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_user_borrows(user_id, current_user, db)

