from django.contrib import admin
from userauths import models as user_models

class UserAdmin(admin.ModelAdmin):
    list_display=['username','email'] #list me dekhinxa user page ma admin bhitra
class ProfileAdmin(admin.ModelAdmin):
    list_display=['user','full_name','mobile','user_type','bio']

admin.site.register(user_models.User,UserAdmin),
admin.site.register(user_models.Profile,ProfileAdmin),

