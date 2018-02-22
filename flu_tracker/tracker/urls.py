from django.conf.urls import url

from . import views

app_name = 'tracker'
urlpatterns = [
    url(
        regex=r'^$',
        view=views.TrackerView.as_view(),
        name='list'
    ),
]
