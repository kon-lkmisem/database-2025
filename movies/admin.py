from django.contrib import admin
from .models import Movie, Genre, Company, Director, Casting

admin.site.register(Movie)
admin.site.register(Genre)
admin.site.register(Company)
admin.site.register(Director)
admin.site.register(Casting)
