from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout
from abq.forms import LoginForm, RegistrationForm
from abq.models import AbqUser
from django.contrib.auth.models import User
import datetime, random, sha
from django.core.mail import send_mail
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from misc import login_user_no_credentials
from django import forms

def UserRegistration(request):
    # if the user is already authenticated, redirect them to his/her profile
    if request.user.is_authenticated():
        return HttpResponseRedirect('/profile/')
    # if user is registering
    if request.method == 'POST':
        # get the form they just posted
        form =RegistrationForm(request.POST)
        # if the form is valid
        if form.is_valid():
            # get their username and password
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            # create the user
            user = User.objects.create_user(username=username,password=password)
            # set first name, last name and email address
            user.email      = username;
            user.first_name = form.cleaned_data['firstname']
            user.last_name  = form.cleaned_data['lastname']
            # set the user as inactive and wait for confirmation
            user.is_active  = False
            # save the user into data-base
            user.save()
            # now create an abaqual user
            abqUser = AbqUser(user=user,abaqual_status='PR')
            # set the activation key and expiration date
            salt                   = sha.new(str(random.random())).hexdigest()[:5]
            abqUser.activation_key = sha.new(salt+username).hexdigest()
            abqUser.key_expires_on = timezone.now() + datetime.timedelta(hours=48)
            # save abaqual user into database
            abqUser.save()
            # email the user activation link
            email_subject = 'Your new Abaqual account confirmation'
            email_body = 'Hello %s, and thanks for signing up for an Abaqual account!\n\n ' \
                           'To activate your account, click this link within 48 hours:\n\n' \
                           'http://127.0.0.1:8000/confirm/%s' \
                           %(abqUser.user.first_name,abqUser.activation_key)
            send_mail(email_subject,email_body,'abaqualinc@gmail.com',[abqUser.user.email])
            # and redirect them to thank you page
            return HttpResponseRedirect('/thankyou/')
        # if the form is not valid show then the form again
        else:
            return render_to_response('register.html', {'form':form}, 
                                      context_instance=RequestContext(request))
    # otherwise show the user an empty form
    else:
        form = RegistrationForm()
        return render_to_response('register.html', {'form':form}, 
                                  context_instance=RequestContext(request))



def Confirmation(request,activation_key):
    
    # if user is already authenticated, then they cannot confirm a new account
    if request.user.is_authenticated():
        return render_to_response('confirmation.html',{'has_account': True},
                                  context_instance=RequestContext(request))
    # if not then try to get the abaqual user based on the activation key
    try:
        abqUser = AbqUser.objects.get(activation_key=activation_key)
    # if user does not exists
    except ObjectDoesNotExist:
        return render_to_response('confirmation.html',{'no_account': True},
                                  context_instance=RequestContext(request))
    # otherwise check the time 
    else:
        # check if user is already activated, then tell them that their account is already active
        if ( abqUser.user.is_active ):
            return render_to_response('confirmation.html',{'active': True},
                                      context_instance=RequestContext(request))
        # if the key has expired, delete the user and redirect them to expiration
        if abqUser.key_expires_on < timezone.now():
            abqUser.user.delete()
            abqUser.delete()
            return render_to_response('confirmation.html',{'expired': True},
                                      context_instance=RequestContext(request))
        # otherwise activate user
        abqUser.user.is_active = True
        # save in the data base
        abqUser.user.save();
        # lon in the user and redirect them to their profile
        login_user_no_credentials(request,abqUser.user)
        return HttpResponseRedirect('/profile/')
        


def LoginRequest(request):
    
    # if the user is already authenticated redirect them to profile
    if request.user.is_authenticated():
        return HttpResponseRedirect('/profile/')    
    # if the user is posting  
    if request.method == 'POST':
        form = LoginForm(request.POST)
        # check form is valid
        if form.is_valid():
            # get username and password
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            # authenticate user
            user = authenticate(username=username, password=password)
            # check if the user is autheticated
            if user is not None:
                # log the user in
                login(request,user)
                # and redirect the user to his/her profile
                return HttpResponseRedirect('/profile/')
            # otherwise show them the form again
            else:
                return render_to_response('home.html', {'form': form}, 
                                          context_instance=RequestContext(request))
        # if the form is not valid, show th blank form again
        else:
            return render_to_response('home.html', {'form': form}, 
                                      context_instance=RequestContext(request))
    # otherwise show them a blank form
    else:
        form = LoginForm()
        return render_to_response('home.html', {'form': form}, 
                                  context_instance=RequestContext(request))



def LogoutRequest(request):
    # log out user
    logout(request)
    # and redirect them to home
    return HttpResponseRedirect('/home')
