from django.db import models


class Genre(models.Model):
    name = models.CharField(max_length=255)
    def __str__(self):
        return f'{self.name}'



class Movie(models.Model):
    genre = models.ForeignKey(
    Genre,
    on_delete=models.CASCADE,
    related_name="movies",
    null=True,
    blank=True,
)
    title = models.CharField(max_length=255)
    description = models.TextField()
    filmed_at = models.DateField()

    def __str__(self):
        return f'{self.title} - {self.filmed_at}'


class Review(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="reviews")
    rating = models.IntegerField()
    comment = models.TextField()

    def __str__(self):
        return f'{self.movie.title} - {self.rating}'

