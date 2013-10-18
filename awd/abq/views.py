from django import forms
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout, decorators
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.conf import settings
from django.core.files import File
from django.forms.models import modelformset_factory, modelform_factory
from abq.misc import login_user_no_credentials, get_aws_region
from abq.forms import LoginForm, RegistrationForm, CompanyRegForm, \
    WorkspaceLaunchForm, EmploymentForm, WorkspaceTerminateForm, \
    EmploymentTerminationForm, ContactUsForm, RequestToolForm, \
    SoftwareForm
from abq.models import AbqUser, Company, OS, Hardware, Employment, \
    Workspace, Region, Software, SoftwareLaunch
import datetime, random, hashlib, threading, os
threading._DummyThread._Thread__stop = lambda x: 42

if settings.AWS:
    from interface import get_instance_id, instance_status, \
        terminate_instance, make_company, remove_company

@decorators.login_required
def NxAuth(request):

    # get the username
    username = request.user.username
    # get the user object
    user = User.objects.get(username=username)
    # from user object get the abaqual user
    abq_user = AbqUser.objects.get(user=user)
    # build the filename path based on activation key
    filename = '/static/nxauth/' + abq_user.activation_key + '.js'
    # redirect to the file
    return HttpResponseRedirect(filename)


def Tools(request):

    hardwares = Hardware.objects.all()
    oss = OS.objects.all()
    softwares = Software.objects.all()

    context = {'hardwares': hardwares, 
               'oss': oss, 
               'softwares': softwares}
    return render_to_response('seetools.html',
                              context,
                              context_instance=RequestContext(request))


def OrderTools(request):

    # if the user is posting  
    if request.method == 'POST':
        # populate the form from post
        form = RequestToolForm(request.POST)
        # if the form is valid
        if form.is_valid():
            # first email the content 
            email_address = 'shared@abaqual.com'
            email_subject = 'Abaqual order tool request'
            email_body = \
                'Product name: %s\n' \
                'Product link: %s\n' \
                'Email address: %s\n' \
                'comment: %s\n' \
                %(form.cleaned_data['name'],\
                      form.cleaned_data['link'],\
                      form.cleaned_data['email'],\
                      form.cleaned_data['comment'])
            thread = threading.Thread(target=send_mail,
                                      args=(email_subject,email_body,
                                            settings.EMAIL_HOST_USER,
                                            [email_address]))
            thread.start()
            # redirect them to a thank you page
            return render_to_response(
                'ordertool_thankyou.html',
                context_instance=RequestContext(request)) 

    else:
        # show them an empty form
        form = RequestToolForm()

    return render_to_response(
        'ordertool.html',
        {'form': form}, 
        context_instance=RequestContext(request)) 


    
def get_aws_regions():
    """ Get regions list """

    # DBG
    if settings.AWS:
        regions2 = Region.objects.all()
        regions = []
        for region in regions2:
            regions.append(region.name)
    else:
        regions = ['west']
    return regions

    
def build_workspaces_list(company):
    """ Build workspaces and their termination form for a given company """
    
    # get all the workspaces that a company has
    workspaces = Workspace.objects.filter(
        company=company).order_by('launch_date')
    workspaces_list = [] 
    # now for all those workspaces
    for workspace in workspaces:
        # DBG
        if settings.AWS:
            # if workspace does not have an assigned url, update it
            if workspace.instance_url == '#':
                output = instance_status(workspace.instance_id,
                                         workspace.region)
                if output[0] == 'ready':
                    workspace.instance_url = output[2]
                    workspace.save()
        # prepopulate termination form
        workspace_terminate_form = WorkspaceTerminateForm(
            initial={'company_name': company.name, 
                     'region': workspace.region, 
                     'instance_id': workspace.instance_id})
        # add the workspace and its termination form as a 
        # dictionary to the list
        workspaces_list.append(
            {'workspace': workspace,
             'termination_form':workspace_terminate_form } )
    # return the list
    return workspaces_list
    
    
def build_employees_list(company):
    """ Build employees and their termination form for a given company """
    
    # employees who have already accpeted employment
    employees_accepted = AbqUser.objects.filter(\
        employment__company=company, employment__end_date=None).exclude(\
        employment__start_date=None).order_by(\
        'user__last_name', 'user__first_name')
    # employees who still have not responded to their employment
    employees_pending = AbqUser.objects.filter(\
        employment__company=company, 
        employment__start_date=None).order_by(\
        'user__last_name', 'user__first_name')
    # now build the list
    employees_list = []
    # first are the ones who have accepted 
    for employee in employees_accepted:
        # initialize the termination form
        employee_termination_form = EmploymentTerminationForm(
            initial={'username': employee.user.username, 
                     'company_name': company.name} )
        # append them to the list
        employees_list.append(
            {'employee': employee, 'accepted': True, 
             'termination_form': employee_termination_form }
            )
    # first are the ones who have accepted 
    for employee in employees_pending:
        # initialize the termination form
        employee_termination_form = EmploymentTerminationForm(
            initial={'username': employee.user.username, 
                     'company_name': company.name} )
        # append them to the list
        employees_list.append(
            {'employee': employee, 'accepted': False, 
             'termination_form': employee_termination_form }
            )
    # and return the list
    return employees_list
        
    
def populate_company_dict(company):
    """ Build a dictionary for a given company's belongings  """
    
    # start a new workspace form
    workspace_launch_form = WorkspaceLaunchForm(\
        initial={'company_name': company.name})
    # invite a new employee form
    employment_form = EmploymentForm(\
        initial={'company_name': company.name})
    # workspaces that are already launched
    workspaces_list = build_workspaces_list(company)
    # employees 
    employees_list = build_employees_list(company)
    # build the dictionary
    company_dict = {
        'company': company, 
        'workspace_launch_form': workspace_launch_form, 
        'employment_form': employment_form,
        'workspaces_list': workspaces_list,
        'employees_list': employees_list
        }
    # return the dictionary
    return company_dict


def build_companies_dict(abq_user):
    """ Build a dictionary of companies with their belongins  """

    # get all the compnaies that user owns
    companies_owned = Company.objects.filter(owner=abq_user)
    # get all the compnaies that user work for
    companies_works = Company.objects.filter(employee=abq_user)
    # build a dictionary of compnay-name:value pairs
    companies_dict = {}
    # add the companies that the user owns
    for company in companies_owned:
        company_dict = populate_company_dict(company)
        companies_dict[company.name] = company_dict
    # add the companies that the user works for
    for company in companies_works:
        company_dict = populate_company_dict(company)
        companies_dict[company.name] = company_dict
    # and return the dictionary
    return companies_dict


def register_new_company(request,abq_user):
    """ Register a new company  """
    
    # get the company registration from
    company_reg_form = CompanyRegForm(request.POST)
    # if the form is valid
    if company_reg_form.is_valid():
        # get the compnay name
        name = company_reg_form.cleaned_data['name']
        # create a new company
        company = Company(name=name,owner=abq_user)
        company.launch_date = timezone.now()
        # and add it to the database
        company.save()
        # DBG
        if settings.AWS:
            make_company(company.name,get_aws_regions())
        # the form has been successfully submitted so 
        # we should show a clean form
        company_reg_form = CompanyRegForm()
    # return the registration form    
    return company_reg_form


def launch_new_workspace(request, company):
    """ Build and launch a new workspace  """
    
    # get the form from request.POST
    workspace_launch_form = WorkspaceLaunchForm(request.POST)
    # if the value is not the default
    if request.POST['hardware'] != '':
        # get the hardware
        hardware = Hardware.objects.get(pk=request.POST['hardware'])
        # hardware should defintely exist
        if hardware == None:
            raise LookupError('hardware deoes not exist')
        # add the relevant oss
        workspace_launch_form.fields['os'].queryset = \
            OS.objects.filter(hardware=hardware)
        # check if it is valid
        if workspace_launch_form.is_valid() and \
                workspace_launch_form.check_os():
            # add the workspace
            workspace = Workspace()
            workspace.name = workspace_launch_form.cleaned_data['name']
            workspace.company = company
            workspace.hardware = hardware
            workspace.os = workspace_launch_form.cleaned_data['os']
            # if the aws integration flag is on, launch an instance 
            # and prepare it
            # DBG
            if settings.AWS:
                workspace.region  = get_aws_region()
                owner_username = \
                    (request.user.first_name[0]+request.user.last_name).lower()
                workspace.instance_id = get_instance_id(\
                    region_name=workspace.region, 
                    instance_type=hardware.key, 
                    os=workspace.os.key, 
                    company_name=company.name, 
                    uname=owner_username)
            # otherwise just put something there
            else:
                workspace.region      = 'west'
                salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
                workspace.instance_id = \
                    hashlib.sha1(salt+workspace.name).hexdigest()
            # set the launch date and time                        
            workspace.launch_date = timezone.now()
            # background image
            # DBG
            image_filename  = 'workspaceImage__'+company.name+\
                '__'+workspace.name+'.png'
            # for now read from a default file
            source_filename = settings.MEDIA_ROOT+\
                'workspace_images/desktop_background_default.png'
            workspace.set_size_and_save_image(
                image_filename,source_filename)   
            workspace.save()
            # create an empty from
            workspace_launch_form = WorkspaceLaunchForm(
                initial={'company_name': company.name, 
                         'name': 'workspace'})
    else:    
        workspace_launch_form.raise_hardware_error()

    # return the form
    return workspace_launch_form
     

def terminate_workspace(instance_id, region):
    """ Terminate a workspace  """
    
    # check that the combination is unique
    try:
        workspace = Workspace.objects.get(instance_id=instance_id,
                                          region=region)
    except:
        raise Exception(\
            "combination of instance id and region is not unique")
    # here we can do whatever we want
    # terminate the workspace from aws
    # DBG
    if settings.AWS:
        terminate_instance(workspace.instance_id, 
                           workspace.region)
    # and delete the workspace from database
    workspace.delete()
    # and we don't need to return anything
    return True


def populate_os(request):
    """ Populate operating system based on hardware """
    
    # get the form from request.POS
    workspace_launch_form = WorkspaceLaunchForm(request.POST)
    # if the value is not the default
    if request.POST['hardware'] != '':
        # get the hardware
        hardware = Hardware.objects.filter(
            pk=request.POST['hardware'])
        # hardware should defintely exist
        if hardware == None:
            raise LookupError('hardware deoes not exist')
        # and fill in the workspace
        workspace_launch_form.fields['os'].queryset = \
            OS.objects.filter(hardware=hardware)
    # return the form
    return workspace_launch_form


def invite_new_employee(request, company_name):
    """ Send offer letter of employment """
    
    # get the employment form
    employment_form = EmploymentForm(
        request.POST, initial={'company_name': company_name})
    if employment_form.is_valid():
        abq_user = employment_form.cleaned_data['abqUser']
        company = Company.objects.get(name=company_name)        
        employment = Employment(employee=abq_user, company=company)
        # set the activation key and expiration date
        salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
        employment.activation_key = \
            hashlib.sha1(salt+abq_user.user.username).hexdigest()
        employment.key_expiration = \
            timezone.now() + datetime.timedelta(days=7)
        employment.save()
        # email the employee activation link
        domain_name = request.build_absolute_uri('/')
        email_subject = 'Your new Abaqual employment confirmation'
        email_body = 'Hello %s,\n\n ' \
            '%s has sent you an employment request.'\
            ' To accept your offer, click this link within 7 days:\n\n' \
            '%semployment-confirmation/%s' \
            %(employment.employee.user.first_name,\
                  employment.company.name, domain_name, \
                  employment.activation_key)
        thread = threading.Thread(target=send_mail,
                                  args=(email_subject,email_body,
                                        settings.EMAIL_HOST_USER,
                                        [abq_user.user.email]))
        thread.start()
        # and show a new form
        employment_form = EmploymentForm(\
            initial={'company_name': company.name})
    #return the employment form
    return employment_form


def terminate_employment(username, company):
    """ Terminate employment  """
    
    # from username get the abaqual user
    try:
        abq_user = AbqUser.objects.get(user__username=username)
    except:
        raise Exception('user '+username+' does not exist')
    # and get the employment
    try:
        employment = Employment.objects.get(
            employee=abq_user,company=company)
    except:
        raise Exception('problem with employment')
    # delete employment
    employment.delete()
    # we do not need to return anything
    return True


def dissolve_company(company):
    """ Terminate a compnay  """
    
    # just make sure that workspaces are terminated
    # get the compnay's workspaces
    workspaces = Workspace.objects.filter(company=company)
    # for all the workspaces
    for workspace in workspaces:
        terminate_workspace(workspace.instance_id, workspace.region)
    # DBG
    if settings.AWS:
        # remove company keys and other stuffa
        remove_company(company.name,get_aws_regions())
    # and delete the company
    company.delete()
    # don't need to return anything
    return True


def console(request):
    
    # if the user is not authenticated, then redirect them 
    # to the home page where they can lon in
    # make sure that this stays at the top of this function
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/home/')
    
    # if we are here it means tha the user is authenticated
    # so we can get the user
    abq_user = AbqUser.objects.get(user=request.user)

    # there is just one single posting for launching a company
    company_reg_form = CompanyRegForm()

    # build companies forms in a dictionary format
    companies_dict = build_companies_dict(abq_user)

    # if user is posting
    if request.method == 'POST':
        
        # ====================
        # company registration
        # ====================
        
        # if the user is launching a new company
        if 'register_company' in request.POST:
            # make sure the user has expert status
            if abq_user.abaqual_status != 'EX':
                raise Exception(
                    'You are not authorized to start a new company')
            company_reg_form = register_new_company(request,abq_user)
            # if we are registering a new company, 
            # we should rebuild the company dictionary 
            # so the new company shows up
            companies_dict = build_companies_dict(abq_user)
                

        # ================
        # workspace launch
        # ================

        # workspace is a little bit more complicated
        # if user is launching a new workspace
        if 'workspace_launch' in request.POST:
            company_name = request.POST['company_name']
            company = companies_dict[company_name]['company']
            # check that the owner is launching a workspace            
            if company.owner != abq_user:
                raise Exception('only owner can  a workspace')
            companies_dict[company_name]['workspace_launch_form'] = \
                launch_new_workspace(request,company)
            # since we just added a new workspace, we need to 
            # update the list of workspaces for this company
            companies_dict[company_name]['workspaces_list'] = \
                build_workspaces_list(company)
                        
        # if the user is not posting a workspace launch
        else:
            if 'hardware' in request.POST:
                # add os to the list
                company_name = request.POST['company_name']
                companies_dict[company_name]['workspace_launch_form'] = \
                    populate_os(request)
             

        # =================================
        # add /remove software to workspace
        # =================================
        if 'add_remove_software' in request.POST:
            software_form = SoftwareForm(request.POST)
            # get the region, instace id 
            region = request.POST['region']
            instance_id = request.POST['instance_id']
            # check that the combination is unique
            try:
                workspace = Workspace.objects.get(instance_id=instance_id,
                                                  region=region)
            except:
                raise Exception(\
                    "combination of instance id and region is not unique")
            else:
                # initialize the form
                if software_form.is_valid():
                    softwares = software_form.cleaned_data['software']
                    softwares_old = Software.objects.filter(
                        softwarelaunch__workspace=workspace)
                    for software in softwares_old:
                        if software not in softwares:
                            launch = SoftwareLaunch.objects.get(
                                software=software, workspace=workspace)
                            launch.delete()
                    for software in softwares:
                        if not software in softwares_old:
                            launch = \
                                SoftwareLaunch(software=software,
                                               workspace=workspace,
                                               launched_date=timezone.now())
                            launch.save()
        # if user is adding software
        if 'go_to_software' in request.POST:
            # get the company
            company_name = request.POST['company_name']
            company = companies_dict[company_name]['company']
            # check that the owner is launching a workspace            
            if company.owner != abq_user:
                raise Exception('only owner can add software to a workspace')
            # get the region, instace id 
            region = request.POST['region']
            instance_id = request.POST['instance_id']
            # check that the combination is unique
            try:
                workspace = Workspace.objects.get(instance_id=instance_id,
                                                  region=region)
            except:
                raise Exception(\
                    "combination of instance id and region is not unique")
            else:
                # initialize the form
                software_form = SoftwareForm()
                software_form.fields['software'].initial = \
                    Software.objects.filter(\
                    softwarelaunch__workspace=workspace)
                software_form.fields['region'].initial = region
                software_form.fields['instance_id'].initial = instance_id
                context = {'workspace': workspace,
                           'softwares': software_form}
                return render_to_response(
                    'desktop.html', context,
                    context_instance=RequestContext(request))
                             
        # ===================
        # terminate workspace
        # ===================

        if 'terminate_workspace' in request.POST:
            company_name = request.POST['company_name']
            company = companies_dict[company_name]['company']
            # check that the owner terminating a workspace            
            if company.owner != abq_user:
                raise Exception('only owner can terminate a workspace')
            # get the region, instace id 
            region = request.POST['region']
            instance_id = request.POST['instance_id']
            # and terminate workspace
            terminate_workspace(instance_id, region)
            # now we need to rebuild the list
            companies_dict[company_name]['workspaces_list'] = \
                build_workspaces_list(company)
            


        # ===================================
        # invite a person to join the company
        # ===================================
        
        # if the user is inviting a person
        if 'invite_employee' in request.POST:
            # get company name
            company_name = request.POST['company_name']
            company = companies_dict[company_name]['company']
            # check that the owner terminating a workspace            
            if company.owner != abq_user:
                raise Exception('only owner can invite a new person')
            # now we need to replace the form we had in the dictionary
            companies_dict[company_name]['employment_form'] = \
                invite_new_employee(request, company_name)     
            # we need to add the employee to the pending list
            companies_dict[company_name]['employees_list'] = \
                build_employees_list(company)


        # ====================
        # terminate employment
        # ====================

        if 'terminate_employment' in request.POST:
            # get company name
            company_name = request.POST['company_name']
            company = companies_dict[company_name]['company']
            # check that the owner terminating an employment            
            if company.owner != abq_user:
                raise Exception('only owner can terminate an employment')
            # get the username
            username = request.POST['username']
            terminate_employment(username, company)
            # we need to rebuild the employees list
            companies_dict[company_name]['employees_list'] = \
                build_employees_list(company)
            # as well as employment form
            companies_dict[company_name]['employment_form'] = \
                EmploymentForm(initial={'company_name': company_name})

        # ==================
        # dissolve a company
        # ==================

        if 'dissolve_company' in request.POST:
            # get company name
            company_name = request.POST['company_name']
            # get the company
            company = Company.objects.get(name=company_name)
            # check that the owner is dissolving a company            
            if company.owner != abq_user:
                raise Exception('only owner can dissolve a company')
            # dissolve the company
            dissolve_company(company)
            # we need to rebuild the companies dictionary
            companies_dict = build_companies_dict(abq_user)
            

    # context based on the populated fields
    context = {'abq_user': abq_user,
               'company_reg_form':company_reg_form,
               'companies_dict': companies_dict
               }
    return render_to_response('console.html', context,
                              context_instance=RequestContext(request))



def EmploymentConfirmation(request,activation_key):
    
    # get the employment letter
    try:
        employment = Employment.objects.get(activation_key=activation_key)
    # if user does not exists
    except ObjectDoesNotExist:
        return render_to_response(
            'employment_confirmation.html',{'no_account': True},
            context_instance=RequestContext(request))
    # otherwise check the time 
    else:
        # if user has not already activated their account
        if employment.start_date is None:
            # if the key has expired, delete the employment 
            # and redirect them to expiration
            if employment.key_expiration < timezone.now():
                employment.delete()
                return render_to_response(
                    'employment_confirmation.html',{'expired': True},
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
        return HttpResponseRedirect('/console/')

    
def UserRegistration(request):
    
    # if the user is already authenticated,
    # redirect them to his/her profile
    if request.user.is_authenticated():
        return HttpResponseRedirect('/console/')
    # if user is registering
    if request.method == 'POST':
        # get the form they just posted
        form =RegistrationForm(request.POST)
        # if the form is valid
        if form.is_valid():
            # get their username and password
            username = form.cleaned_data['username'].lower()
            password = form.cleaned_data['password']
            # create the user
            user = User.objects.create_user(username=username,
                                            password=password)
            # set first name, last name and email address
            user.email      = username;
            user.first_name = form.cleaned_data['firstname']
            user.last_name  = form.cleaned_data['lastname']
            # set the user as inactive and wait for confirmation
            user.is_active  = False
            # save the user into data-base
            user.save()
            # now create an abaqual user
            # DBG  --> user is always given an professional status
            abqUser = AbqUser(user=user,abaqual_status='EX')
            # set the activation key and expiration date
            salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
            abqUser.activation_key = hashlib.sha1(salt+username).hexdigest()
            abqUser.key_expiration = timezone.now() + \
                datetime.timedelta(hours=48)
            # save abaqual user into database
            abqUser.save()

            # create a file for nx authentication
            filename = settings.STATICFILES_DIRS[0] + \
                '/nxauth/' + abqUser.activation_key + '.js'
            with open(filename, 'w') as f:
                myfile = File(f)
                body = 'function user_auth() {\n'\
                    '  var uname = "%s";\n'\
                    '  var pass  = "%s";\n'\
                    'return [uname,pass] ;\n'\
                    '}' \
                    %(username, abqUser.activation_key)
                myfile.write(body)
            myfile.closed
            f.closed

            # email the user activation link
            domain_name = request.build_absolute_uri('/')
            email_subject = 'Your new Abaqual account confirmation'
            email_body = 'Hello %s, and thanks for signing up '\
                'for an Abaqual account!\n\n ' \
                'To activate your account, click this '\
                'link within 48 hours:\n\n' \
                '%sregistration-confirmation/%s' \
                %(abqUser.user.first_name, domain_name, 
                  abqUser.activation_key)
            thread = threading.Thread(target=send_mail,
                                      args=(email_subject,email_body,
                                            settings.EMAIL_HOST_USER,
                                            [abqUser.user.email]))
            thread.start()
            # and redirect them to thank you page
            return render_to_response('registration_thankyou.html')
        # if the form is not valid show then the form again
        else:
            return render_to_response(
                'registration.html', {'form':form}, 
                context_instance=RequestContext(request))
    # otherwise show the user an empty form
    else:
        form = RegistrationForm()
        return render_to_response(
            'registration.html', {'form':form}, 
            context_instance=RequestContext(request))



def RegistrationConfirmation(request,activation_key):
    
    # if user is already authenticated, 
    # then they cannot confirm a new account
    if request.user.is_authenticated():
        return render_to_response(
            'registration_confirmation.html',
            {'has_account': True, 'username': request.user.username},
            context_instance=RequestContext(request))
    # if not then try to get the abaqual user based on the activation key
    try:
        abqUser = AbqUser.objects.get(activation_key=activation_key)
    # if user does not exists
    except ObjectDoesNotExist:
        return render_to_response(
            'registration_confirmation.html',
            {'no_account': True},
            context_instance=RequestContext(request))
    # otherwise check the time 
    else:
        # check if user is already activated, 
        # then just redirect them to their profile
        if ( abqUser.user.is_active ):
            # log in the user and redirect them to their profile
            login_user_no_credentials(request,abqUser.user)
            return HttpResponseRedirect('/console/')
        # if the key has expired, delete the user and 
        # redirect them to expiration
        if abqUser.key_expiration < timezone.now():
            abqUser.user.delete()
            abqUser.delete()
            return render_to_response(
                'registration_confirmation.html',
                {'expired': True},
                context_instance=RequestContext(request))
        # otherwise activate user
        abqUser.user.is_active = True
        # save in the data base
        abqUser.user.save();
        # lon in the user and redirect them to their profile
        login_user_no_credentials(request,abqUser.user)
        return HttpResponseRedirect('/console/')



def ContactUs(request):

    # if the user is posting  
    if request.method == 'POST':
        # populate the form from post
        form = ContactUsForm(request.POST)
        # if the form is valid
        if form.is_valid():
            # first email the content 
            email_address = 'shared@abaqual.com'
            email_subject = 'Abaqual contact us request'
            email_body = \
                'First name: %s\n' \
                'Last name: %s\n' \
                'Email address: %s\n' \
                'message: %s\n' \
                %(form.cleaned_data['firstname'],\
                      form.cleaned_data['lastname'],\
                      form.cleaned_data['email'],\
                      form.cleaned_data['message'])
            thread = threading.Thread(target=send_mail,
                                      args=(email_subject,email_body,
                                            settings.EMAIL_HOST_USER,
                                            [email_address]))
            thread.start()
            # redirect them to a thank you page
            return render_to_response(
                'contactus_thankyou.html',
                context_instance=RequestContext(request)) 

    else:
        # show them an empty form
        form = ContactUsForm()

    return render_to_response(
        'contactus.html',
        {'form': form}, 
        context_instance=RequestContext(request)) 


def LoginRequest(request):
    
    # if the user is already authenticated redirect them to profile
    if request.user.is_authenticated():
        return HttpResponseRedirect('/console/')    
    # if the user is posting  
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        # check form is valid
        if login_form.is_valid():
            # get username and password
            username = login_form.cleaned_data['username'].lower()
            password = login_form.cleaned_data['password']
            # authenticate user
            user = authenticate(username=username, password=password)
            # check if the user is autheticated
            if user is not None:
                # log the user in
                login(request,user)
                # and redirect the user to his/her profile
                return HttpResponseRedirect('/console/')
            # otherwise show them the form again
            else:
                return render_to_response(
                    'home.html', 
                    {'login_form': login_form}, 
                    context_instance=RequestContext(request))
        # if the form is not valid, show th blank form again
        else:
            return render_to_response(
                'home.html', 
                {'login_form': login_form}, 
                context_instance=RequestContext(request))
    # otherwise show them a blank form
    else:
        login_form = LoginForm()
        return render_to_response(
            'home.html', 
            {'login_form': login_form}, 
            context_instance=RequestContext(request))


def LogoutRequest(request):
    # log out user
    logout(request)
    # and redirect them to home
    return HttpResponseRedirect('/home')
