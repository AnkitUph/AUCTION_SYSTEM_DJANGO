from django.urls import path
from .import views

app_name="vendor"

urlpatterns=[
    path("login/",views.vendor_login,name='vendor-login'),
    path("profile/",views.profile,name='profile'),
    path("change_password/",views.change_password,name='change_password'),
    path("dashboard/",views.dashboard,name='dashboard'),
    path("products/",views.products,name='products'),
    path("products_sold/",views.products_sold,name='products_sold'),
    path("orders/",views.orders,name='orders'),
    path("create_product/",views.create_product,name='create_product'),
    path("update_product/<id>/",views.update_product,name='update_product'),
    path("delete_product/<id>/",views.delete_product,name='delete_product'),
    path("update_order_status/<product_id>/",views.update_order_status,name='update_order_status'),
    path("reviews/",views.reviews,name='reviews'),
    path("update_reply/<id>/",views.update_reply,name='update_reply'),

    path("notis/",views.notis,name='notis'),
    path("mark_noti_seen/<id>/",views.mark_noti_seen,name='mark_noti_seen'),

    path('request-payout/<int:order_id>/', views.request_payout_for_order, name='request_payout_for_order'),
    path('payouts/', views.payouts, name='payouts'),
    path('bank-account/', views.bank_account, name='bank_account'),


]