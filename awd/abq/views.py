from django.http                  import HttpResponseRedirect
from django.shortcuts             import render_to_response
from django.template              import RequestContext
from django.contrib.auth          import authenticate, login, logout
from django.contrib.auth.models   import User
from django.core.mail             import send_mail
from django.core.exceptions       import ObjectDoesNotExist
from django.utils                 import timezone
from django.conf                  import settings
from abq.misc                     import login_user_no_credentials
from abq.forms                    import LoginForm, RegistrationForm, \
    CompanyForm, WorkspaceLaunchForm
from abq.models                   import AbqUser, Company, OS, Hardware
import datetime, random, hashlib


def Profile(request):
    # if the user is not authenticated, then redirect them to the home page where they can lon in
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/home/')

    # initialize empty forms is case user is not posting
    form_company          = CompanyForm()
    form_workspace_launch = WorkspaceLaunchForm()
    
    # if user is posting
    if request.method == 'POST':


        # ====================
        # company registration
        # ====================

        # if the user is launching a new company
        if 'company_reg' in request.POST:
            # get the company registration from
            form_company = CompanyForm(request.POST)
            if form_company.is_valid():
                # get the compnay name
                name = form_company.cleaned_data['name']
                # create a new company
                abqUser = AbqUser.objects.get(user=request.user)
                company = Company(name=name,owner=abqUser)
                company.launch_date = timezone.now()
                # and add it to the database
                company.save()
                # the form has been successfully submitted so we should show a clean form
                form_company = CompanyForm()
                # otherwise there was an error and we should show just show the old form with errors
    


        # ================
        # workspace launch
        # ================

        # workspace is a little bit more complicated
        # if user is launching a new workspace
        if 'workspace_launch' in request.POST:
            # get the form from request.POS
            form_workspace_launch = WorkspaceLaunchForm(request.POST)
            # if the value is not the default
            if request.POST['hardware'] != '':
                # get the hardware
                hardware = Hardware.objects.filter(pk=request.POST['hardware'])
                # hardware should exist
                if hardware != None:
                    form_workspace_launch.fields['os'].queryset = OS.objects.filter(hardware=hardware)
                    # check if it is valid
                    if form_workspace_launch.is_valid():
                        # add the workspace
                        # XXXXXXXXXXXXXXXXXXXXX
                        print 'workspace form is valid'
                        # XXXXXXXXXXXXXXXXXXXXX
                        # create an empty from
                        form_workspace_launch = WorkspaceLaunchForm()
        # if the user is not posting a workspace launch
        else:
            if 'hardware' in request.POST:
                # get the form from request.POS
                form_workspace_launch = WorkspaceLaunchForm(request.POST)
                # if the value is not the default
                if request.POST['hardware'] != '':
                    # fill in the os field
                    hardware = Hardware.objects.filter(pk=request.POST['hardware'])
                    if hardware != None:
                        form_workspace_launch.fields['os'].queryset = OS.objects.filter(hardware=hardware)
            
        
    
    # create a new company
    abqUser = AbqUser.objects.get(user=request.user)
    # get all the compnaies that user has
    companies = Company.objects.filter(owner=abqUser)
    context = {'form_company':form_company, 'companies':companies,'form_workspace_launch':form_workspace_launch} 
    return render_to_response('profile.html', context,
                          context_instance=RequestContext(request))

    
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
            salt                   = hashlib.sha1(str(random.random())).hexdigest()[:5]
            abqUser.activation_key = hashlib.sha1(salt+username).hexdigest()
            abqUser.key_expiration = timezone.now() + datetime.timedelta(hours=48)
            # save abaqual user into database
            abqUser.save()
            # email the user activation link
            email_subject = 'Your new Abaqual account confirmation'
            email_body = 'Hello %s, and thanks for signing up for an Abaqual account!\n\n ' \
                           'To activate your account, click this link within 48 hours:\n\n' \
                           'http://127.0.0.1:8000/confirm/%s' \
                           %(abqUser.user.first_name,abqUser.activation_key)
            send_mail(email_subject,email_body,settings.EMAIL_HOST_USER,[abqUser.user.email])
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
        return render_to_response('confirmation.html',
                                  {'has_account': True, 'username': request.user.username},
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
        # check if user is already activated, then jutr redirect them to their profile
        if ( abqUser.user.is_active ):
            # log in the user and redirect them to their profile
            login_user_no_credentials(request,abqUser.user)
            return HttpResponseRedirect('/profile/')
        # if the key has expired, delete the user and redirect them to expiration
        if abqUser.key_expiration < timezone.now():
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
