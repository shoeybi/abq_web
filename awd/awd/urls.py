from django.conf.urls import patterns, include, url
# for direct use of template
from django.views.generic import TemplateView
# for media root and url
from django.conf import settings
from django.conf.urls.static import static
# enable admin
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns(

    # no generic view pattern
    '',
    
    # admin
    url(r'^admin/', include(admin.site.urls)),

    # home
    url(r'^home/$','abq.views.LoginRequest'),
    url(r'^$','abq.views.LoginRequest'),

    # logout
    url(r'^logout/$','abq.views.LogoutRequest'),

    # registration
    url(r'^registration/$','abq.views.UserRegistration'),

    # registration confirmation
    url(r'^registration-confirmation/(?P<activation_key>\w+)/$',
        'abq.views.RegistrationConfirmation'),

    # console
    url(r'^console/$','abq.views.console'),

    # desktop
    url(r'^desktop/$','abq.views.Desktop'),

    # employment confirmation
    url(r'^employment-confirmation/(?P<activation_key>\w+)/$',
        'abq.views.EmploymentConfirmation'),

    # contact us
    url(r'^contactus/$','abq.views.ContactUs'),

    # tools
    url(r'^tools/$','abq.views.Tools'),

    # order tools
    url(r'^ordertools/$','abq.views.OrderTools'),
    


    # base
    url(r'^base/$',TemplateView.as_view(template_name="base.html")),

    # test
    url(r'^test/$',TemplateView.as_view(template_name="mytests.html")),


    # Examples:
    # url(r'^$', 'awd.views.home', name='home'),
    # url(r'^awd/', include('awd.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
