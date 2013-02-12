from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from expert.models import Expert
from expert.forms import RegistrationForm, LoginForm
from django.contrib.auth import authenticate, login, logout
import os
def ExpertRegistration(request):
        if request.user.is_authenticated():
                return HttpResponseRedirect('/profile/')
        if request.method == 'POST':
		form = RegistrationForm(request.POST)
		if form.is_valid():
                        username = form.cleaned_data['username']
                        password = form.cleaned_data['password']
                        user = User.objects.create_user(username=username, email=form.cleaned_data['username'], password=password)
			user.first_name = form.cleaned_data['first_name']
			user.last_name  = form.cleaned_data['last_name']
                        user.save()
                        expert = Expert(user=user)
                        expert.save()
			context = {'expert': expert}
			expert.desktopname = form.cleaned_data['username'].replace("@","_")
			os.system('/home/khalighi/abaqual/abq_dev/NXscripts/NXadduser ' + expert.desktopname + ' ' + form.cleaned_data['password'])
			return render_to_response('profile.html', context, context_instance=RequestContext(request))
                        #return HttpResponseRedirect('/profile/')
                else:
                        return render_to_response('register.html', {'form': form}, context_instance=RequestContext(request))
		
        else:
                ''' user is not submitting the form, show them a blank registration form '''
                form = RegistrationForm()
                context = {'form': form}
                return render_to_response('register.html', context, context_instance=RequestContext(request))
	
	
@login_required
def Profile(request):
        if not request.user.is_authenticated():
                return HrttpResponseRedirect('/login/')
        expert = request.user.get_profile
        context = {'expert': expert}
        return render_to_response('profile.html', context, context_instance=RequestContext(request))

def LoginRequest(request):
        if request.user.is_authenticated():
                return HttpResponseRedirect('/profile/')
        if request.method == 'POST':
                form = LoginForm(request.POST)
                if form.is_valid():
                        username = form.cleaned_data['username']
                        password = form.cleaned_data['password']
                        expert = authenticate(username=username, password=password)
                        if expert is not None:
                                login(request, expert)
                                return HttpResponseRedirect('/profile/')
                        else:
                                return render_to_response('login.html', {'form': form}, context_instance=RequestContext(request))
                else:
                        return render_to_response('login.html', {'form': form}, context_instance=RequestContext(request))
        else:
                ''' user is not submitting the form, show the login form '''
                form = LoginForm()
                context = {'form': form}
                return render_to_response('login.html', context, context_instance=RequestContext(request))

def LogoutRequest(request):
        logout(request)
        return HttpResponseRedirect('/')
