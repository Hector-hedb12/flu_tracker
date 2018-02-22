from django.contrib.gis.geos import GEOSGeometry
from django.shortcuts import render
from django.views.generic.edit import FormView


from .forms import PolygonForm, TrackerForm


class TrackerView(FormView):
    form_class = PolygonForm
    template_name = 'world/tracker.html'
    results_template_name = 'world/results.html'
    success_url = '/results/'

    def form_valid(self, form):
        polygon = form.cleaned_data.get('poly')
        collection = GEOSGeometry(
            'GEOMETRYCOLLECTION({})'.format(polygon.wkt),
            srid=polygon.srid
        )

        result_form = TrackerForm(data={'collection': collection})
        return render(self.request, self.results_template_name, {'form': result_form})
