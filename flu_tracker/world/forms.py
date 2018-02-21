from django.contrib.gis import forms


class PolygonForm(forms.Form):
    poly = forms.PolygonField(
        widget=forms.OSMWidget(attrs={
            'map_width': 800,
            'map_height': 500
        })
    )
