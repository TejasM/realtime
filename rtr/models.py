import json
import urllib
import urllib2
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from mysite import settings


def send_event(event_type, event_data):
    to_send = {
        'event': event_type,
        'data': event_data
    }
    urllib2.urlopen(settings.ASYNC_BACKEND_URL, urllib.urlencode(to_send))


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
    votes = models.IntegerField(default=0)

    def __unicode__(self):
        return self.question

    def as_dict(self):
        data = {
            'id': self.pk,
            'question': self.question,
        }
        return json.dumps(data)

    def save(self, *args, **kwargs):
        super(Question, self).save(*args, **kwargs)
        send_event('message-create-' + str(self.session.id), self.as_dict())


class Poll(models.Model):
    question = models.CharField(max_length=200)
    session = models.ForeignKey(Session)
    live = models.BooleanField(default=True)

    def __unicode__(self):
        return self.question


class Choice(models.Model):
    poll = models.ForeignKey(Poll)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
    correct_choice = models.BooleanField(default=False)

    def __unicode__(self):
        return self.choice_text