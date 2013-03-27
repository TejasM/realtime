from django.conf.urls import patterns, include, url, handler500

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
import rtr

admin.autodiscover()

handler500 = rtr.views.error

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mysite.views.home', name='home'),
    url(r'^rtr/', include('rtr.urls', namespace="rtr")),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

)
