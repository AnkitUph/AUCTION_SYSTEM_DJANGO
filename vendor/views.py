from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from base import models as base_models
from vendor  import models as vendor_models
from django.db import models
from django.db.models.functions import TruncMonth
from django.contrib import messages
from django.http import JsonResponse
from django.utils.text import slugify
from django.conf import settings
from base.decorators import vendor_required
from django.contrib.auth import authenticate, login,update_session_auth_hash
from django.contrib.messages import WARNING
from userauths import models as userauths_models
from customer import models as customer_models
from django.http import JsonResponse
from django.contrib.auth.hashers import check_password
from django.views.decorators.csrf import csrf_exempt

USER_TYPE=(
    ("Vendor","Vendor"),
    ("Customer","Customer"),
)
Delivery_status=(
    ("processing","Processing"),
    ("shipped","Shipped"),
    ("delivered","Delivered"),
)


User = settings.AUTH_USER_MODEL

def get_monthly_revenue():
    monthly_revenue=(
        base_models.BidsWon.objects.annotate(month=TruncMonth("won_time"))
        .values("month")
        .annotate(order_count=models.Count("id"))
        .order_by("month")
    )
    return monthly_revenue


def vendor_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user = userauths_models.User.objects.get(email=email)
        except:
            messages.warning(request, f"User with {email} doesn't exist")
            return redirect("vendor:login")  # Redirect to login page

        user = authenticate(request, email=email, password=password)

        if user is not None:
            # Check if the user has a profile before accessing it
            if hasattr(user, 'profile') and user.profile.user_type == "Vendor":
                login(request, user)
                return redirect("vendor:dashboard")  # Redirect to vendor dashboard
            else:
                messages.warning(request, "You are logged in as a customer. Please log in as a vendor.")
                return redirect("vendor:vendor-login")
        else:
            messages.error(request, "Invalid credentials or not a vendor account.")

    context = {}
    return render(request, "vendor/login.html", context)

@vendor_required
def dashboard(request):
    products=base_models.Product.objects.filter(vendor=request.user)
    product_sold=base_models.BidsWon.objects.filter(product__vendor=request.user)
    revenue=base_models.BidsWon.objects.filter(product__vendor=request.user).aggregate(total=models.Sum('winning_bid'))['total']
    notis=vendor_models.Notification.objects.filter(user=request.user,seen=False)
    reviews=base_models.Review.objects.filter(product__vendor=request.user)
    rating=base_models.Review.objects.filter(product__vendor=request.user).aggregate(avg=models.Avg("rating"))['avg']
    monthly_revenue=get_monthly_revenue()
    orders=base_models.Product.objects.filter(id__in=base_models.Order.objects.filter(product__vendor=request.user).values_list('product', flat=True).distinct())

    context={
        'products':products,
        'product_sold':product_sold,
        'revenue':revenue,
        'notis':notis,
        'reviews':reviews,
        'rating':rating,
        'orders':orders,
    }

    return render(request,"vendor/dashboard.html",context)

@vendor_required
def profile(request):
    profile=request.user.profile

    if request.method=="POST":
        image=request.FILES.get("image")
        full_name=request.POST.get("full_name")
        mobile=request.POST.get("mobile")
        bio=request.POST.get("bio")

        if image !=None:
            profile.image=image
        
        profile.full_name=full_name
        profile.mobile=mobile
        profile.bio=bio

        request.user.save()
        profile.save()

        messages.success(request,"Profile updated Succesfully")
        return redirect("vendor:profile")
    
    context={
        "profile":profile
    }
    return render(request,"vendor/profile.html",context)

def change_password(request):
    user=request.user

    if request.method=="POST":
        old_password=request.POST.get("old_password")
        new_password=request.POST.get("new_password")
        confirm_new_password=request.POST.get("confirm_new_password")

        if confirm_new_password!=new_password:
            messages.error(request,"Password doesn't match")
            return redirect("vendor:change_password")
        
        if check_password(old_password,user.password):
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request,user)#keeps user logged in 
            messages.success(request,"Password changed Succesfully")
            return redirect("vendor:profile")
        else:
            messages.error(request,"Old password is incorrect")
            return redirect("vendor:change_password")
        
    return render(request, "vendor/change_password.html")


@vendor_required
def products(request):#products listed by seller
    products=base_models.Product.objects.filter(vendor=request.user)

    context={
        'products':products
    }

    return render(request,"vendor/products.html",context)

@vendor_required
def products_sold(request):
    products_sold=base_models.Product.objects.filter(id__in=base_models.BidsWon.objects.filter(product__vendor=request.user).values_list('product', flat=True).distinct())

    context={
        'products_sold':products_sold
    }

    return render(request,"vendor/products_sold.html",context)


@vendor_required
def orders(request):
    vendor = request.user.vendor
    orders=base_models.Order.objects.filter(product__vendor=request.user).select_related('product')
    payouts = vendor_models.Payout.objects.filter(vendor=vendor)
    

    payout_status_map = {payout.item.id: payout.status for payout in payouts if payout.item is not None}

    context={
        'orders':orders,
        'payout_status_map': payout_status_map,
    }
    return render(request,'vendor/orders.html',context)


@vendor_required
def create_product(request):

    categories=base_models.Category.objects.all()

    if request.method=="POST":
        images=request.FILES.getlist("images")
        name=request.POST.get("name")
        category_id=request.POST.get("category_id")
        description=request.POST.get("description")
        start_bid=request.POST.get("start_bid")
        auction_start_time=request.POST.get("auction_start_time")
        auction_end_time=request.POST.get("auction_end_time")
        shipping=request.POST.get("shipping")
        
        category=base_models.Category.objects.get(id=category_id)

        product=base_models.Product.objects.create(
            vendor=request.user,
            name=name,
            category=category,
            description=description,
            start_bid=start_bid,
            auction_start_time=auction_start_time,
            auction_end_time=auction_end_time,
            shipping=shipping,
        )
        product.save()
        for image in images:
            base_models.ProductImage.objects.create(product=product,image=image)

        return redirect("vendor:update_product",product.id)

    
    context={
        "categories":categories
    }
    

    return render(request,"vendor/create_product.html",context)

@vendor_required
def update_product(request, id):
    # Fetch the product to be updated using its ID
    product = get_object_or_404(base_models.Product, id=id)
    product_images=base_models.ProductImage.objects.all()
    categories = base_models.Category.objects.all()


    if request.method == 'POST':
        # Extract data from the POST request
        name = request.POST.get('name')
        description = request.POST.get('description')
        category_id = request.POST.get('category_id')
        start_bid = request.POST.get('start_bid')
        auction_start_time = request.POST.get('auction_start_time')
        auction_end_time = request.POST.get('auction_end_time')
        shipping = request.POST.get('shipping')

        category=base_models.Category.objects.get(id=category_id)


        # Update the product
        product.name = name
        product.description = description
        product.category = category
        product.start_bid = start_bid
        product.auction_start_time = auction_start_time
        product.auction_end_time = auction_end_time
        product.shipping = shipping
        product.save()

        delete_images = request.POST.getlist('delete_images')
        for image_id in delete_images:
            
            base_models.ProductImage.objects.filter(id=image_id).delete()

        # Save new product images
        new_images=request.FILES.getlist('new_images')
        for image in new_images:
            base_models.ProductImage.objects.create(product=product, image=image)

        return redirect('vendor:dashboard') 

    return render(request, 'vendor/update_product.html', {
        'product': product,
        'categories': categories
    })

@csrf_exempt  # Temporarily exempt CSRF for testing (use proper CSRF handling in production)
def delete_image(request, id):
    if request.method == 'POST':
        try:
            image = base_models.ProductImage.objects.get(id=image.id,product__vendor=request.user)
            image.delete()
            return JsonResponse({'status': 'success'})
        except base_models.ProductImage.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Image not found'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


@vendor_required
def delete_product(request,id):
    # Get the product and verify ownership
    product = get_object_or_404(base_models.Product, id=id)
    
    if request.method == 'POST':
        # Delete the product and related images
        product.delete()
        messages.success(request, 'Product deleted successfully!')
        return redirect('vendor:dashboard')
    
    # If not POST, show confirmation page
    return render(request, 'vendor/confirm_delete.html', {'product': product,"Delivery_status": base_models.Order.Delivery_status,})


@vendor_required
def update_order_status(request, product_id):
    # Get the specific order belonging to the vendor
    order = get_object_or_404(
        base_models.Order,
        product__id=product_id,
        product__vendor=request.user,
    )
    product_images = base_models.ProductImage.objects.filter(product=order.product)
    if request.method == "POST":
        delivery_status = request.POST.get("delivery_status")
        if delivery_status in dict(base_models.Order.Delivery_status):
            order.delivery_status = delivery_status
            order.save()

            customer_models.Notification.objects.create(
            user=order.user,
            type=order.delivery_status,
            orders=order,
            seen=False
        )
        return redirect('vendor:dashboard')
    
    return render(request, 'vendor/update_status.html', {'order': order,'Delivery_status': base_models.Order.Delivery_status,'product_images':product_images,})


@vendor_required
def reviews(request):
    reviews=base_models.Review.objects.filter(product__vendor=request.user)
    

    rating=request.GET.get('rating')
    
    sort = request.GET.get('review_time', '-review_time')

    if rating:
        reviews=reviews.filter(rating=rating)

    valid_sorts = ['-review_time', 'review_time']
    if sort in valid_sorts:
        reviews = reviews.order_by(sort)

    context={
        'reviews':reviews
    }
    return render(request,"vendor/reviews.html",context)

@vendor_required
def update_reply(request,id):
    review=base_models.Review.objects.get(id=id)

    if request.method=="POST":
        reply=request.POST.get("reply")

        review.reply=reply
        review.save()
        messages.success(request,"Reply Added")

        return redirect("vendor:reviews")
    
@vendor_required
def notis(request):
    notis=vendor_models.Notification.objects.filter(user=request.user,seen=False)

    context={
        'notis':notis
    }
    return render(request,"vendor/notis.html",context)

@vendor_required
def mark_noti_seen(request,id):
    noti=vendor_models.Notification.objects.get(user=request.user,id=id)
    noti.seen=True
    noti.save()
    messages.success(request,"Notification marked as seen")
    return redirect("vendor:notis")

@vendor_required
def request_payout_for_order(request, order_id):
    

    try:
        order = base_models.Order.objects.get(id=order_id, product__vendor=request.user)
    except base_models.Order.DoesNotExist:
        messages.error(request, "Order not found.")
        return redirect('vendor:orders')  # or your actual order page name

    # Check delivery status
    if order.delivery_status.lower() != 'delivered':
        messages.error(request, "Payout only available after product delivery.")
        return redirect('vendor:orders')

    # Check if payout already requested
    if vendor_models.Payout.objects.filter(item=order).exists():
        messages.error(request, "Payout already requested for this product.")
        return redirect('vendor:orders')

    # Create payout request
    vendor_models.Payout.objects.create(
        vendor=request.user.vendor,
        item=order,
        amount=order.total_price
    )
    messages.success(request, f"Payout request submitted for Order #{order.id}.")
    return redirect('vendor:orders')

@vendor_required
def payouts(request):
    vendor = request.user.vendor
    status = request.GET.get('status', 'pending')  # Default to pending
    
    # Validate status input
    valid_statuses = ['pending', 'approved']
    status = status if status in valid_statuses else 'pending'
    
    payouts = vendor_models.Payout.objects.filter(
        vendor=vendor, 
        status=status
    ).select_related('item__product')
    
    # Get counts for both statuses
    pending_count = vendor_models.Payout.objects.filter(
        vendor=vendor, 
        status='pending'
    ).count()
    
    approved_count = vendor_models.Payout.objects.filter(
        vendor=vendor, 
        status='approved'
    ).count()

    context = {
        'payouts': payouts,
        'current_status': status,
        'pending_count': pending_count,
        'approved_count': approved_count,
    }
    return render(request, 'vendor/payouts.html', context)

@vendor_required
def bank_account(request):
    vendor = request.user.vendor
    try:
        bank_account = vendor_models.BankAccount.objects.get(vendor=vendor)
    except vendor_models.BankAccount.DoesNotExist:
        bank_account = None

    if request.method == "POST":
        bank_name = request.POST.get("bank_name")
        account_number = request.POST.get("account_number")
        account_name = request.POST.get("account_name")

        if bank_account:
            # Update existing account
            bank_account.bank_name = bank_name
            bank_account.account_number = account_number
            bank_account.account_name = account_name
            bank_account.save()
            messages.success(request, "Bank account updated successfully!")
        else:
            # Create new account
            vendor_models.BankAccount.objects.create(
                vendor=vendor,
                bank_name=bank_name,
                account_number=account_number,
                account_name=account_name
            )
            messages.success(request, "Bank account created successfully!")
        
        return redirect("vendor:bank_account")

    context = {
        'bank_account': bank_account
    }
    return render(request, "vendor/bank_account.html", context)