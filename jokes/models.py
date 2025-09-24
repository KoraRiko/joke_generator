from django.db import models

class Joke(models.Model):
    keyword = models.CharField(max_length=100)  # The user's input keyword
    text = models.TextField()  # The generated joke
    type = models.CharField(max_length=50, default='none')
    timestamp = models.DateTimeField(auto_now_add=True)  # When the joke was created
    
    def __str__(self):
        return f"Joke about {self.keyword}"

class Quote(models.Model):
    text = models.CharField(max_length=255)
    keyword = models.CharField(max_length=50)
    type = models.CharField(max_length=50, default='none')
    timestamp = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return f"Quote about {self.keyword}"

