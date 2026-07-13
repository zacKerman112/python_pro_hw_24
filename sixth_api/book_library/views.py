from datetime import date, datetime
from typing import Any

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from ninja import NinjaAPI, Schema

from .models import Author, Book, Genre, Rental


api = NinjaAPI(title="Book Library API", version="1.0.0")


class AuthorIn(Schema):
    name: str
    bio: str


class AuthorOut(Schema):
    id: int
    name: str
    bio: str


class BookIn(Schema):
    title: str
    author_id: int
    publication_date: date
    genre_ids: list[int] = []


class BookUpdate(Schema):
    title: str | None = None
    author_id: int | None = None
    publication_date: date | None = None
    genre_ids: list[int] | None = None


class BookOut(Schema):
    id: int
    title: str
    author_id: int
    publication_date: date


class GenreIn(Schema):
    name: str
    description: str


class GenreOut(Schema):
    id: int
    name: str
    description: str


class RentalIn(Schema):
    user_id: int
    book_id: int
    due_date: date


class RentalOut(Schema):
    id: int
    user_id: int
    book_id: int
    rented_at: datetime
    due_date: date
    returned_at: datetime | None = None


@api.get("/authors", response=list[AuthorOut])
@login_required
def list_authors(request: HttpRequest) -> Any:
    """Return all authors."""
    return Author.objects.all()


@api.post("/authors", response=AuthorOut)
@login_required
def create_author(request: HttpRequest, author: AuthorIn) -> Any:
    """Create a new author."""
    return Author.objects.create(**author.dict())


@api.get("/genres", response=list[GenreOut])
@login_required
def list_genres(request: HttpRequest) -> Any:
    """Return all genres."""
    return Genre.objects.all()


@api.post("/genres", response=GenreOut)
@login_required
def create_genre(request: HttpRequest, genre: GenreIn) -> Any:
    """Create a new genre."""
    return Genre.objects.create(**genre.dict())


@api.get("/books", response=list[BookOut])
@login_required
def list_books(
    request: HttpRequest,
    title: str = None,
    author: str = None,
    genre: str = None,
) -> Any:
    """Return books filtered by title, author, or genre."""
    books = Book.objects.all()

    if title:
        books = books.filter(title__icontains=title)

    if author:
        books = books.filter(author__name__icontains=author)

    if genre:
        books = books.filter(genres__name__icontains=genre)

    return books.distinct()


@api.post("/books", response=BookOut)
@login_required
def create_book(request: HttpRequest, book: BookIn) -> Any:
    """Create a new book."""
    get_object_or_404(Author, id=book.author_id)
    genre_ids = book.genre_ids
    book_obj = Book.objects.create(
        title=book.title,
        author_id=book.author_id,
        publication_date=book.publication_date,
    )
    book_obj.genres.set(genre_ids)
    return book_obj


@api.get("/books/{id}", response=BookOut)
@login_required
def get_book(request: HttpRequest, id: int) -> Any:
    """Return a single book by ID."""
    return get_object_or_404(Book, id=id)


@api.put("/books/{id}", response=BookOut)
@login_required
def update_book(request: HttpRequest, id: int, book: BookIn) -> Any:
    """Replace a book."""
    get_object_or_404(Author, id=book.author_id)
    book_obj = get_object_or_404(Book, id=id)
    book_obj.title = book.title
    book_obj.author_id = book.author_id
    book_obj.publication_date = book.publication_date
    book_obj.save()
    book_obj.genres.set(book.genre_ids)
    return book_obj


@api.patch("/books/{id}", response=BookOut)
@login_required
def patch_book(request: HttpRequest, id: int, book: BookUpdate) -> Any:
    """Partially update a book."""
    book_obj = get_object_or_404(Book, id=id)
    data = book.dict(exclude_unset=True)
    genre_ids = data.pop("genre_ids", None)

    if "author_id" in data:
        get_object_or_404(Author, id=data["author_id"])

    for attr, value in data.items():
        setattr(book_obj, attr, value)

    book_obj.save()

    if genre_ids is not None:
        book_obj.genres.set(genre_ids)

    return book_obj


@api.delete("/books/{id}")
@login_required
def delete_book(request: HttpRequest, id: int) -> dict[str, bool]:
    """Delete a book."""
    book_obj = get_object_or_404(Book, id=id)
    book_obj.delete()
    return {"success": True}


@api.get("/rentals", response=list[RentalOut])
@login_required
def list_rentals(request: HttpRequest) -> Any:
    """Return all book rentals."""
    return Rental.objects.all()


@api.post("/rentals", response=RentalOut)
@login_required
def create_rental(request: HttpRequest, rental: RentalIn) -> Any:
    """Create a new book rental."""
    get_object_or_404(User, id=rental.user_id)
    get_object_or_404(Book, id=rental.book_id)
    return Rental.objects.create(**rental.dict())


@api.patch("/rentals/{rental_id}/return", response=RentalOut)
@login_required
def return_book(request: HttpRequest, rental_id: int) -> Any:
    """Mark a rental as returned."""
    rental = get_object_or_404(Rental, id=rental_id)
    rental.returned_at = datetime.now()
    rental.save()
    return rental
