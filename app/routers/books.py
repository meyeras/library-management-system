
from typing import List
from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import PositiveInt
from sqlalchemy import not_, exists
from sqlalchemy.orm import Session
from app.schemas import BookBaseSchema, BookQueryParams, BookCreateSchema, BookUpdateSchema, BooksResponseSchema, BookDetailsResponseSchema
from app.models import Book, Copy, User, Borrow, Author
from app.database import get_db
from app.auth import get_current_user
from app.routers.utils import count_available_copies,count_borrowed_copies, borrowed_copy_for_user_and_book
router = APIRouter()

@router.get("/", response_model=BooksResponseSchema)
def get_books(
    query_params: BookQueryParams = Depends(),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    # Define the base query to fetch books from the database
    base_query = db.query(Book)

    # Apply filters based on query parameters
    if query_params.title:
        base_query = base_query.filter(Book.title.ilike(f"%{query_params.title}%"))

    if query_params.author:
        base_query = base_query.join(Book.author).filter(Author.name.ilike(f"%{query_params.author}%"))

    if query_params.available is not None:
        base_query = base_query.filter(~Book.copies.any(Copy.borrowed == query_params.available))

 
    # Apply pagination
    offset = (page - 1) * limit
    books = base_query.offset(offset).limit(limit+1).all()
    books = [BookBaseSchema.from_model(book) for book in books]

    # Check if there are more books available
    has_more = len(books) > limit

    # If there are more books, remove the extra book used for determining the has_more flag
    if has_more:
        books = books[:-1]
    return BooksResponseSchema(books=books, page=page, count=len(books), has_more=has_more)


@router.post("/")
def create_books(
    books_list: List[BookCreateSchema],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    
    books = [book.trim_data() for book in books_list]
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Unauthorized access")

    for book in books:
        # Check if the author exists, or create a new one
        author = db.query(Author).filter(Author.name == book.author).first()
        if not author:
            author = Author(name=book.author)
            db.add(author)
            db.commit()
            db.refresh(author)

        # Check if the book exists already (same isbn)
        # If the book already exists, we will ignore the author or the title if they differ from the data in db
        book_in_library = db.query(Book).filter(Book.isbn == book.isbn).first()
        if book_in_library:
            for _ in range(book.copies):
                new_copy = Copy(book_id=book_in_library.id, borrowed=False)
                db.add(new_copy)
                db.commit()
                db.refresh(new_copy)
        else:            
            # Create the book with the specified number of copies
            new_book = Book(
                title=book.title,
                author_id=author.id,
                isbn= book.isbn
                # Set other properties as needed
            )
            db.add(new_book)
            db.commit()
            db.refresh(new_book)

            # Create the copies
            for _ in range(book.copies):
                new_copy = Copy(book_id=new_book.id, borrowed=False)
                db.add(new_copy)
                db.commit()
                db.refresh(new_copy)

    return {"message": "Books added successfully"}


@router.get("/{book_id}", response_model=BookDetailsResponseSchema)
def get_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    book = db.query(Book).get(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    response_model = BookDetailsResponseSchema(
        id=book.id,
        title=book.title,
        author=book.author.name,
        isbn=book.isbn,
    )

    if current_user.is_admin:
        num_copies = db.query(Copy).filter(Copy.book_id == book.id).count()
        response_model.num_copies = num_copies

        num_borrowed_copies = count_borrowed_copies(book_id, db)
        response_model.num_borrowed_copies = num_borrowed_copies

    return response_model


@router.put("/{book_id}")
def update_book(
    book_id: int,
    book_data: BookUpdateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    book_data = book_data.trim_data()
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Unauthorized access")

    # Fetch the book from the database
    book = db.query(Book).get(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    # Check if any copies are currently borrowed
    borrowed_copies = count_borrowed_copies(book_id, db)

    if book_data.copies is not None:
        if book_data.copies < borrowed_copies:
            raise HTTPException(status_code=400, detail="Cannot reduce the number of copies below the number of borrowed copies")

        if book_data.copies < book.copies.count():
            excess_copies = book.copies.count() - book_data.copies
            excess_copies_query = (
                db.query(Copy)
                .filter(Copy.book_id == book.id, Copy.borrowed == False)
                .order_by(Copy.id.asc())
                .limit(excess_copies)
            )
            excess_copies_instances = excess_copies_query.all()  # Execute the query and get the instances
            for copy in excess_copies_instances:
                db.delete(copy)
        elif book_data.copies > book.copies.count():
            num_additional_copies = book_data.copies - book.copies.count()
            for _ in range(num_additional_copies):
                new_copy = Copy(book_id=book.id, borrowed=False)
                db.add(new_copy)
                db.commit()
                db.refresh(new_copy)

    if book_data.title:
        book.title = book_data.title
    if book_data.author:
        author = db.query(Author).filter(Author.name == book_data.author).first()
        if not author:
            author = Author(name=book_data.author)
            db.add(author)
            db.commit()
            db.refresh(author)
        book.author_id = author.id
    if book_data.isbn:
        book.isbn = book_data.isbn

    # Commit the changes to the database
    db.commit()
    db.refresh(book)

    return {"message": "Book updated successfully"}


@router.delete("/{book_id}")
def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Unauthorized access")

    # Fetch the book from the database
    book = db.query(Book).get(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    # Check if any copies are currently borrowed
    borrowed_copies = count_borrowed_copies(book_id, db)
    if borrowed_copies > 0:
        raise HTTPException(status_code=400, detail="Cannot delete a book with borrowed copies")

    # Delete the book copies
    db.query(Copy).filter(Copy.book_id == book.id).delete()

    # Delete the book
    db.delete(book)

    # Commit the changes to the database
    db.commit()

    return {"message": "Book deleted successfully"}
