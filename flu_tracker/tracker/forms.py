from django.contrib.gis import forms

from .widgets import ReadonlyOSMWidget

DEFAULT_LAT = 45.4215
DEFAULT_LON = -75.6972
DEFAULT_ZOOM = 8


class PolygonForm(forms.Form):
    poly = forms.PolygonField(
        widget=forms.OSMWidget(attrs={
            'map_width': 800,
            'map_height': 500,
            'map_srid': 4326,
            'default_lat': DEFAULT_LAT,
            'default_lon': DEFAULT_LON,
            'default_zoom': DEFAULT_ZOOM,
        })
    )


class TrackerForm(forms.Form):
    collection = forms.GeometryCollectionField(
        widget=ReadonlyOSMWidget(attrs={
            'map_width': 800,
            'map_height': 500,
            'map_srid': 4326,
        })
    )
