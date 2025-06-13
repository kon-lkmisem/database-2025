from django.db import models

class Movie(models.Model):
    mid = models.AutoField(primary_key=True)  # 추가
    movie_name = models.CharField(max_length=255)
    movie_engname = models.CharField(max_length=255)
    create_year = models.IntegerField()
    movie_type = models.CharField(max_length=10)
    movie_state = models.CharField(max_length=10)

    class Meta:
        managed = False
        db_table = 'movie'

class Genre(models.Model):
    mgid = models.AutoField(primary_key=True)  # 추가
    genre = models.CharField(max_length=255)
    movie = models.ForeignKey(Movie, on_delete=models.RESTRICT, db_column='mid', related_name='genres')

    class Meta:
        managed = False
        db_table = 'movie_genre'

class Company(models.Model):
    mcid = models.AutoField(primary_key=True)  # 추가
    company = models.CharField(max_length=255)
    movie = models.ForeignKey(Movie, on_delete=models.RESTRICT, db_column='mid', related_name='companies')

    class Meta:
        managed = False
        db_table = 'movie_company'

class Director(models.Model):
    did = models.AutoField(primary_key=True)  # 추가
    dname = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'director'

class Casting(models.Model):
    cid = models.AutoField(primary_key=True)  # 추가
    movie = models.ForeignKey(Movie, on_delete=models.RESTRICT, db_column='mid', related_name='castings')
    director = models.ForeignKey(Director, on_delete=models.RESTRICT, db_column='did', related_name='castings')

    class Meta:
        managed = False
        db_table = 'casting'

class MovieNation(models.Model):
    mnid = models.AutoField(primary_key=True)
    nation = models.CharField(max_length=255)
    movie = models.ForeignKey(Movie, on_delete=models.RESTRICT, db_column='mid', related_name='nations')

    class Meta:
        managed = False
        db_table = 'movie_nation'
