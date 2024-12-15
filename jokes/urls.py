from django.urls import path

from . import views

urlpatterns = [
    path('anecdotes/', views.joke_generator, name='joke_generator'),
]
