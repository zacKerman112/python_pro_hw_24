from datetime import date
from typing import Any

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from ninja import Schema, NinjaAPI

from .models import Genre, Movie, Review


api = NinjaAPI(title="Movie Collection API", version="1.0.0")


class GenreIn(Schema):
    name: str


class GenreOut(Schema):
    id: int
    name: str


class MovieIn(Schema):
    title: str
    description: str
    filmed_at: date
    genre_id: int | None = None


class MovieUpdate(Schema):
    title: str | None = None
    description: str | None = None
    filmed_at: date | None = None
    genre_id: int | None = None


class MovieOut(Schema):
    id: int
    title: str
    description: str
    filmed_at: date
    genre_id: int | None = None


class ReviewIn(Schema):
    movie_id: int
    rating: int
    comment: str


class ReviewOut(Schema):
    id: int
    movie_id: int
    rating: int
    comment: str


@api.get("/genres", response=list[GenreOut])
@login_required
def list_genres(request: HttpRequest) -> Any:
    """Return all genres."""
    return Genre.objects.all()


@api.post("/genres", response=GenreOut)
@login_required
def create_genre(request: HttpRequest, payload: GenreIn) -> Any:
    """Create a new genre."""
    return Genre.objects.create(**payload.dict())


@api.get("/movies", response=list[MovieOut])
@login_required
def list_movies(
    request: HttpRequest,
    genre_id: int = None,
    rating: int = None,
    filmed_at: date = None,
    search: str = None,
) -> Any:
    """Return movies filtered by genre, rating, date, or title."""
    movies = Movie.objects.all()

    if genre_id:
        movies = movies.filter(genre_id=genre_id)

    if rating:
        movies = movies.filter(reviews__rating=rating)

    if search:
        movies = movies.filter(title__icontains=search)

    if filmed_at:
        movies = movies.filter(filmed_at=filmed_at)

    return movies.distinct()


@api.get("/movies/{movie_id}", response=MovieOut)
@login_required
def get_movie(request: HttpRequest, movie_id: int) -> Any:
    """Return a single movie by ID."""
    return get_object_or_404(Movie, id=movie_id)


@api.post("/movies", response=MovieOut)
@login_required
def create_movie(request: HttpRequest, payload: MovieIn) -> Any:
    """Create a new movie."""
    return Movie.objects.create(**payload.dict())


@api.delete("/movies/{movie_id}")
@login_required
def delete_movie(request: HttpRequest, movie_id: int) -> dict[str, bool]:
    """Delete a movie."""
    movie = get_object_or_404(Movie, id=movie_id)
    movie.delete()
    return {"success": True}


@api.patch("/movies/{movie_id}", response=MovieOut)
@login_required
def patch_movie(request: HttpRequest, movie_id: int, payload: MovieUpdate) -> Any:
    """Partially update an existing movie."""
    movie = get_object_or_404(Movie, id=movie_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(movie, attr, value)
    movie.save()
    return movie


@api.put("/movies/{movie_id}", response=MovieOut)
@login_required
def update_movie(request: HttpRequest, movie_id: int, payload: MovieIn) -> Any:
    """Replace an existing movie."""
    movie = get_object_or_404(Movie, id=movie_id)
    for attr, value in payload.dict().items():
        setattr(movie, attr, value)
    movie.save()
    return movie


@api.get("/reviews", response=list[ReviewOut])
@login_required
def list_reviews(request: HttpRequest, movie_id: int = None) -> Any:
    """Return reviews, optionally filtered by movie."""
    reviews = Review.objects.all()
    if movie_id:
        reviews = reviews.filter(movie_id=movie_id)
    return reviews


@api.post("/reviews", response=ReviewOut)
@login_required
def create_review(request: HttpRequest, payload: ReviewIn) -> Any:
    """Create a new movie review."""
    return Review.objects.create(**payload.dict())