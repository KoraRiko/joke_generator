from django.db import models

class Joke(models.Model):
    keyword = models.CharField(max_length=100)  # The user's input keyword
    text = models.TextField()  # The generated joke
    rating = models.IntegerField(null=True, blank=True)  # User rating from 1-10
    timestamp = models.DateTimeField(auto_now_add=True)  # When the joke was created
    
    def __str__(self):
        return f"Joke about {self.keyword}"

