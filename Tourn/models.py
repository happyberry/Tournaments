from django.db import models
from django.conf import settings


# Create your models here.


class Tournament(models.Model):
    name = models.CharField(max_length=50)
    discipline = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    registration_deadline = models.DateField()
    participants_limit = models.IntegerField()
    city = models.CharField(max_length=20)
    street = models.CharField(max_length=50)
    number = models.IntegerField()
    organizer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


class Logo(models.Model):
    image = models.ImageField(upload_to='logo')
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)


class Participation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    license = models.IntegerField()
    rank = models.IntegerField()


class Game(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, related_name="user1")
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, related_name="user2")
    score1 = models.IntegerField(blank=True)
    score2 = models.IntegerField(blank=True)
    score = models.IntegerField(blank=True)
