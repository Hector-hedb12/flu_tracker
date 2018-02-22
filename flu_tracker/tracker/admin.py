from django.contrib.gis import admin
from .models import Tweet

admin.site.register(Tweet, admin.OSMGeoAdmin)
