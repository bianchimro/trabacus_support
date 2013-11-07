from django.conf.urls import patterns, include, url
from .views import CSVProcessView

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'trabacus_support.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    
    url(r'^$', CSVProcessView.as_view(), name="csv_process"),
)
