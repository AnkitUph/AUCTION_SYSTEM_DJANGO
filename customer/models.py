from django.db import models
from base import models as base_models
from userauths.models import User
from shortuuid.django_fields import ShortUUIDField
from django.utils.html import format_html
from userauths.models import User
from base import models as base_models
from email.policy import default
from pyexpat import model
from unicodedata import decimal
from django.utils import timezone
from django.utils.text import  slugify
import shortuuid
from django.utils.timezone import now

TYPE=(
    ("New order","New order"),
    ("Item-Shipped","Item-Shipped"),
    ("Item-Delivered","Item-Delivered"),
)



class Address(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    full_name=models.CharField(max_length=200,null=True,blank=True,default=None)
    mobile=models.CharField(max_length=50,null=True,blank=True,default=None)
    email=models.EmailField(null=True,blank=True)
    country=models.CharField(max_length=50,null=True,blank=True,default=None)
    state=models.CharField(max_length=50,null=True,blank=True,default=None)
    city=models.CharField(max_length=50,null=True,blank=True,default=None)

    class Meta:
        verbose_name_plural="Customer Address"

    def __str__(self):
        return self.full_name
    
class Notification(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    type=models.CharField(max_length=100,choices=TYPE,default=None)
    orders=models.ForeignKey("base.Order",on_delete=models.CASCADE,null=True,blank=True)
    seen=models.BooleanField(default=False)
    date=models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural="Notification"

    def __str__(self):
        return self.type

    


