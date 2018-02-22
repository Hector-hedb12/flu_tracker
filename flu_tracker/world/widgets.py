from django.contrib.gis.forms import OSMWidget


class ReadonlyOSMWidget(OSMWidget):
    template_name = 'gis/openlayers-readonly-osm.html'
    disabled = True

    def __init__(self, attrs=None):
        super().__init__()
        for key in ('default_lon', 'default_lat', 'default_zoom', 'disabled'):
            self.attrs[key] = getattr(self, key)
        if attrs:
            self.attrs.update(attrs)
