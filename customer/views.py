from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from base import models as base_models
from customer import models as customer_models
from django.db import models
from django.contrib import messages
from django.http import JsonResponse
from django.utils.text import slugify
from django.conf import settings
from base.decorators import vendor_required
from django.contrib.auth import authenticate, login,update_session_auth_hash
from django.contrib.messages import WARNING
from userauths import models as userauths_models
from vendor import models as vendor_models
from decimal import Decimal
from django.utils import timezone
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
import json
from base.decorators import customer_required
from django.urls import reverse
import hmac
import hashlib
import uuid
import base64
from django.views import View
from django.views.decorators.csrf import csrf_exempt
import requests
from django.shortcuts import render
from django.contrib.auth.hashers import check_password



def customer_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user = userauths_models.User.objects.get(email=email)
        except:
            messages.warning(request, f"User with {email} doesn't exist")
            return redirect("customer:login")  # Redirect to login page

        user = authenticate(request, email=email, password=password)

        if user is not None:
            # Check if the user has a profile before accessing it
            if hasattr(user, 'profile') and user.profile.user_type == "Customer":
                login(request, user)
                return redirect("customer:dashboard")  # Redirect to vendor dashboard
            else:
                messages.warning(request, "You are logged in as a customer. Please log in as a vendor.")
                return redirect("customer:customer-login")
        else:
            messages.error(request, "Invalid credentials or not a vendor account.")

    context = {}
    return render(request, "customer/login.html", context)

@customer_required
def dashboard(request):
    items_bid = base_models.Product.objects.filter(id__in=base_models.Bid.objects.filter(bidder=request.user).values_list('product', flat=True).distinct())
    items_won = base_models.Product.objects.filter(id__in=base_models.BidsWon.objects.filter(winner=request.user).values_list('product', flat=True).distinct())
    bid_amount=base_models.BidsWon.objects.filter(winner=request.user).aggregate(total=models.Sum('winning_bid'))['total']
    shipping_amount=base_models.BidsWon.objects.filter(winner=request.user).aggregate(total=models.Sum('product__shipping'))['total']
    notis=customer_models.Notification.objects.filter(user=request.user,seen=False)
    reviews=base_models.Review.objects.filter(user=request.user)
    wishlist=base_models.wishlist.objects.filter(user=request.user)
    total_spent=base_models.Order.objects.filter(user=request.user).aggregate(total=models.Sum('total_price'))['total']
    order=base_models.Product.objects.filter(id__in=base_models.Order.objects.filter(user=request.user).values_list('product', flat=True).distinct())
    

    context={
        'items_bid':items_bid,
        'items_won':items_won,
        'notis':notis,
        'bid_amount':bid_amount,
        'shipping_amount':shipping_amount,
        'total_spent':total_spent,
        'reviews':reviews,
        'wishlist':wishlist,
        'order':order,
    }
    return render(request,"customer/dashboard.html",context)


@customer_required
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
        return redirect("customer:profile")
    
    context={
        "profile":profile
    }
    return render(request,"customer/profile.html",context)

@customer_required
def change_password(request):
    user=request.user

    if request.method=="POST":
        old_password=request.POST.get("old_password")
        new_password=request.POST.get("new_password")
        confirm_new_password=request.POST.get("confirm_new_password")

        if confirm_new_password!=new_password:
            messages.error(request,"Password doesn't match")
            return redirect("customer:change_password")
        
        if check_password(old_password,user.password):
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request,user)#keeps user logged in 
            messages.success(request,"Password changed Succesfully")
            return redirect("customer:profile")
        else:
            messages.error(request,"Old password is incorrect")
            return redirect("customer:change_password")
        
    return render(request, "customer/change_password.html")

@customer_required
def items_bid(request):
    items_bid = base_models.Product.objects.filter(id__in=base_models.Bid.objects.filter(bidder=request.user).values_list('product', flat=True).distinct())

    context={
        'items_bid':items_bid
    }

    return render(request,"customer/items_bid.html",context)

@customer_required
def items_won(request):
    items_won = base_models.Product.objects.filter(id__in=base_models.BidsWon.objects.filter(winner=request.user).values_list('product', flat=True).distinct())


    context={
        'items_won':items_won
    }

    return render(request,"customer/items_won.html",context)

@customer_required
def orders(request):
    orders=base_models.Order.objects.filter(user=request.user).select_related('product')
    context={
        'orders':orders,
    }
    return render(request,'customer/orders.html',context)

@customer_required
def wishlist(request): #list of product added to wishlist
    wishlist_list=base_models.Product.objects.filter(id__in=base_models.wishlist.objects.filter(user=request.user).values_list('product', flat=True).distinct())

    context={
        'wishlist_list':wishlist_list
    }
    return render(request,"customer/wishlist.html",context)

@customer_required
def remove_from_wishlist(request,id):
    wishlist_item = base_models.wishlist.objects.filter(user=request.user, product_id=id).first()
    if wishlist_item:
        wishlist_item.delete()
        messages.success(request, "Item removed from wishlist")
        return redirect('customer:dashboard')  # Ensure 'wishlist' is correctly defined in urls.py
    else:
        messages.error(request, "Item not found in wishlist")
        return redirect('customer:wishlist')
    
def add_to_wishlist(request,id):
    if request.user.is_authenticated:
        product=base_models.Product.objects.get(id=id)
        wishlist_exists=base_models.wishlist.objects.filter(product=product,user=request.user).first()

        if not wishlist_exists:
            base_models.wishlist.objects.create(user=request.user,product=product)

        wishlist=base_models.wishlist.objects.filter(user=request.user)
        return JsonResponse({"message":"Item added to wishlist","wishlist_count":wishlist.count()})
    else:
        return JsonResponse({"message":"User is not logged in","wishlist_count":'0'})

def toggle_wishlist(request,id):
    """Add or remove a product from the wishlist"""
    if not request.user.is_authenticated:
        return JsonResponse({"message": "Login required", "wishlist_count": "0"}, status=401)
    user = request.user
    product = base_models.Product.objects.get(id=id)

    wishlist_item, created = base_models.wishlist.objects.get_or_create(user=user, product=product)

    if not created:
        wishlist_item.delete()
        return JsonResponse({"message": "Item removed from wishlist", "wishlist_count": base_models.wishlist.objects.filter(user=user).count()})
    
    return JsonResponse({"message": "Item added to wishlist", "wishlist_count": base_models.wishlist.objects.filter(user=user).count()})

@customer_required
def reviews(request):#see list of product reviewed
    reviews=base_models.Review.objects.filter(user=request.user)

    rating=request.GET.get('rating')
    
    sort = request.GET.get('review_time', '-review_time')

    if rating:
        reviews=reviews.filter(rating=rating)

    valid_sorts = ['-review_time', 'review_time']
    if sort in valid_sorts:
        reviews = reviews.order_by(sort)

    context={
        'reviews':reviews,
    }
    return render(request,"customer/reviews.html",context)

    
@customer_required
def rate_product(request,product_id):
    product = get_object_or_404(base_models.Product, id=product_id)
    bidswon = get_object_or_404(base_models.BidsWon, product=product, winner=request.user)

    existing_review = base_models.Review.objects.filter(user=request.user,product=product).first()

    if request.method == "POST":
        rating = request.POST.get("rating")
        review_text = request.POST.get("review_text")

        # Validate rating
        if not rating or not rating.isdigit():
            messages.error(request, "Please select a valid rating")
            return redirect('customer:rate_product', id=id)

        rating = int(rating)
        
        # Update or create review
        if existing_review:
            existing_review.rating = rating
            existing_review.review = review_text
            existing_review.save()
            messages.success(request, "Review updated successfully!")

        else:
            base_models.Review.objects.create(
                user=request.user,
                product=product,
                rating=rating,
                review=review_text
            )
            messages.success(request, "Thank you for your review!")
            vendor_models.Notification.objects.create(
            user=product.vendor,
            type="New Review",
            order=bidswon,
            seen=False
        )

        return redirect('customer:dashboard')

    context = {
        'product': product,
        'existing_review': existing_review,
    }
    return render(request, 'customer/rate_product.html', context)

@customer_required
def update_review(request,id):
    review=base_models.Review.objects.get(id=id,user=request.user)
    

    if request.method=="POST":
        review_text=request.POST.get("review_text")
        rating = request.POST.get("rating")

        if review:
            review.review=review_text

        if rating:
            review.rating = int(rating)

        review.save()
        

        messages.success(request,"Review Added")
        return redirect("customer:reviews")

@customer_required
def notis(request):
    notis=customer_models.Notification.objects.filter(user=request.user,seen=False)

    context={
        'notis':notis
    }
    return render(request,"customer/notis.html",context)

@customer_required
def mark_noti_seen(request,id):
    noti=customer_models.Notification.objects.get(user=request.user,id=id)
    noti.seen=True
    noti.save()
    messages.success(request,"Notification marked as seen")
    return redirect("customer:notis")

@customer_required
def checkout_view(request, product_id):
    product = get_object_or_404(base_models.Product, id=product_id)
    bidswon = get_object_or_404(base_models.BidsWon, product=product, winner=request.user)

    # Check if the product is already ordered
    if base_models.Order.objects.filter(product=product, user=request.user).exists():
        messages.info(request, "You have already checked out this product.")
        return redirect("customer:dashboard")

    # Get user's addresses
    addresses = customer_models.Address.objects.filter(user=request.user)
    payment_methods = base_models.Order._meta.get_field('payment_method').choices

    if request.method == "POST":
        address_id = request.POST.get("address_id")
        payment_method = request.POST.get("payment_method")
        new_address_checkbox = request.POST.get("new_address")  # Checkbox for new address

        if not payment_method:
            messages.error(request, "Please select a payment method.")
            return redirect("checkout_view", product_id=product.id)
        
        address = None


        # If "Add New Address" is selected, update the existing address instead of creating a new one
        if new_address_checkbox:
            full_name = request.POST.get("full_name")
            mobile = request.POST.get("mobile")
            email = request.POST.get("email")
            country = request.POST.get("country")
            state = request.POST.get("state")
            city = request.POST.get("city")

            if not (full_name and mobile and email and country and state and city):
                messages.error(request, "Please fill all address fields.")
                return redirect("checkout_view", product_id=product.id)

            # Check if the user has an existing address, update the first one found
            address,created = customer_models.Address.objects.get_or_create(user=request.user)
            address.full_name = full_name
            address.mobile = mobile
            address.email = email
            address.country = country
            address.state = state
            address.city = city
            address.save()
        elif address_id:  # If an existing address is selected
            address = get_object_or_404(customer_models.Address, id=address_id, user=request.user)
        else:
            messages.error(request, "Please select or add an address.")
            return redirect("customer:checkout_view", product_id=product.id)

        # Create an order
        
        if payment_method=="Cash":
            order=base_models.Order.objects.create(
            user=request.user,
            product=product,
            bid_won=bidswon,
            order_date=timezone.now(),
            total_price=Decimal(bidswon.winning_bid) + Decimal(product.shipping),
            address=address,
            payment_method=payment_method,
            delivery_status="processing",
        )
            vendor_models.Notification.objects.create(
            user=product.vendor,
            type="New Order",
            order=bidswon,
            seen=False
        )
            messages.success(request, "Order placed successfully!")
            return redirect("customer:dashboard")

        elif payment_method == "E-sewa":
    # Store checkout details in session temporarily
            request.session['checkout'] = {
                'product_id': product.id,
                'bidswon_id': bidswon.id,
                'address_id': address.id,
                'total_price': str(Decimal(bidswon.winning_bid) + Decimal(product.shipping)),
                }
            return redirect(reverse('customer:esewaform'))
        

        elif payment_method == "Khalti":
            request.session['checkout'] = {
                'product_id': product.id,
                'bidswon_id': bidswon.id,
                'address_id': address.id,
                'total_price': str(Decimal(bidswon.winning_bid) + Decimal(product.shipping)),
            }
            return redirect(reverse('customer:khalti_payment'))
        
        else:
            messages.ERROR(request,"Invalid payment option")
            return redirect("customer:items_won")

 

    return render(request, "customer/checkout.html", {"product": product, "addresses": addresses,'payment_methods':payment_methods,'bidswon':bidswon})

class EsewaView(View):
    def get(self, request, *args, **kwargs):
        checkout_data = request.session.get('checkout')
        if not checkout_data:
            messages.error(request, "Session expired or invalid access.")
            return redirect("customer:items_won")

        uuid_val = uuid.uuid4()

        total_price = checkout_data['total_price']
        def genSha256(key, message):
            key = key.encode('utf-8')
            message = message.encode('utf-8')
            hmac_sha256 = hmac.new(key, message, hashlib.sha256)
            return base64.b64encode(hmac_sha256.digest()).decode('utf-8')

        secret_key = '8gBm/:&EnhH.1/q'
        data_to_sign = f"total_amount={total_price},transaction_uuid={uuid_val},product_code=EPAYTEST"
        signature = genSha256(secret_key, data_to_sign)

        data = {
            'amount': total_price,
            'total_amount': total_price,
            'transaction_uuid': uuid_val,
            'product_code': 'EPAYTEST',
            'signature': signature,
        }

        return render(request, 'customer/esewa_payment.html', {'data': data,})

def esewa_verify(request):
    if request.method == "GET":
        data = request.GET.get('data')
        decoded_data = base64.b64decode(data).decode('utf-8')
        map_data = json.loads(decoded_data)

        if map_data.get('status') == 'COMPLETE':
            checkout_data = request.session.get('checkout')
            if not checkout_data:
                messages.error(request, "Session expired or invalid access.")
                return redirect("customer:items_won")

            product = get_object_or_404(base_models.Product, id=checkout_data['product_id'])
            bidswon = get_object_or_404(base_models.BidsWon, id=checkout_data['bidswon_id'])
            address = get_object_or_404(customer_models.Address, id=checkout_data['address_id'])

            order = base_models.Order.objects.create(
                user=request.user,
                product=product,
                bid_won=bidswon,
                order_date=timezone.now(),
                total_price=Decimal(checkout_data['total_price']),
                address=address,
                payment_method="E-sewa",
                delivery_status="processing",
                payment_status="Completed"
            )

            vendor_models.Notification.objects.create(
                user=product.vendor,
                type="New Order",
                order=bidswon,
                seen=False
            )

            # Clear session data
            del request.session['checkout']
            messages.success(request, "Order placed successfully!")
            return redirect("customer:dashboard")

        else:
            messages.error(request, "Payment failed. Please try again.")
            return redirect("customer:items_won")

@customer_required
def khalti_payment(request):
    checkout_data = request.session.get('checkout')
    if not checkout_data:
        messages.error(request, "Session expired")
        return redirect("customer:items_won")

    total_price = Decimal(checkout_data['total_price'])
    amount_in_paisa = int(total_price * 100)  # Khalti accepts paisa
    purchase_order_id = str(checkout_data['bidswon_id'])

    return_url = request.build_absolute_uri(reverse('customer:khalti_verify'))


    # Initiate Khalti checkout
    payload = {
        "return_url": return_url,
        "website_url": "http://127.0.0.1:8000/",  # ✅ Replace with your production domain in live
        "amount": amount_in_paisa,
        "purchase_order_id": purchase_order_id,
        "purchase_order_name": "Auction Payment",
        

    }

    headers = {
        "Authorization": f"Key {settings.KHALTI_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(settings.KHALTI_INITIATE_URL, json=payload, headers=headers)
        response_data = response.json()

        if response.status_code == 200 and 'payment_url' in response_data:
            return redirect(response_data['payment_url'])
        else:
            error_msg = response_data.get('detail', 'Khalti payment initiation failed')
            messages.error(request, f"Khalti Error: {error_msg}")
    except Exception as e:
        messages.error(request, f"Connection Error: {str(e)}")

    return redirect("customer:items_won")

@csrf_exempt
def khalti_verify(request):
    pidx = request.GET.get('pidx')
    purchase_order_id = request.GET.get('purchase_order_id')
    
    
    if not pidx or not purchase_order_id:
        messages.error(request, "Invalid Khalti callback parameters")
        return redirect("customer:items_won")

    try:
        # Call Khalti Lookup API to verify the transaction
        headers = {
            "Authorization": f"Key {settings.KHALTI_SECRET_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "pidx": pidx
        }

        response = requests.post(
            settings.KHALTI_LOOKUP_URL,  
            json=payload,
            headers=headers
        )
        response_data = response.json()

        if response.status_code == 200 and response_data.get('status') == 'Completed':
            # Payment successful
            checkout_data = request.session.get('checkout')
            if not checkout_data or str(checkout_data['bidswon_id']) != purchase_order_id:
                messages.error(request, "Session mismatch or expired")
                return redirect("customer:items_won")

            # Create order
            product = get_object_or_404(base_models.Product, id=checkout_data['product_id'])
            bidswon = get_object_or_404(base_models.BidsWon, id=checkout_data['bidswon_id'])
            address = get_object_or_404(customer_models.Address, id=checkout_data['address_id'])

            base_models.Order.objects.create(
                user=request.user,
                product=product,
                bid_won=bidswon,
                order_date=timezone.now(),
                total_price=Decimal(checkout_data['total_price']),
                address=address,
                payment_method="Khalti",
                delivery_status="processing",
                payment_status="Completed"
            )

            # Notify vendor
            vendor_models.Notification.objects.create(
                user=product.vendor,
                type="New Order",
                order=bidswon,
                seen=False
            )

            del request.session['checkout']
            messages.success(request, "Khalti Payment successful! Order placed.")
            return redirect("customer:dashboard")

        else:
            error_msg = response_data.get('detail', 'Payment verification failed')
            messages.error(request, f"Khalti Error: {error_msg}")
    except Exception as e:
        messages.error(request, f"Verification Error: {str(e)}")

    return redirect("customer:items_won")
