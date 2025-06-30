from django.contrib import admin
from vendor import models as vendor_models
from django.utils import timezone
from django.utils.timezone import now

class VendorAdmin(admin.ModelAdmin):
    list_display=['store_name','user','vendor_id','date']
    search_fields=['store_name','user__username','vendor_id']
    list_filter=['store_name','date']

class PayoutAdmin(admin.ModelAdmin):
    list_display = ['payout_id', 'vendor', 'item', 'amount', 'status', 'approved_on']
    search_fields = ['payout_id', 'vendor__store_name', 'item__product__name']
    list_filter = ['status', 'vendor']
    readonly_fields = ('approved_on', 'requested_on', 'payout_id')
    actions = ['approve_payouts', 'reject_payouts']

    def save_model(self, request, obj, form, change):
        # Set approved_on automatically when status changes to approved
        if change:
            original = vendor_models.Payout.objects.get(pk=obj.pk)
            if original.status != 'approved' and obj.status == 'approved':
                obj.approved_on = timezone.now()
        else:
            if obj.status == 'approved':
                obj.approved_on = timezone.now()
        super().save_model(request, obj, form, change)

    @admin.action(description="Mark selected payouts as Approved")
    def approve_payouts(self, request, queryset):
        for payout in queryset.filter(status='pending'):
            payout.approve()  # Use model method instead of direct update
        self.message_user(request, f"{queryset.count()} payout(s) approved.")

    @admin.action(description="Mark selected payouts as Rejected")
    def reject_payouts(self, request, queryset):
        for payout in queryset.filter(status='pending'):
            payout.reject("Rejected by admin")
        self.message_user(request, f"{queryset.count()} payout(s) rejected.")


class NotificationAdmin(admin.ModelAdmin):
    list_display=['user','type','order','seen']
    list_editable=['order']

class BankAccountAdmin(admin.ModelAdmin):
    list_display=['vendor','bank_name','account_number']
    search_fields=['vendor__base_name','bank_name','account_number']
    list_filter=['vendor']

admin.site.register(vendor_models.Vendor,VendorAdmin)
admin.site.register(vendor_models.Payout,PayoutAdmin)
admin.site.register(vendor_models.Notification,NotificationAdmin)
admin.site.register(vendor_models.BankAccount,BankAccountAdmin)
