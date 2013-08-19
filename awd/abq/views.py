
from django.http                  import HttpResponseRedirect
from django.shortcuts             import render_to_response
from django.template              import RequestContext
from django.contrib.auth          import authenticate, login, logout
from django.contrib.auth.models   import User
from django.core.mail             import send_mail
from django.core.exceptions       import ObjectDoesNotExist
from django.utils                 import timezone
from django.conf                  import settings
from django.core.files            import File
from abq.misc                     import login_user_no_credentials, get_aws_region
from abq.forms                    import LoginForm, RegistrationForm, \
    CompanyForm, WorkspaceLaunchForm, EmploymentForm
from abq.models                   import AbqUser, Company, OS, Hardware, Employment, Workspace
import datetime, random, hashlib

if settings.AWS:
    from interface import get_instance_id, instance_status, get_public_dns, get_url


# get the compnay lists that the current user is the owner
def build_company_dic_for_employee(user):
    abqUser = AbqUser.objects.get(user=user)
    # get all the compnaies that user has
    companies = Company.objects.filter(employee=abqUser)
    # build a dictionary of compnay-name:value pairs
    company_dict = {}
    for company in companies:
        workspaces = Workspace.objects.filter(company=company)
        employees  = AbqUser.objects.filter(
            employment__company=company,
            employment__end_date=None).exclude(
            employment__start_date=None).exclude(user=abqUser.user)
        dic = {'company':company, 
               'workspaces':workspaces,
               'employees':employees,
               'owner':company.owner}
        company_dict[company.name] = dic
    # and return the dictionary
    return company_dict
    

# get the compnay lists that the current user is an employee
def build_company_dic_for_owner(user):
    abqUser = AbqUser.objects.get(user=user)
    # get all the compnaies that user is part an employee in
    companies = Company.objects.filter(owner=abqUser)
    # build a dictionary of compnay-name:value pairs
    company_dic = {}
    for company in companies:
        workspace_launch_form = WorkspaceLaunchForm(initial={'company_name': company.name})
        employment_form       = EmploymentForm(user,initial={'company_name': company.name})
        workspaces            = Workspace.objects.filter(company=company)

        # ---------------------------
        # HACK
        if settings.AWS:
            for workspace in workspaces:
                print workspace
                print ' >', workspace.instance_id
                print ' >', workspace.region
                print ' >', instance_status(workspace.instance_id,workspace.region)
                print ' >', get_url(workspace.instance_id,workspace.region)
        # ---------------------------

        employees_accepted    = AbqUser.objects.filter(employment__company=company).exclude(
            employment__start_date=None)
        employees_pending     = AbqUser.objects.filter(employment__company=company,
                                                        employment__start_date=None)
        dic = {'company':company, 
               'workspace_launch_form':workspace_launch_form, 
               'employment_form':employment_form,
               'workspaces':workspaces,
               'employees_accepted':employees_accepted,
               'employees_pending':employees_pending}
        company_dic[company.name] = dic
    # and return the dictionary
    return company_dic


def Profile(request):
    # if the user is not authenticated, then redirect them 
    # to the home page where they can lon in
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/home/')

    # an employee does not have much functionality
    company_dic_employee = build_company_dic_for_employee(request.user)


    # =====================
    # initialize empty form
    # =====================


    # there is just one single posting for launching a company
    company_form = CompanyForm()

    # however, the other forms are per registered company so put them
    # in a dictionary with company name as the keyword. Note that company 
    # name is unique so there is no conflict
    company_dic = build_company_dic_for_owner(request.user)

    # if user is posting
    if request.method == 'POST':

        # ====================
        # company registration
        # ====================

        # if the user is launching a new company
        if 'company_reg' in request.POST:
            # get the company registration from
            company_form = CompanyForm(request.POST)
            if company_form.is_valid():
                # get the compnay name
                name = company_form.cleaned_data['name']
                # create a new company
                abqUser = AbqUser.objects.get(user=request.user)
                company = Company(name=name,owner=abqUser)
                company.launch_date = timezone.now()
                # and add it to the database
                company.save()
                # the form has been successfully submitted so we should show a clean form
                company_form = CompanyForm()
                # otherwise there was an error and we should show just show the old form with errors
                # if we are registering a new company, we should rebuild the company_dic
                company_dic = build_company_dic_for_owner(request.user)
                

        # ===================================
        # invite a person to join the company
        # ===================================
        
        # if the user is inviting a person
        if 'invite_employee' in request.POST:
            # get the employment form
            employment_form = EmploymentForm(request.user,request.POST)
            if employment_form.is_valid():
                abqUser      = employment_form.cleaned_data['abqUser']
                company_name = employment_form.cleaned_data['company_name']
                company      = company_dic[company_name]['company']
                employment   = Employment(employee=abqUser, company=company)
                # set the activation key and expiration date
                salt                      = hashlib.sha1(str(random.random())).hexdigest()[:5]
                employment.activation_key = hashlib.sha1(salt+abqUser.user.username).hexdigest()
                employment.key_expiration = timezone.now() + datetime.timedelta(days=7)
                employment.save()
                # email the employee activation link
                email_subject = 'Your new Abaqual employment confirmation'
                email_body = 'Hello %s,\n\n ' \
                    '%s has sent you an employment request. To accept your offer, click this link within 7 days:\n\n' \
                    'http://127.0.0.1:8000/confirm-employment/%s' \
                    %(employment.employee.user.first_name,employment.company.name,employment.activation_key)
                send_mail(email_subject,email_body,settings.EMAIL_HOST_USER,[abqUser.user.email])
                # and show a new form
                employment_form = EmploymentForm(request.user,initial={'company_name': company.name})
            else:
                company_name = employment_form.cleaned_data['company_name']
            # now we need to replace the form we had in the dictionary
            company_dic[company_name]['employment_form'] = employment_form


        # ================
        # workspace launch
        # ================

        # workspace is a little bit more complicated
        # if user is launching a new workspace
        if 'workspace_launch' in request.POST:
            # get the form from request.POS
            workspace_launch_form = WorkspaceLaunchForm(request.POST)
            company_name          = request.POST['company_name']
            company               = company_dic[company_name]['company']
           
            # if the value is not the default
            if request.POST['hardware'] != '':
                # get the hardware
                hardware = Hardware.objects.get(pk=request.POST['hardware'])
                # hardware should defintely exist
                if hardware == None:
                    raise LookupError('hardware deoes not exist')
                # add the relevant oss
                workspace_launch_form.fields['os'].queryset = OS.objects.filter(hardware=hardware)
                # check if it is valid
                if workspace_launch_form.is_valid() and workspace_launch_form.check_os():
                    # add the workspace
                    workspace = Workspace()
                    # count the number of workspaces that this company has
                    workspaces = Workspace.objects.filter(company=company)
                    workspace.name        = 'workspace '+str(len(workspaces)+1)
                    workspace.company     = company
                    workspace.hardware    = hardware
                    workspace.os          = workspace_launch_form.cleaned_data['os']
                    # if the aws integration flag is on, launch an instance 
                    # and prepare it
                    if settings.AWS:
                        #print 'aws is on:'
                        workspace.region  = get_aws_region()
                        #print ' region:', workspace.region
                        owner_username = (request.user.first_name[0]+request.user.last_name).lower()
                        #print ' username:', owner_username
                        workspace.instance_id = get_instance_id(region=workspace.region, 
                                                                instance_type=hardware.key, 
                                                                os=workspace.os.key, 
                                                                company_name=company.name, 
                                                                uname=owner_username, 
                                                                pswd='123')
                        #print ' instance id:', workspace.instance_id
                        #print ' DONE!!!'                    
                    # otherwise just put something there
                    else:
                        workspace.region      = 'west'
                        workspace.instance_id = 'a2456d'
                    # set the launch date and time                        
                    workspace.launch_date = timezone.now()
                    # background image
                    # XXX
                    image_filename  = 'workspaceImage__'+company.name+'__'+workspace.name+'.png'
                    # for now read from a default file
                    source_filename = settings.MEDIA_ROOT+'workspace_images/desktop_background_default.png'
                    workspace.set_size_and_save_image(image_filename,source_filename)   
                    workspace.save()
                    # create an empty from
                    workspace_launch_form = WorkspaceLaunchForm(
                        initial={'company_name': company.name})
            # now we need to replace the form we had in the dictionary
            company_dic[company_name]['workspace_launch_form'] = workspace_launch_form

        # if the user is not posting a workspace launch
        else:
            if 'hardware' in request.POST:
                company_name = request.POST['company_name']
                company      = company_dic[company_name]['company']
                # get the form from request.POS
                workspace_launch_form = WorkspaceLaunchForm(request.POST)
                # if the value is not the default
                if request.POST['hardware'] != '':
                    # get the hardware
                    hardware = Hardware.objects.filter(pk=request.POST['hardware'])
                    # hardware should defintely exist
                    if hardware == None:
                        raise LookupError('hardware deoes not exist')
                    # and fill in the workspace
                    workspace_launch_form.fields['os'].queryset = OS.objects.filter(hardware=hardware)
                # now we need to replace the form we had in the dictionary
                company_dic[company_name]['workspace_launch_form'] = workspace_launch_form

    abqUser = AbqUser.objects.get(user=request.user)
    context = {'abqUser': abqUser,
               'company_dic':company_dic,
               'company_form':company_form,
               'company_dic_employee':company_dic_employee}
    return render_to_response('profile.html', context,
                          context_instance=RequestContext(request))


def EmploymentConfirmation(request,activation_key):
    
    # get the employment letter
    try:
        employment = Employment.objects.get(activation_key=activation_key)
    # if user does not exists
    except ObjectDoesNotExist:
        return render_to_response('employment_confirmation.html',{'no_account': True},
                                  context_instance=RequestContext(request))
    # otherwise check the time 
    else:
        # if user has not already activated their account
        if employment.start_date is None:
            # if the key has expired, delete the employment and redirect them to expiration
            if employment.key_expiration < timezone.now():
                employment.delete()
                return render_to_response('employment_confirmation.html',{'expired': True},
                                          context_instance=RequestContext(request))
            # otherwise start employment
            employment.start_date = timezone.now()
            # save in the data base
            employment.save()
        # log in the user and redirect them to their profile
        if request.user != employment.employee.user: 
            # if employee is logged in as a different user,log him/her out
            if request.user.is_authenticated():
                logout(request)
            login_user_no_credentials(request,employment.employee.user)
        # redirect employee to his/her profile
        return HttpResponseRedirect('/profile/')


    
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
