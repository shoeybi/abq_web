from django                         import forms
from django.db                      import models
from django.contrib.auth.models     import User
from django.forms                   import ModelForm
from django.forms.util              import ErrorDict, ErrorList
from abq.models                     import AbqUser, Company, Workspace, Hardware, OS, \
    Employment


class EmploymentForm(forms.Form):

    # the user we are inviting
    abqUser = forms.ModelChoiceField(queryset=AbqUser.objects.exclude(
            abaqual_status='CU'),empty_label='choose a user')
    # company name
    company_name = forms.CharField(widget=forms.HiddenInput())


class WorkspaceLaunchForm(forms.Form):

    # company name
    company_name = forms.CharField(widget=forms.HiddenInput())
    # show hardware option and resubmit the form as soon as it is changed
    hardware = forms.ModelChoiceField(queryset=Hardware.objects.all(),
                                      widget=forms.Select(attrs={"onChange":'submit()'}),
                                      empty_label='Select a hardware')
    # by default, don't show any os until we know thw hardware
    os       = forms.ModelChoiceField(queryset=OS.objects.none(), 
                                      empty_label="Selec an os", required=False)

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
            self._errors['os'] = ErrorList([u'os field is required'])
            return False
        


class CompanyForm(ModelForm):
    
    # company form only need a name
    class Meta:
        model = Company
        exclude = ('owner','launch_date',)

    # check that the company name is unique
    def clean_name(self):
        # get the company name
        name = self.cleaned_data['name']
        # search the database
        try: 
            Company.objects.get(name=name)
        # if the company name is not already taken, return the name
        except Company.DoesNotExist:
            return name            
        # otherwise raise a validation error
        raise forms.ValidationError('company name '+name+
                                    ' is taken. Please select a different name.')


class RegistrationForm(forms.Form):
    
    # minimum information required for registration
    username  = forms.EmailField(label=(u'Email Address'))
    firstname = forms.CharField(label=(u'First Name'))
    lastname  = forms.CharField(label=(u'Last Name'))
    password  = forms.CharField(label=(u'Password'), 
                                 widget=forms.PasswordInput(render_value=False))
    password1 = forms.CharField(label=(u'Verify Password'), 
                                 widget=forms.PasswordInput(render_value=False))

    # check that username does not already exist
    def clean_username(self):
        # get the username from form
        username = self.cleaned_data['username']
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(username+" is already taken.")

    # check passwords match
    def clean(self):
        if self.cleaned_data['password'] != self.cleaned_data['password1']:
            raise forms.ValidationError("The passwords did not match")
        # make sure we return the cleaned_data
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
    
