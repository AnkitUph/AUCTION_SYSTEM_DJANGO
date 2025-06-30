from django.core.management.base import BaseCommand
from django.utils.timezone import now
from base.models import Product

class Command(BaseCommand):
    help = "Activates auctions whose start time has passed and end time has not yet passed, and are still inactive."

    def handle(self, *args, **kwargs):
        current_time = now()

        # Only activate products where:
        # - start time has passed
        # - end time has not passed
        # - product is not already active
        to_activate = Product.objects.filter(
            auction_start_time__lte=current_time,
            auction_end_time__gt=current_time,
            is_active=False
        )

        if not to_activate.exists():
            self.stdout.write(self.style.WARNING("No auctions to activate."))
            return

        for product in to_activate:
            product.is_active = True
            product.save()
            self.stdout.write(self.style.SUCCESS(f"Auction activated for: {product.name}"))

        self.stdout.write(self.style.SUCCESS("Auction activation process completed."))
