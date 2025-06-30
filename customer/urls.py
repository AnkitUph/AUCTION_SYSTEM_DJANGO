from django.urls import path
from .import views

app_name="customer"

urlpatterns=[
    path("login/",views.customer_login,name='customer-login'),
    path("profile/",views.profile,name='profile'),
    path("change_password/",views.change_password,name='change_password'),
    path("dashboard/",views.dashboard,name='dashboard'),
    path("items_bid/",views.items_bid,name='items_bid'),
    path("items_won/",views.items_won,name='items_won'),
    path("orders/",views.orders,name='orders'),
    path("checkout_view/<product_id>/",views.checkout_view,name='checkout_view'),
    path("wishlist/",views.wishlist,name='wishlist'),
    path("add_to_wishlist/<id>/",views.add_to_wishlist,name='add_to_wishlist'),
    path("remove_from_wishlist/<id>/",views.remove_from_wishlist,name='remove_from_wishlist'),
    path("toggle_wishlist/<id>/", views.toggle_wishlist, name="toggle_wishlist"),

    path("reviews/",views.reviews,name='reviews'),
    path("rate_product/<product_id>/",views.rate_product,name='rate_product'),
    path("update_review/<id>/",views.update_review,name='update_review'),

    path("notis/",views.notis,name='notis'),
    path("mark_noti_seen/<id>/",views.mark_noti_seen,name='mark_noti_seen'),

    path("esewaform/",views.EsewaView.as_view(),name="esewaform"),
    path("esewa_verify/",views.esewa_verify,name="esewa_verify"),

    

    path('khalti_payment/', views.khalti_payment, name='khalti_payment'),
    path('khalti-verify/', views.khalti_verify, name='khalti_verify'),




]