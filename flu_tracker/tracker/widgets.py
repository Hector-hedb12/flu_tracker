from django.contrib.gis.forms import OSMWidget


class ReadonlyOSMWidget(OSMWidget):
    template_name = 'widgets/openlayers-readonly-osm.html'
    disabled = True
    map_srid = 4326  # before: 3857

    def __init__(self, attrs=None):
        super().__init__()
        for key in ('default_lon', 'default_lat', 'default_zoom', 'disabled'):
            self.attrs[key] = getattr(self, key)
        if attrs:
            self.attrs.update(attrs)
