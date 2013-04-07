from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Series(models.Model):
    live = models.BooleanField(default=False)
    series_id = models.CharField(max_length=200)


class Session(models.Model):
    series = models.ForeignKey(Series)
    create_time = models.DateTimeField('date published')
    stats_on = models.CharField(max_length=200)
    user = models.ForeignKey(User)
    cur_num = models.IntegerField(default=0)
    max_num = models.IntegerField(default=0)

    def __unicode__(self):
        return self.series.series_id


class Stats(models.Model):
    session = models.ForeignKey(Session)
    name = models.CharField(max_length=200)
    live = models.BooleanField(default=True)


class Stat(models.Model):
    change = models.IntegerField()
    old_value = models.IntegerField()
    timestamp = models.DateTimeField(default=timezone.now)
    stats = models.ForeignKey(Stats)


class Question(models.Model):
    session = models.ForeignKey(Session)
    question = models.CharField(max_length=500)
    time_asked = models.DateTimeField()
