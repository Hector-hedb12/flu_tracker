from django.contrib.gis import admin
from .models import WorldBorder, ZipCode

admin.site.register(WorldBorder, admin.OSMGeoAdmin)
admin.site.register(ZipCode, admin.OSMGeoAdmin)
