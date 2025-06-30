from django.db import models
from shortuuid.django_fields import ShortUUIDField
from userauths.models import User
from django.utils.text import slugify
import shortuuid
from django.utils import timezone
from django.utils.timezone import now


NOTIFICATION_TYPE=(
    ("New Order","New Order"),
    ("New Review","New Review")
)

TYPE=(
    ("New order","New order"),
    ("Item-Shipped","Item-Shipped"),
    ("Item-Delivered","Item-Delivered"),
)

PAYMENT_METHOD=(
("E-sewa","E-sewa"),
("Khalti","Khalti"),
)

class Vendor(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE,null=True,blank=True,related_name="vendor")
    image=models.ImageField(upload_to='vendor/',default="shop-image.jpg",blank=True)
    store_name=models.CharField(max_length=100,null=True,blank=True)
    description=models.TextField(null=True,blank=True)
    vendor_id=ShortUUIDField(unique=True,length=6,max_length=10,alphabet="1234567890")
    date=models.DateTimeField(auto_now_add=True)
    slug=models.SlugField(blank=True,null=True)

    def __str__(self):
        return str(self.store_name)
    
    def save(self,*args,**kwargs):
        if self.slug=="" or self.slug==None:
            self.slug=slugify(self.store_name)
            super(Vendor,self).save(*args,**kwargs)


class BankAccount(models.Model):
    vendor=models.OneToOneField(Vendor,on_delete=models.SET_NULL,null=True)
    bank_name=models.CharField(max_length=100)
    account_number=models.CharField(max_length=100)
    account_name=models.CharField(max_length=100)

    class Meta:
        verbose_name_plural="Bank Account"
    
    def __str__(self):
        return self.bank_name


class Notification(models.Model):
    NOTIFICATION_TYPE=(
    ("New Order","New Order"),
    ("New Review","New Review")
)
    user=models.ForeignKey(User,on_delete=models.CASCADE,null=True,related_name="vendor_notification")
    type=models.CharField(max_length=100,choices=TYPE,default=None)
    order=models.ForeignKey("base.BidsWon",on_delete=models.CASCADE,null=True,blank=True)
    seen=models.BooleanField(default=False)
    date=models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural="Notification"

    def __str__(self):
        return self.type

class Payout(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE,null=True,blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    item=models.ForeignKey("base.Order",on_delete=models.SET_NULL,null=True)
    requested_on = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payout_id=ShortUUIDField(unique=True,length=6,max_length=10,alphabet="1234567890")
    approved_on = models.DateTimeField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)  # For admin notes like txn ID, etc.

    def approve(self):
        self.status = 'approved'
        self.approved_on = timezone.now()
        self.save()

    def reject(self, remarks=''):
        self.status = 'rejected'
        self.remarks = remarks
        self.save()

    def __str__(self):
        return f"{self.vendor.store_name} - {self.amount} ({self.status})"
