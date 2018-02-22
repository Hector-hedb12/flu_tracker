from django.shortcuts import render
from django.views.generic.edit import FormView

from .forms import PolygonForm, TrackerForm, SAMPLE_COLLECTION


class TrackerView(FormView):
    form_class = PolygonForm
    template_name = 'world/tracker.html'
    results_template_name = 'world/results.html'
    success_url = '/results/'

    def form_valid(self, form):
        result_form = TrackerForm(data={'collection': SAMPLE_COLLECTION})
        return render(self.request, self.results_template_name, {'form': result_form})
