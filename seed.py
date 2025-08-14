import os
import django
from decimal import Decimal

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alx_backend_graphql_crm.settings")
django.setup()

from crm.models import Customer, Product, Order
from django.utils import timezone


def run():
    # Customers
    alice, _ = Customer.objects.get_or_create(
        name="Alice", email="alice@example.com", phone="+1234567890"
    )
    bob, _ = Customer.objects.get_or_create(
        name="Bob", email="bob@example.com", phone="123-456-7890"
    )

    # Products
    laptop, _ = Product.objects.get_or_create(
        name="Laptop", defaults={"price": Decimal("999.99"), "stock": 10}
    )
    mouse, _ = Product.objects.get_or_create(
        name="Mouse", defaults={"price": Decimal("19.99"), "stock": 200}
    )

    # One sample order
    order = Order.objects.create(
        customer=alice, total_amount=Decimal("0.00"), order_date=timezone.now()
    )
    order.products.add(laptop, mouse)
    order.total_amount = laptop.price + mouse.price
    order.save()

    print("Seed complete.")
    print(
        f"Customers: {Customer.objects.count()}, Products: {Product.objects.count()}, Orders: {Order.objects.count()}"
    )


if __name__ == "__main__":
    run()
