from django.contrib.gis import forms

from .widgets import ReadonlyOSMWidget


class PolygonForm(forms.Form):
    poly = forms.PolygonField(
        widget=forms.OSMWidget(attrs={
            'map_width': 800,
            'map_height': 500
        })
    )


class TrackerForm(forms.Form):
    collection = forms.GeometryCollectionField(
        widget=ReadonlyOSMWidget(attrs={
            'map_width': 800,
            'map_height': 500
        })
    )
