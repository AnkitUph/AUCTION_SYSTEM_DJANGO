from django.shortcuts import render,redirect
from django.contrib import messages
from django.conf import settings
from django.contrib.auth import authenticate,login,logout
from django.contrib.messages import WARNING

from userauths import forms as userauths_forms
from vendor import models as vendor_models 
from userauths import models as userauths_models
from django.contrib.auth.hashers import check_password



User = settings.AUTH_USER_MODEL  #link with AUTH_USER_MODEL in settings.py

def register_view(request):
    if request.method=="POST":
        form=userauths_forms.UserRegisterForm(request.POST or None)
        if form.is_valid():
            user=form.save()
            full_name=form.cleaned_data.get("full_name")
            password=form.cleaned_data.get('password1')
            email=form.cleaned_data.get("email")
            mobile=form.cleaned_data.get("mobile")
            user_type=form.cleaned_data.get("user_type")
            
            user=authenticate(request,email=email,password=password)
            
            login(request,user)

            messages.success(request,f"Hey {full_name},Your account was created succesfully")
            profile=userauths_models.Profile.objects.create(user=user,full_name=full_name,mobile=mobile)
            if user_type=="Vendor":
                vendor_models.Vendor.objects.create(user=user,store_name=full_name)
                profile.user_type="Vendor"
            else:
                profile.user_type="Customer"

            profile.save()
            return redirect('base:home')
           

    else:
        
        form=userauths_forms.UserRegisterForm()

    context ={
        'form':form,
    }

    return render(request,'userauths/sign-up.html',context)

def login_view(request):
    if request.user.is_authenticated:
        redirect('base:home')
    
    if request.method=="POST":
        email=request.POST.get("email")
        password=request.POST.get("password")

        try:
            user=User.objects.get(email=email)
        except:
            messages.warning(request,f"User with {email} doesn't exist")
        
        user=authenticate(request,email=email,password=password)

        if user is not None:
            login(request,user)
            return redirect('base:home')
        else:
            messages.warning(request,"User doesn't exist create an account")
    
    context={

    }
    
    return render(request,"userauths/sign-in.html",context)

def logout_view(request):
    logout(request)
    messages.success(request,"You have been sucessfully Logged-out")
    return redirect('base:home')




