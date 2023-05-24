from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Author(Base):
    __tablename__ = 'authors'

    id = Column(Integer, primary_key=True)
    name = Column(String)


class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True)
    author_id = Column(Integer, ForeignKey('authors.id'))
    title = Column(String)
    isbn = Column(String)
    copies = relationship('Copy', backref='book', lazy='dynamic')
    author = relationship('Author', backref='books')


class Copy(Base):
    __tablename__ = 'copies'

    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey('books.id'))
    borrowed = Column(Boolean, default=False)
    # book = relationship('Book', backref='copies')



class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String)
    email = Column(String)
    password = Column(String)
    is_admin = Column(Boolean, default=False)


class Borrow(Base):
    __tablename__ = 'borrows'

    id = Column(Integer, primary_key=True)
    copy_id = Column(Integer, ForeignKey('copies.id'))
    user_id = Column(Integer, ForeignKey('users.id'))

    copy = relationship('Copy', backref='borrows')
    user = relationship('User', backref='borrows')
    borrow_date = Column(String)
    return_date = Column(String)
