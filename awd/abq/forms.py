from django import forms
from django.contrib.auth.models import User



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
    
