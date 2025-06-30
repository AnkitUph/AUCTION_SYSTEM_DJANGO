from django.urls import path
from .import views

app_name="base"

urlpatterns=[
    path('',views.home,name='home'),
    path('account/',views.account,name='account'),
    path('products/',views.products,name='products'),
    path('category/',views.category_list,name='category_list'),
    path('category_list_product/<slug:slug>/',views.category_list_product,name='category_list_product'),
    path("product_detail/<id>/",views.product_detail,name="product_detail"),
    path("place_bid/<id>/",views.place_bid,name="place_bid"),
    path('search/',views.search_view,name='search'),
    
]