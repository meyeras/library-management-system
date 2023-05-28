from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, exists
from app.models import User, Copy, Book, Borrow
from datetime import datetime
from pydantic.types import Optional

def get_ongoing_borrows(book_id: int, db: Session, user_id=None):
    ongoing_borrows_query = db.query(Borrow).join(Copy).filter(
        Borrow.copy_id == Copy.id,
        Copy.book_id == book_id,
        Borrow.return_date == None
    )
    if user_id is not None:
        ongoing_borrows_query = ongoing_borrows_query.filter(user_id==Borrow.user_id)
    
    return ongoing_borrows_query.all()

def get_copies_from_borrows(ongoing_borrows):
    copies = [borrow.copy for borrow in ongoing_borrows]
    return copies

def borrowed_record_for_user_and_book(user_id:str, book_id:int, db: Session):
    ongoing_borrows = get_ongoing_borrows(user_id=user_id, book_id=book_id, db=db)
    print("ongoing borrows = ", ongoing_borrows)
    return ongoing_borrows[0] if ongoing_borrows else None

def borrowed_copy_for_user_and_book(user_id:str, book_id:int, db: Session):
    borrow_record = borrowed_record_for_user_and_book(user_id=user_id, book_id=book_id, db=db)
    return borrow_record.copy if borrow_record else None

def count_available_copies(book_id: int, db: Session) -> int:
    return (
        db.query(Copy)
        .join(Book)
        .filter(Book.id == book_id, Copy.borrowed == False)
        .count()
    )

def count_borrowed_copies(book_id: int, db: Session) -> int:
    return (
        db.query(Copy)
        .join(Book)
        .filter(Book.id == book_id, Copy.borrowed == True)
        .count()
    )

def get_available_copies(book_id: int, db: Session):
    return (
        db.query(Copy)
        .join(Book)
        .filter(Book.id == book_id, Copy.borrowed == False)
        .all()
    )

def get_available_copy(book_id: int, db: Session):
    try:
        copy = (
            db.query(Copy)
            .join(Book)
            .filter(Book.id == book_id, Copy.borrowed == False)
            .first()
        )
    except Exception as e:
        print("Cannot get first available copy:%s",e)
    else:    
        return copy

# def count_available_copies(book_id: int, db: Session) -> int:
#     return (
#         db.query(func.count(Copy.id))
#         .join(Book)
#         .outerjoin(Borrow, Borrow.copy_id == Copy.id)
#         .filter(Book.id == book_id, Borrow.return_date.is_(None))
#         .scalar()
#     )

# def count_borrowed_copies(book_id: int, db: Session) -> int:
#     return (
#         db.query(func.count(Borrow.copy_id))
#         .filter(Borrow.copy.has(book_id=book_id), Borrow.return_date.is_(None))
#         .scalar()
#     )


# def get_available_copy(book_id: int, db: Session):
#     available_copies = get_available_copies(book_id, db)
#     return available_copies[0] if available_copies else None


# def get_available_copies(book_id: int, db: Session):
#     returned_copies = (
#         db.query(Copy)
#         .join(Borrow, and_(Copy.id == Borrow.copy_id, Borrow.return_date.isnot(None)))
#         .filter(Copy.book_id == book_id)
#         .all()
#     )

#     available_copies = (
#         db.query(Copy)
#         .filter(Copy.book_id == book_id)
#         .filter(~Copy.id.in_(db.query(Borrow.copy_id).subquery()))
#         .all()
#     )

#     all_copies = returned_copies + available_copies
#     return all_copies 
