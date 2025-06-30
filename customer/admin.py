from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from customer.models import Notification,Address

class AddressAdmin(admin.ModelAdmin):
    list_display=['user','full_name']


class NotificationAdmin(admin.ModelAdmin):
    list_display=['user','type','seen','date']

admin.site.register(Address,AddressAdmin),
admin.site.register(Notification,NotificationAdmin),
