from django import forms
from django.contrib.auth.forms import UserCreationForm
from userauths.models import User,Profile

USER_TYPE=(
    ("Vendor","Vendor"),
    ("Customer","Customer"),
)

class UserRegisterForm(UserCreationForm):
    full_name=forms.CharField(widget=forms.TextInput(attrs={"placeholder":'Fullname'}),required=True)
    email=forms.EmailField(widget=forms.EmailInput(attrs={"placeholder":'E-Mail'}))
    mobile=forms.CharField(widget=forms.TextInput(attrs={"placeholder":'Mobile'}))
    password1=forms.CharField(widget=forms.PasswordInput(attrs={"placeholder":'Password'}))
    password2=forms.CharField(widget=forms.PasswordInput(attrs={"placeholder":'Confirm Password'}))
    user_type=forms.ChoiceField(choices=USER_TYPE,widget=forms.Select(attrs={"placeholder":"User_type"}))

    class Meta:
        model=User
        fields=['full_name','email','mobile','password1','password2','user_type']

class LoginForm(forms.Form):
    email=forms.EmailField(widget=forms.EmailInput(attrs={"placeholder":'E-Mail'}))
    password1=forms.CharField(widget=forms.PasswordInput(attrs={"placeholder":'Password'}))

    class Meta:
        model=User
        fields=['email','password']

class VendorLoginForm(forms.Form):
    email=forms.EmailField(widget=forms.EmailInput(attrs={"placeholder":'E-Mail'}))
    password1=forms.CharField(widget=forms.PasswordInput(attrs={"placeholder":'Password'}))

    class Meta:
        model=User
        fields=['email','password']


