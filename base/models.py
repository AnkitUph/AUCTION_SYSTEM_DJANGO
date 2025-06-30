from django.db import models
from shortuuid.django_fields import ShortUUIDField
from django.utils.html import format_html
from userauths.models import User
from email.policy import default
from pyexpat import model
from unicodedata import decimal
from django.utils import timezone
from django.utils.text import  slugify
import shortuuid
from django.utils.timezone import now
from userauths import models as user_models
from customer import models as customer_models
from vendor import models as vendor_models
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.apps import apps



RATING=(
(1,"⭐ ☆ ☆ ☆ ☆"),
(2,"⭐⭐ ☆ ☆ ☆"),
(3,"⭐⭐⭐ ☆ ☆"),
(4,"⭐⭐⭐⭐ ☆"),
(5,"⭐⭐⭐⭐⭐"),

)

def user_directory_path(instance,filename):
    return 'user_{0}/{1}'.format(instance.user.id,filename)

class Category(models.Model):
    slug=models.SlugField(null=True,blank=True)
    title=models.CharField(max_length=100) #title,heading
    image=models.ImageField(upload_to="category/",default="category.jpg")

    class Meta:
        verbose_name_plural="categories"  #want to see categories in admin section instead of category

    def category_image(self):
        if self.image:
            return f'<img src="{self.image.url}" style="width:50px; height:50px;" />'
        return "No Image"
    category_image.allow_tags = True  # For HTML rendering in Django < 2.0
    category_image.short_description = "Image"

    def __str__(self):
        return self.title

class Product(models.Model):
    name=models.CharField(max_length=100) #title,heading
    description=models.TextField(null=True,blank=True,default="This is the product")

    category=models.ForeignKey(Category,on_delete=models.SET_NULL,null=True)

    vendor=models.ForeignKey(user_models.User,on_delete=models.CASCADE)
    sku=ShortUUIDField(unique=True,length=5,max_length=10,prefix="sku" ,alphabet='abcdef123456') #generate id for product
    slug=models.SlugField(null=True,blank=True)


    auction_start_time=models.DateTimeField(null=True,blank=True)
    auction_end_time=models.DateTimeField(null=True,blank=True)
    is_active=models.BooleanField(default=False)
    start_bid=models.DecimalField(max_digits=12,decimal_places=2,default="0.00",null=True,blank=True)
    current_bid=models.DecimalField(max_digits=12,decimal_places=2,default="0.00",null=True,blank=True)


    
    shipping=models.DecimalField(max_digits=12,decimal_places=2,default=0.00,null=True,blank=True,verbose_name="Shipping-Price")


    class Meta:
        verbose_name_plural="Products"  #want to see categories in admin section instead of category
        ordering=['-id']# we see products in order based on product sku

    def wishlist(self,user):
        return wishlist.objects.filter(product=self,user=user)


   
    def __str__(self):
        return self.name
    
    def product_image(self):
        if self.image:
            return f'<img src="{self.image.url}" style="width:50px; height:50px;" />'
        return "No Image"
    product_image.allow_tags = True  # For HTML rendering in Django < 2.0
    product_image.short_description = "Image"
    
    

    

    def average_rating(self):
        return Review.objects.filter(product__vendor=self.vendor,product__isnull=False).aggregate(avg_rating=models.Avg('rating'))['avg_rating']

    def reviews(self):
        return Review.objects.filter(product=self)

    def get_vendor_reviews(self):
        return Review.objects.filter(product__vendor=self.vendor, product__isnull=False)
    
    

    def save(self,*args,**kwargs):
        if not self.slug:
            self.slug=slugify(self.name)
        super(Product,self).save(*args,**kwargs)
        

    def clean(self):
        if self.auction_end_time<=self.auction_start_time:
            raise ValidationError("End time must be after start time")
        
class ProductImage(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE,related_name="images",null=True,blank=True)
    image=models.ImageField(upload_to="Products/",default="product.jpg",null=True,blank=True)
    product_image_id=ShortUUIDField(max_length=100,null=True,blank=True) 

    def __str__(self):
        return f"Image for {self.product.name}"
    
    def product_image(self):
        if self.image:
            return f'<img src="{self.image.url}" style="width:50px; height:50px;" />'
        return "No Image"
    product_image.allow_tags = True  # For HTML rendering in Django < 2.0
    product_image.short_description = "Image"

class Bid(models.Model):
    product=models.ForeignKey(Product,on_delete=models.SET_NULL,related_name='bids',null=True,blank=True)
    bidder=models.ForeignKey(user_models.User,on_delete=models.CASCADE,null=True,blank=True,related_name="buyer")
    bid_amount=models.DecimalField(max_digits=12,decimal_places=2,default="0.00",null=True,blank=True)
    bid_time=models.DateTimeField(default=timezone.now)
    bid_id=ShortUUIDField(unique=True,length=5,max_length=10,prefix="bid" ,alphabet='123456') 


    def __str__(self):
        return f"{self.bidder.username} bid {self.bid_amount} on {self.product.name if self.product else "unknown product"}"
    


    def save(self,*args,**kwargs):
        is_new=self.bid_id
        super().save(*args,**kwargs)
        if not is_new:
            if self.product.current_bid is None or Decimal(self.bid_amount)>Decimal(self.product.current_bid):
                self.product.current_bid=self.bid_amount
                self.product.save(update_fields=['current_bid'])

class BidsWon(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE,related_name='bids_won')
    winner=models.ForeignKey(user_models.User,on_delete=models.CASCADE)
    winning_bid=models.DecimalField(max_digits=12,decimal_places=2)
    won_time=models.DateTimeField(default=timezone.now)
    

    def __str__(self):
        return f"{self.winner.username} won {self.product.name} with {self.winning_bid}"

class BidsHistory(models.Model):
    user=models.ForeignKey(user_models.User,on_delete=models.CASCADE,related_name="bids_history")
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    bid_amount=models.DecimalField(max_digits=12,decimal_places=2)
    bid_time=models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} bid {self.bid_amount} on {self.product.name}"

class Review(models.Model):
    user=models.ForeignKey(user_models.User,on_delete=models.SET_NULL,blank=True,null=True)
    product=models.ForeignKey(Product,on_delete=models.SET_NULL,blank=True,null=True)
    review=models.TextField(null=True,blank=True)
    reply=models.TextField(null=True,blank=True)
    rating=models.IntegerField(choices=RATING,default=None)
    review_time=models.DateTimeField(default=timezone.now)


    class Meta:
        verbose_name_plural="Reviews"
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username} review on {self.product.name}"
    
class wishlist(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    product=models.ForeignKey(Product,on_delete=models.CASCADE,null=True,blank=True)

    class Meta:
        verbose_name_plural="Wishlist"

    def __str__(self):
        if self.product.name:
            return self.product.name
        else:
            return "Wishlist"


class Order(models.Model):
    Delivery_status=(
    ("processing","Processing"),
    ("shipped","Shipped"),
    ("delivered","Delivered"),
)
    Payment_method=(
    ("E-sewa","E-sewa"),
    ("Khalti","Khalti"),
    ("Cash","Cash"),
)

    user = models.ForeignKey(user_models.User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    bid_won=models.ForeignKey(BidsWon,on_delete=models.CASCADE,null=True,blank=True)
    order_date = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    address = models.ForeignKey(customer_models.Address,on_delete=models.CASCADE,null=True,blank=True)
    payment_method = models.CharField(choices=Payment_method,default=None,max_length=100)
    payment_status=models.CharField(default="Pending",max_length=200)
    delivery_status=models.CharField(choices=Delivery_status,default="processing",max_length=100)

    def __str__(self):
        return f"Order {self.id} - {self.product.name} - {self.delivery_status}"





 