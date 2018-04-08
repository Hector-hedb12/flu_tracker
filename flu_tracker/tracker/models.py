from django.contrib.gis.db import models

from model_utils.models import TimeStampedModel


class Tweet(TimeStampedModel, models.Model):
    ref = models.CharField(max_length=25)
    location = models.PointField()

    def __str__(self):
        return '{}:{}'.format(self.ref, self.location)


class AddressLocator(models.Model):
    address = models.CharField(max_length=255)
    location = models.PointField(null=True)  # srid=3857

    def __str__(self):
        return '{}:{}'.format(self.address, self.location)
