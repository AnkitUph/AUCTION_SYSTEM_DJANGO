from django.shortcuts import render,redirect,get_object_or_404
from django.urls import path
from base import models as base_models
from vendor  import models as vendor_models
from customer import models as customer_models
from django.contrib.auth.decorators import login_required
from django.db import models
from django.contrib import messages
from django.http import JsonResponse
from django.utils.text import slugify
import os
from django.conf import settings
from django.utils import timezone
from django.utils.timezone import now
from decimal import Decimal
from base.decorators import customer_required

def home(request):#main page
    categories = base_models.Category.objects.all()[:6]  # Show only first 6
    products = base_models.Product.objects.filter(is_active=True)[:6]  # Show only first 6
    context = {
        'categories': categories,
        'products': products,
    }
    return render(request, 'base/index.html', context)


def account(request):
    return render(request,'base/account.html')

def products(request):#products page
    products=base_models.Product.objects.filter(is_active=True)
    context={"products":products,}
    return render(request,'base/products.html',context)

def category_list(request):#category list page
    categories=base_models.Category.objects.all()

    context={
        'categories':categories,
        
    }
    return render(request,'base/category_list.html',context)

def category_list_product(request,slug):#category maparne products haru
    category = get_object_or_404(base_models.Category, slug=slug)
    products=base_models.Product.objects.filter(category=category,is_active=True)

    context={
        'category':category,
        'products':products,
    }
    return render (request,'base/category_list_product.html',context)


def product_detail(request,id):
    product=base_models.Product.objects.get(id=id)
    bids_history = base_models.BidsHistory.objects.filter(product=product).order_by('-bid_time')
    
    context={
    "product":product,
    'bids_history': bids_history
    }
    return render(request,'base/product_detail.html',context)

@customer_required
def place_bid(request,id):
    product = get_object_or_404(base_models.Product, id=id)
    
    if request.method == "POST":
        try:
            bid_amount = float(request.POST.get("bid_amount"))
        except (ValueError, TypeError):
            messages.error(request, "Invalid bid amount")
            return redirect("base:product_detail",product.id)

        # Get current highest bid or starting price
        current_bid = product.current_bid if product.current_bid else product.start_bid
        
        if Decimal(bid_amount) <= Decimal(current_bid):
            messages.error(request, f"Bid must be higher than ${current_bid:.2f}")
            messages.Al
            return redirect("base:product_detail",product.id)

        # Create new bid
        new_bid = base_models.Bid.objects.create(
            product=product,
            bidder=request.user,
            bid_amount=bid_amount,
            bid_time=timezone.now()
        )
        base_models.BidsHistory.objects.create(
            product=product,
            user=request.user,
            bid_amount=bid_amount,
            bid_time=timezone.now()
        )
        print(new_bid)

        # Update product's current bid
        product.current_bid = new_bid.bid_amount
        product.save()
        bids_history = base_models.BidsHistory.objects.filter(product=product)

        messages.success(request, "Bid placed successfully!")
        return redirect("base:product_detail",product.id)

    context={
        'products':products,
        'bids_history':bids_history
    }
    return render(request,"base/products.html",context)

def search_view(request):
    
    query = request.GET.get('query', '')  # Default to an empty string if query is None
    if query:  # Only filter if query is not empty
        products = base_models.Product.objects.filter(name__icontains=query).order_by('-auction_start_time')
    else:
        products = base_models.Product.objects.all()  # Or return an empty queryset


    context={
        'products':products,
        'query':query,
    }
    return render(request,"base/search.html",context)
