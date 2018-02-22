from django.contrib.gis.db import models


class Tweet(models.Model):
    ref = models.CharField(max_length=15)
    location = models.PointField()

    def __str__(self):
        return '{}:{}'.format(self.ref, self.location)
