from django.db import models

class Joke(models.Model):
    keyword = models.CharField(max_length=100)  # The user's input keyword
    joke = models.TextField()  # The generated joke
    timestamp = models.DateTimeField(auto_now_add=True)  # When the joke was created

    def __str__(self):
        return f"Joke about {self.keyword}"
