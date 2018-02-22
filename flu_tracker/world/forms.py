from django.contrib.gis import forms
from django.contrib.gis.geos import GEOSGeometry


SAMPLE_COLLECTION = GEOSGeometry("SRID=4326;GEOMETRYCOLLECTION("
                                 "POINT(5.625 -0.263671875),"
                                 "POINT(6.767578125 -3.603515625),"
                                 "POINT(8.525390625 0.087890625),"
                                 "POINT(8.0859375 -2.13134765625),"
                                 "LINESTRING("
                                 "6.273193359375 -1.175537109375,"
                                 "5.77880859375 -1.812744140625,"
                                 "7.27294921875 -2.230224609375,"
                                 "7.657470703125 -1.25244140625))")


class PolygonForm(forms.Form):
    poly = forms.PolygonField(
        widget=forms.OSMWidget(attrs={
            'map_width': 800,
            'map_height': 500
        })
    )


class TrackerForm(forms.Form):
    collection = forms.GeometryCollectionField(
        widget=forms.OSMWidget(attrs={
            'map_width': 800,
            'map_height': 500,
            'disabled': True
        })
    )
