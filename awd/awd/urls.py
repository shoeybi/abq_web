from django.conf.urls import patterns, include, url
# for direct use of template
from django.views.generic import TemplateView
# enable admin
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns(
    # no generic view pattern
    '',
    # admin
    url(r'^admin/', include(admin.site.urls)),

    # base
    url(r'^base/$',TemplateView.as_view(template_name="base.html")),

    # prifile
    #url(r'^profile/$',TemplateView.as_view(template_name="profile.html")),
    url(r'^profile/$','abq.views.Profile'),

    # registration
    url(r'^register/$','abq.views.UserRegistration'),
    # and followup thank you
    url(r'^thankyou/$',TemplateView.as_view(template_name="registerThankyou.html")),
    # confirmation
    url(r'^confirm/(?P<activation_key>\w+)/$','abq.views.Confirmation'),

    # home
    url(r'^home/$','abq.views.LoginRequest'),

    # logout
    url(r'^logout/$','abq.views.LogoutRequest'),

    # Examples:
    # url(r'^$', 'awd.views.home', name='home'),
    # url(r'^awd/', include('awd.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),


)
