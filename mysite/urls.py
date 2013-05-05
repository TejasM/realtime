from django.conf.urls import patterns, include, url, handler500

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from index import views
import rtr

admin.autodiscover()

handler500 = rtr.views.error

urlpatterns = patterns('',
                       # Examples:
                       url(r'^rtr/', include('rtr.urls', namespace="rtr")),
                       url(r'^$', views.index, name='index'),
                       url(r'^admin/', include(admin.site.urls)),
)
