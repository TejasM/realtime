from django.views.generic import ListView, DetailView

__author__ = 'tejas'

from django.conf.urls import patterns, url

from rtr import views

urlpatterns = patterns('',
                       url(r'^$', views.index, name='index'),
                       url(r'login/$', views.loginUser, name='login'),
                       url(r'profsettings/$', views.prof_settings, name='prof_settings'),
                       url(r'profsettings/start/$', views.prof_start_display, name='prof_start_display'),
                       url(r'profDisplay/$', views.prof_display, name='prof_display'),
                       url(r'profDisplay/statisticsGet/$', views.get_stats, name='get_stats'),
                       url(r'profDisplay/count/$', views.get_count, name='get_count'),
                       url(r'profDisplay/questions/$', views.get_questions, name='get_questions'),
                       url(r'profDisplay/all/$', views.get_all, name='get_all'),
                       url(r'audience_view/$', views.audience_display, name='audience_display'),
                       url(r'audience_view/audienceResponse/$', views.updateStats, name='audience_response'),
                       url(r'audience_view/audienceQuestion/$', views.ask_question, name='audience_question'),
                       url(r'endsession/$', views.end_session, name='end_session'),
                       url(r'audience_view/leavesession/$', views.end_session, name='leave_session'),
                       url(r'viewSeries/(?P<series_id>\d+)/$', views.view_series, name='view_series'),
                       url(r'viewSession/(?P<session_id>\d+)/(?P<location>\w+)$', views.view_session, name='view_session'),
)

