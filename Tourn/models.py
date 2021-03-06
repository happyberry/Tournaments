from django.db import models
from django.conf import settings
from .validators import validate_file_extension


# Create your models here.


class Tournament(models.Model):
    name = models.CharField(max_length=50)
    discipline = models.CharField(max_length=50)
    start_date = models.DateTimeField()
    registration_deadline = models.DateTimeField()
    participants_limit = models.IntegerField()
    city = models.CharField(max_length=20)
    street = models.CharField(max_length=50)
    number = models.IntegerField()
    organizer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


class Logo(models.Model):
    image_src = models.CharField(max_length=200, unique=True)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)


class Participation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    license = models.IntegerField()
    rank = models.IntegerField()

    class Meta:
        unique_together = ('tournament', 'license', 'rank')


class Game(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, related_name="user1", blank=True, null=True)
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, related_name="user2", blank=True, null=True)
    score1 = models.IntegerField(blank=True, null=True)
    score2 = models.IntegerField(blank=True, null=True)
    score = models.IntegerField(blank=True, null=True)
    date = models.DateField()
    matchno = models.IntegerField()

    class Meta:
        unique_together = ('tournament', 'matchno')
