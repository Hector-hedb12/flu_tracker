from django.contrib.gis.db import models

from model_utils.models import TimeStampedModel


class Tweet(TimeStampedModel, models.Model):
    ref = models.CharField(max_length=15)
    location = models.PointField()

    def __str__(self):
        return '{}:{}'.format(self.ref, self.location)
