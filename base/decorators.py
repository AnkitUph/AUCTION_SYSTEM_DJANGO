from django.shortcuts import redirect
from django.urls import reverse
from functools import wraps
from django.contrib import messages
from django.contrib.auth import logout



def vendor_required(view_func):
    @wraps(view_func)
    def wrapper_func(request, *args, **kwargs):
        if hasattr(request.user, 'profile') and request.user.profile.user_type == "Vendor":
            return view_func(request, *args, **kwargs)
        else:
            messages.warning(request, "You were logged out as a customer. Please log in as a vendor to access this page.")
            logout(request)  # Log out the customer
            return redirect(reverse('vendor:vendor-login'))  # Redirect to vendor login page
    return wrapper_func

def customer_required(view_func):
    @wraps(view_func)
    def wrapper_func(request, *args, **kwargs):
        if hasattr(request.user, 'profile') and request.user.profile.user_type == "Customer":
            return view_func(request, *args, **kwargs)
        else:
            messages.warning(request, "You were logged out . Please log in as a customer to access this page.")
            logout(request)  # Log out the customer
            return redirect(reverse('customer:customer-login'))  # Redirect to vendor login page
    return wrapper_func
