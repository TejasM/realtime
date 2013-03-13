import datetime
from django.db import models
from django.utils import timezone


class Session(models.Model):
    def __init__(self, sessionId):
        self.sessionId = sessionId
