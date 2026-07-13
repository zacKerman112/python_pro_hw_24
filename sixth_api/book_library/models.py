from django.contrib.auth.models import User
from django.db import models


class Author(models.Model):
    name = models.CharField(max_length=100)
    bio = models.TextField()

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    genres = models.ManyToManyField(Genre, related_name="books", blank=True)
    publication_date = models.DateField()

    def __str__(self):
        return self.title


class Rental(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="rentals")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="rentals")
    rented_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField()
    returned_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"

