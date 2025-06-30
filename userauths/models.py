from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

USER_TYPE=(
    ("Vendor","Vendor"),
    ("Customer","Customer"),
)

class User(AbstractUser):
    username=models.CharField(max_length=20,null=True,blank=True)
    email=models.EmailField(unique=True,null=False)# null =false means email must be provided
    

    USERNAME_FIELD='email'#instead of using username to login we will use email

    REQUIRED_FIELDS=['username'] # we want username along with email and password while creating superuser
    def __str__(self):
        return self.email
    def save(self,*args,**kwargs):
        email_username,_=self.email.split('@')
        if not self.username:
            self.username=email_username
        super(User,self).save(*args,**kwargs)

    
class Profile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    image=models.ImageField(upload_to="image/",default="default-user.jpg",null=True,blank=True)
    full_name=models.CharField(max_length=255,null=True,blank=True) # full name can be empty
    mobile=models.CharField(max_length=255,null=True,blank=True)
    user_type=models.CharField(max_length=255,choices=USER_TYPE,null=True,blank=True,default=None)
    bio=models.CharField(max_length=100,default="")

    def __str__(self):
        return self.user.username
    
    def save(self,*args,**kwargs):
        if not self.full_name:
            self.full_name=self.user.username
        super(Profile,self).save(*args,**kwargs)

