from django import forms
from django.contrib.auth.forms import UserCreationForm
from userauths.models import User,Profile

USER_TYPE=(
    ("Vendor","Vendor"),
    ("Customer","Customer"),
)

class LoginForm(forms.Form):
    email=forms.EmailField(widget=forms.EmailInput(attrs={"placeholder":'E-Mail'}))
    password1=forms.CharField(widget=forms.PasswordInput(attrs={"placeholder":'Password'}))

    class Meta:
        model=User
        fields=['email','password']
