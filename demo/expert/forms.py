from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm
from expert.models import Expert

class RegistrationForm(ModelForm):
    username    = forms.EmailField(label=(u'Email Address'))
    first_name  = forms.CharField(label=(u'First Name'))
    last_name   = forms.CharField(label=(u'Last Name'))
    password    = forms.CharField(label=(u'Password'), widget=forms.PasswordInput(render_value=False))
    password1   = forms.CharField(label=(u'Verify Password'), widget=forms.PasswordInput(render_value=False))
    
    class Meta:
        model = Expert
        exclude = ('user',)
        
    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError("That username is already taken, please select another.")
    
    def clean(self):
        if self.cleaned_data['password'] != self.cleaned_data['password1']:
            raise forms.ValidationError("The passwords did not match.  Please try again.")
        return self.cleaned_data
    
class LoginForm(forms.Form):
        username        = forms.EmailField(label=(u'User Name'))
        password        = forms.CharField(label=(u'Password'), widget=forms.PasswordInput(render_value=False))
