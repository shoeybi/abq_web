from django import forms
from django.db import models
from django.contrib.auth.models import User
from django.forms import ModelForm
from django.forms.util import ErrorDict, ErrorList
from abq.models import AbqUser, Company, Workspace, Hardware, OS, \
    Employment, Software


class SoftwareForm(forms.Form):

    software = forms.ModelMultipleChoiceField(
        queryset=Software.objects.all(), 
        widget=forms.CheckboxSelectMultiple,
        required=False)
    region = forms.CharField(widget=forms.HiddenInput())
    instance_id = forms.CharField(widget=forms.HiddenInput())


class RequestToolForm(forms.Form):

    name = forms.CharField(max_length=100, label=(u'Requested tool'))
    link = forms.URLField(max_length=200, required=False)
    email = forms.EmailField(label=(u'Email Address'))
    comment = forms.CharField(widget=forms.Textarea, 
                              label=(u'Comment'), required=False)

    # clean 
    def clean(self):
        # first we need to get access to the original cleaned_data method
        cleaned_data = super(RequestToolForm,self).clean()
        # get the tool name
        name = cleaned_data.get('name')
        if name == None :
            if not self._errors:
                self._errors = ErrorDict()
            self._errors['name'] = ErrorList(
                [u' Requested tool name is required.'])
        # get the email address
        email = cleaned_data.get('email')
        if email == None :
            if not self._errors:
                self._errors = ErrorDict()
            self._errors['email'] = ErrorList(
                [u' Email address is not valid.'])
        return self.cleaned_data


class ContactUsForm(forms.Form):

    firstname = forms.CharField(max_length=100, label=(u'First Name'))
    lastname = forms.CharField(max_length=100, label=(u'Last Name'))
    email = forms.EmailField(label=(u'Email Address'))
    message = forms.CharField(widget=forms.Textarea, label=(u'Message'))

    # clean 
    def clean(self):
        # first we need to get access to the original cleaned_data method
        cleaned_data = super(ContactUsForm,self).clean()
        # get the first name
        firstname = cleaned_data.get('firstname')
        if firstname == None :
            if not self._errors:
                self._errors = ErrorDict()
            self._errors['firstname'] = ErrorList(
                [u' First name is required.'])
        # get the last name
        lastname = cleaned_data.get('lastname')
        if lastname == None :
            if not self._errors:
                self._errors = ErrorDict()
            self._errors['lastname'] = ErrorList(
                [u' Last name is required.'])
        # get the email address
        email = cleaned_data.get('email')
        if email == None :
            if not self._errors:
                self._errors = ErrorDict()
            self._errors['email'] = ErrorList(
                [u' Email address is not valid.'])
        # get the email address
        message = cleaned_data.get('message')
        if message == None :
            if not self._errors:
                self._errors = ErrorDict()
            self._errors['message'] = ErrorList(
                [u' Message is required.'])

        return self.cleaned_data


class EmploymentForm(forms.Form):
    
    # invited user
    abqUser = forms.ModelChoiceField(
        queryset=AbqUser.objects.exclude(
            abaqual_status='CU'),empty_label='invite a user')
    # company name
    company_name = forms.CharField(widget=forms.HiddenInput())
    
    def __init__(self,*arguments,**kwargs):
        # initialize the base class
        super(EmploymentForm, self).__init__(*arguments,**kwargs)
        # get the company name
        company_name = self.initial.get('company_name')
        if company_name != None :
            # get the company
            company = Company.objects.get(name=company_name)
            # first exclude the owner from the list
            self.fields['abqUser'].queryset = \
                self.fields['abqUser'].queryset.exclude(\
                user=company.owner.user) 
            # get the current list of employees
            employees = company.employee.all()
            # now remove current employees
            for employee in employees:
                self.fields['abqUser'].queryset = \
                    self.fields['abqUser'].queryset.exclude(
                    user=employee.user) 
        else:
            raise forms.ValidationError('company name is not valid.')

    # check that abqUser is neither the owner nor 
    # already works for the company
    def clean(self):
        # get access to the original cleaned_data methods
        cleaned_data = super(EmploymentForm,self).clean()
        # company name
        company_name = cleaned_data.get('company_name')
        # check that there was not a validation error
        if company_name == None:
            raise forms.ValidationError("company name is not valid.")
        # check if company exist
        try:
            company = Company.objects.get(name=company_name)
        # if not raise an error
        except Company.DoesNotExist:
            raise forms.ValidationError(
                'company '+company_name+' does not exist.')
        # otherwise, check for the employee
        else:
            # user
            abqUser = cleaned_data.get('abqUser')
            # check that there was not a validation error
            if abqUser == None:
                raise forms.ValidationError("user is invalid.")
            # first make sure that user is not the owner
            if abqUser == company.owner:
                raise forms.ValidationError('You are inviting yourself.')
            # check that invitee is not already part of the company
            if abqUser in company.employee.all():
                raise forms.ValidationError(
                    abqUser.user.username+' is already a member.')
        # make sure we return the cleaned_data
        return self.cleaned_data


class EmploymentTerminationForm(forms.Form):

    # username (unique)
    username = forms.EmailField(widget=forms.HiddenInput())
    # company name
    company_name = forms.CharField(widget=forms.HiddenInput())


class WorkspaceLaunchForm(forms.Form):

    # company name
    company_name = forms.CharField(widget=forms.HiddenInput())
    # workspace name
    name = forms.CharField(max_length=100, 
                           label=(u'Name'), 
                           initial='new workspace')
    # show hardware option and resubmit the form as soon as it is changed
    hardware = forms.ModelChoiceField(
        queryset=Hardware.objects.all(),
        #widget=forms.Select(attrs={"onChange":'submit()'}),
        initial=1,
        empty_label='Hardware')
    # by default, don't show any os until we know thw hardware
    hardware_initial = Hardware.objects.get(pk=1)
    os = forms.ModelChoiceField(
        queryset=OS.objects.filter(hardware=hardware_initial),
        initial=1,
        empty_label="Operating system") 
        #required=False)

    # clean the name
    def clean(self):
        try:
            name = self.cleaned_data['name']
        except:
            if not self._errors:
                self._errors = ErrorDict()
            self._errors['name'] = ErrorList(
                [u' Workspace name is required.'])
        return self.cleaned_data
    
    # because os is to optional but is needed to form a workspace
    # we define a special method that checks if the os is valid otherwise
    # it adds an error message to the field errorlist
    def check_os(self):
        os = self.cleaned_data['os']
        if os != None:
            return True
        else:
            if not self._errors:
                self._errors = ErrorDict()
            self._errors['os'] = ErrorList([u'Operating system is required'])
            return False

    # raise an error for the case that hardware is not provided
    def raise_hardware_error(self):
        if not self._errors:
            self._errors = ErrorDict()
        self._errors['hardware'] = ErrorList([u' Hardware is required'])
        

class WorkspaceTerminateForm(forms.Form):

    # company name
    company_name = forms.CharField(widget=forms.HiddenInput())
    # workspace id and region
    region = forms.CharField(widget=forms.HiddenInput())
    instance_id = forms.CharField(widget=forms.HiddenInput())
    
    # check that the combination id and region exists and it unique
    def clean(self):
        instance_id = self.cleaned_data['instance_id']
        region = self.cleaned_data['region']
        try:
            Workspace.objects.get(instance_id=instance_id,
                                  region=region)
        except:
            raise forms.ValidationError(\
                "combination of instance id and region is not unique")
        # make sure we return the cleaned_data
        return self.cleaned_data

            
class CompanyRegForm(forms.Form):
            
    # company form only need a name
    name = forms.CharField(max_length=100, 
                           label=(u'Company name'))

    def clean(self):
        # first we need to get access to the original cleaned_data method
        cleaned_data = super(CompanyRegForm,self).clean()
        # get the name from the form
        name = cleaned_data.get('name')
        # if there was a validation error then name has not been a valid one
        if name == None:
            raise forms.ValidationError("Company name is not valid.")
        # otherwise try to find if the name is in the database
        # search the database
        try: 
            Company.objects.get(name=name)
        # if the company name is not already taken, return the name
        except Company.DoesNotExist:
            pass            
        # otherwise raise a validation error
        else:
            raise forms.ValidationError(
                'Company name '+name+
                ' is taken. Please select a different name.')
        # return cleaned_data so the methos returns 
        # the full list of cleaned_data
        return self.cleaned_data


class RegistrationForm(forms.Form):
    
    # minimum information required for registration
    username  = forms.EmailField(label=(u'Email Address'))
    firstname = forms.CharField(label=(u'First Name'))
    lastname  = forms.CharField(label=(u'Last Name'))
    password  = forms.CharField(
        label=(u'Password'), 
        widget=forms.PasswordInput(render_value=False))
    password1 = forms.CharField(
        label=(u'Verify Password'), 
        widget=forms.PasswordInput(render_value=False))
    
    def clean(self):
        # first we need to get access to the original cleaned_data method
        cleaned_data = super(RegistrationForm,self).clean()
        
        # get the username from the form
        username = cleaned_data.get('username')
        # if there was a validation error then email has not been a valid one
        if username == None:
            if not self._errors:
                self._errors = ErrorDict()
            self._errors['username'] = \
                ErrorList([u' Email address is not valid.'])
        else:
            # otherwise try to find if the username is in the database
            username = username.lower()
            try:
                User.objects.get(username=username)
            # if user does not exist then it is valid
            except User.DoesNotExist:
                pass
            # otherwise raise an error
            else:
                if not self._errors:
                    self._errors = ErrorDict()
                self._errors['username'] = \
                    ErrorList([username+' is already taken.'])

        # get the firstname from the form
        firstname = cleaned_data.get('firstname')
        # if there was a validation error then 
        # firstname has not been a valid one
        if firstname == None:
            if not self._errors:
                self._errors = ErrorDict()
            self._errors['firstname'] = \
                ErrorList([u'First name is not valid.'])

        # get the lastname from the form
        lastname = cleaned_data.get('lastname')
        # if there was a validation error then 
        # lastname has not been a valid one
        if lastname == None:
            if not self._errors:
                self._errors = ErrorDict()
            self._errors['lastname'] = \
                ErrorList([u'Last name is not valid.'])

        # password
        # get the password from the form
        password = cleaned_data.get('password')
        # if there was a validation error then 
        # password has not been a valid one
        if password == None:
            if not self._errors:
                self._errors = ErrorDict()
            self._errors['password'] = \
                ErrorList([u'Password is not valid.'])
            
        # get the password from the form
        password1 = cleaned_data.get('password1')
        # if there was a validation error then 
        # password has not been a valid one
        if password1 == None:
            if not self._errors:
                self._errors = ErrorDict()
            self._errors['password1'] = \
                ErrorList([u'Password is not valid.'])
            
        # check that the two passwords are the same
        if password != password1:
            raise forms.ValidationError("Passwords did not match")

        # return cleaned_data so the methods returns 
        # the full list of cleaned_data
        return self.cleaned_data
    

class LoginForm(forms.Form):

    # login required info
    username = forms.EmailField(label=(u'User Name'))
    password = forms.CharField(label=(u'Password'), 
                               widget=forms.PasswordInput(render_value=False))

    # check that 
    #   1) username exists in the database
    #   2) password matches
    def clean(self):
        # first we need to get access to the original cleaned_data method
        cleaned_data = super(LoginForm,self).clean()
        # get the username from the form
        username = cleaned_data.get('username')
        # if there was a validation error then email has not been a valid one
        if username == None:
            raise forms.ValidationError("Email address is not valid.")
        # otherwise try to find if the username is in the database
        username = username.lower()
        try:
            User.objects.get(username=username)
        # if user does not exist then raise an error
        except User.DoesNotExist:
            raise forms.ValidationError("Email address does not exist.")
        # otherwise check the password
        else:
            password = cleaned_data.get('password')
            user = User.objects.get(username=username)
            # if the user is not active raise an error
            if not user.is_active:
                raise forms.ValidationError(
                    'Your account is not activated. Please check your email.')
            if not user.check_password(password): 
                raise forms.ValidationError('Password did not match.')
        # return cleaned_data so the methos returns the full list of cleaned_data
        return self.cleaned_data
    
