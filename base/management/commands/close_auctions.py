
from django.core.management.base import BaseCommand
from django.utils.timezone import now
from base.models import Product, Bid, BidsWon  # Adjust model imports if needed

class Command(BaseCommand):
    help = "Closes auctions for products whose end time has passed and records the highest bid in Bidswon."

    def handle(self, *args, **kwargs):
        # Fetch products whose auction end time has passed and are still active
        expired_products = Product.objects.filter(auction_end_time__lte=now(), is_active=True)

        if not expired_products.exists():
            self.stdout.write(self.style.WARNING("No expired auctions found."))
            return

        for product in expired_products:
            print(f"Processing product: {product}")  # Debugging

            # Get the highest bid for the product
            highest_bid = Bid.objects.filter(product=product).order_by('-bid_amount').first()

            if not highest_bid:
                self.stdout.write(self.style.WARNING(f"No bids found for {product.name}."))
                continue

            # Store the winning bid details in Bidswon
            BidsWon.objects.create(
                product=product,
                winner=highest_bid.bidder,
                winning_bid=highest_bid.bid_amount
            )

            self.stdout.write(self.style.SUCCESS(
                f"Auction closed for {product.name}, winner: {highest_bid.bidder.username}, bid: {highest_bid.bid_amount}"
            ))

            # Mark the product auction as closed
            product.is_active = False
            product.save()

        self.stdout.write(self.style.SUCCESS("Auction closing process completed."))
