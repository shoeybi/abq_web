from django.conf.urls import patterns, include, url
# for direct use of template
from django.views.generic.simple import direct_to_template
# for admin tools
from django.contrib import admin
admin.autodiscover()
PLUGIN_DIR =ABQ_PATH+"/demo/desktop/static"
urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'demo.views.home', name='home'),
    # url(r'^demo/', include('demo.foo.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$',direct_to_template,{'template': 'home.html'}),
    url(r'^register/$', 'expert.views.ExpertRegistration'),
    url(r'^login/$', 'expert.views.LoginRequest'),
    url(r'^logout/$', 'expert.views.LogoutRequest'),
    url(r'^profile/$', 'expert.views.Profile'),
    url(r'^plugin/(?P<path>.*)$', 'django.views.static.serve',
          {'document_root': PLUGIN_DIR}),
)
