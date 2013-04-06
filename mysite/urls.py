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
                       url(r'^about/', views.about, name='about'),
                       url(r'^blog-post/', views.blog_post, name='blog-post'),
                       url(r'^contact/', views.contact, name='contact'),
                       url(r'^customers/', views.customers, name='customers'),
                       url(r'^features/', views.features, name='features'),
                       url(r'^pricing/', views.pricing, name='pricing'),
                       url(r'^signup/', views.signup, name='signup'),
                       url(r'^signup/signup/', views.signup_post, name='signup_post'),
                       url(r'^team/', views.team, name='team'),
                       url(r'^admin/', include(admin.site.urls)),
)
