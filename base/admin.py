from django.contrib import admin
from base.models import Category,Product,Review,Bid,BidsHistory,BidsWon,ProductImage,Order,wishlist
from django.utils.html import format_html
from django.utils import timezone
from django.utils.timezone import now
from django import forms

class ProductForm(forms.ModelForm):
    model=Product
    fields='__all__'

    def clean(self):
        cleaned_data=super().clean()
        auction_start_time=cleaned_data.get("auction_start_time")
        auction_end_time=cleaned_data.get("auction_end_time")
        if auction_end_time<=auction_start_time:
            raise forms.ValidationError("End time must be after start time")

class BidInline(admin.TabularInline):
    model=Bid
    extra=0
    readonly_fields=['bidder','bid_amount','bid_time']

class ProductImageInline(admin.TabularInline):
    model=ProductImage

class CategoryAdmin(admin.ModelAdmin):
    list_display=['title','image']
    list_editable=['image']
    prepopulated_fields={'slug':('title',)}

class ProductAdmin(admin.ModelAdmin):
    form=ProductForm
    list_display=['name','category','vendor','auction_start_time','auction_end_time','current_bid','is_active']
    search_fields=['name','category__title']
    list_filter=['category','auction_start_time']
    inlines=[BidInline,ProductImageInline]
    actions=['close_auctions']

class ProductImageAdmin(admin.ModelAdmin):
    list_display=['product']
    search_fields=['product__name']

class BidAdmin(admin.ModelAdmin):
    list_display=['product','bidder','bid_amount','bid_time']
    list_filter=['product','bidder']
    search_fields=['bidder__username','product__name']
    readonly_fields=['bid_time']

class BidsWonAdmin(admin.ModelAdmin):
    list_display=['product','winner','winning_bid','won_time']
    list_filter=['winner','product']
    search_fields=['winner__username','product__name']

class BidsHistoryAdmin(admin.ModelAdmin):
    list_display=['user','product','bid_amount','bid_time']
    list_filter=['user','product']
    search_fields=['user__username','product__name']

class ReviewAdmin(admin.ModelAdmin):
    list_display=['user','product','reply','rating']

class OrderAdmin(admin.ModelAdmin):
    list_display=['user','product','bid_won','payment_method','payment_status','delivery_status']

class wishlistAdmin(admin.ModelAdmin):
    list_display=['user','product']


admin.site.register(Category,CategoryAdmin)
admin.site.register(Product,ProductAdmin)
admin.site.register(ProductImage,ProductImageAdmin)
admin.site.register(Review,ReviewAdmin)
admin.site.register(Bid,BidAdmin)
admin.site.register(BidsWon,BidsWonAdmin)
admin.site.register(BidsHistory,BidsHistoryAdmin)
admin.site.register(Order,OrderAdmin)
admin.site.register(wishlist,wishlistAdmin)