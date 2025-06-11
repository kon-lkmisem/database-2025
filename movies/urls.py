from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.movie_search, name='movie_search'),
]