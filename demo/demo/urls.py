from django.conf.urls import patterns, include, url
# for direct use of template
from django.views.generic.simple import direct_to_template
# for admin tools
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'demo.views.home', name='home'),
    # url(r'^demo/', include('demo.foo.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$',direct_to_template,{'template': 'home.html'}),

)
