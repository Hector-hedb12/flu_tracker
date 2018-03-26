from django.contrib.gis.geos import GEOSGeometry
from django.shortcuts import render
from django.views.generic.edit import FormView


from .forms import PolygonForm, TrackerForm
from .utils import tweet_search


class TrackerView(FormView):
    form_class = PolygonForm
    template_name = 'tracker/tracker.html'
    results_template_name = 'tracker/results.html'
    success_url = '/results/'

    def form_valid(self, form):
        polygon = form.cleaned_data.get('poly')

        points = tweet_search(polygon)
        points_str = ', '.join(p.wkt for p in points)

        collection = GEOSGeometry(
            'GEOMETRYCOLLECTION({}, {})'.format(polygon.wkt, points_str),
            srid=polygon.srid
        )

        result_form = TrackerForm(data={'collection': collection})
        return render(self.request, self.results_template_name, {'form': result_form})
