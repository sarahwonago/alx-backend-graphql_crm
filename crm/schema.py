import decimal
import re
from typing import List, Tuple

import graphene
from graphene_django import DjangoObjectType
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError, ObjectDoesNotExist

from .models import Customer, Product, Order


# ----------------------
# GraphQL Types
# ----------------------
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone")


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "price", "stock")


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ("id", "customer", "products", "total_amount", "order_date")


# ----------------------
# Input Objects
# ----------------------
class CreateCustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String(required=False)


class CreateProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Float(
        required=True
    )  # accept float from clients; convert to Decimal
    stock = graphene.Int(required=False, default_value=0)


class CreateOrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.NonNull(graphene.ID), required=True)
    order_date = graphene.DateTime(required=False)


# ----------------------
# Validators / Helpers
# ----------------------
PHONE_RE = re.compile(r"^(\+\d{7,15}|\d{3}-\d{3}-\d{4})$")


def validate_phone(phone: str) -> bool:
    if phone in (
        None,
        "",
    ):
        return True
    return bool(PHONE_RE.match(phone))


def ensure_unique_email(email: str):
    if Customer.objects.filter(email=email).exists():
        raise ValidationError("Email already exists")


def parse_decimal(value, field_name="value") -> decimal.Decimal:
    try:
        d = decimal.Decimal(str(value))
    except Exception:
        raise ValidationError(f"{field_name} must be a valid number")
    return d


# ----------------------
# Mutations
# ----------------------
class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CreateCustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()
    errors = graphene.List(graphene.String)

    @staticmethod
    def mutate(root, info, input: CreateCustomerInput):
        errors = []

        # Basic validation
        if not validate_phone(input.get("phone")):
            errors.append("Invalid phone format. Use +1234567890 or 123-456-7890.")

        try:
            ensure_unique_email(input["email"])
        except ValidationError as e:
            errors.append(str(e))

        if errors:
            return CreateCustomer(
                customer=None, message="Failed to create customer", errors=errors
            )

        customer = Customer.objects.create(
            name=input["name"],
            email=input["email"],
            phone=input.get("phone") or None,
        )
        return CreateCustomer(
            customer=customer, message="Customer created successfully", errors=[]
        )


class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(graphene.NonNull(CreateCustomerInput), required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    @staticmethod
    def mutate(root, info, input: List[CreateCustomerInput]):
        created: List[Customer] = []
        errors: List[str] = []

        # Single DB transaction with savepoints per item:
        with transaction.atomic():
            for idx, item in enumerate(input, start=1):
                sid = transaction.savepoint()
                try:
                    if not item.get("name"):
                        raise ValidationError("Name is required")
                    if not item.get("email"):
                        raise ValidationError("Email is required")
                    if not validate_phone(item.get("phone")):
                        raise ValidationError(
                            "Invalid phone format. Use +1234567890 or 123-456-7890."
                        )
                    ensure_unique_email(item["email"])

                    c = Customer.objects.create(
                        name=item["name"],
                        email=item["email"],
                        phone=item.get("phone") or None,
                    )
                    created.append(c)
                    transaction.savepoint_commit(sid)
                except ValidationError as e:
                    transaction.savepoint_rollback(sid)
                    errors.append(f"Row {idx}: {str(e)}")
                except Exception as e:
                    transaction.savepoint_rollback(sid)
                    errors.append(f"Row {idx}: {str(e)}")

        return BulkCreateCustomers(customers=created, errors=errors)


class CreateProduct(graphene.Mutation):
    class Arguments:
        input = CreateProductInput(required=True)

    product = graphene.Field(ProductType)
    errors = graphene.List(graphene.String)

    @staticmethod
    def mutate(root, info, input: CreateProductInput):
        errors = []

        price = parse_decimal(input["price"], "price")
        if price <= 0:
            errors.append("Price must be positive.")

        stock = input.get("stock", 0)
        if stock is None:
            stock = 0
        if stock < 0:
            errors.append("Stock cannot be negative.")

        if errors:
            return CreateProduct(product=None, errors=errors)

        product = Product.objects.create(
            name=input["name"],
            price=price,
            stock=stock,
        )
        return CreateProduct(product=product, errors=[])


class CreateOrder(graphene.Mutation):
    class Arguments:
        input = CreateOrderInput(required=True)

    order = graphene.Field(OrderType)
    errors = graphene.List(graphene.String)

    @staticmethod
    def mutate(root, info, input: CreateOrderInput):
        errors: List[str] = []
        # Validate customer
        try:
            customer = Customer.objects.get(pk=input["customer_id"])
        except ObjectDoesNotExist:
            errors.append("Invalid customer ID.")
            return CreateOrder(order=None, errors=errors)

        product_ids = input.get("product_ids") or []
        if not product_ids:
            errors.append("At least one product must be selected.")
            return CreateOrder(order=None, errors=errors)

        # Fetch products and check all exist
        products = list(Product.objects.filter(pk__in=product_ids))
        missing = set(map(str, product_ids)) - set(str(p.pk) for p in products)
        if missing:
            errors.append(f"Invalid product ID(s): {', '.join(sorted(missing))}")
            return CreateOrder(order=None, errors=errors)

        with transaction.atomic():
            # Calculate total amount accurately using Decimal
            total = sum((p.price for p in products), decimal.Decimal("0.00"))
            order_date = input.get("order_date") or timezone.now()
            order = Order.objects.create(
                customer=customer,
                total_amount=total,
                order_date=order_date,
            )
            order.products.add(*products)

        return CreateOrder(order=order, errors=[])


# ----------------------
# Query (simple)
# ----------------------
class Query(graphene.ObjectType):
    customers = graphene.List(CustomerType)
    products = graphene.List(ProductType)
    orders = graphene.List(OrderType)

    customer = graphene.Field(CustomerType, id=graphene.ID(required=True))
    product = graphene.Field(ProductType, id=graphene.ID(required=True))
    order = graphene.Field(OrderType, id=graphene.ID(required=True))

    def resolve_customers(root, info):
        return Customer.objects.all()

    def resolve_products(root, info):
        return Product.objects.all()

    def resolve_orders(root, info):
        return (
            Order.objects.select_related("customer").prefetch_related("products").all()
        )

    def resolve_customer(root, info, id):
        return Customer.objects.get(pk=id)

    def resolve_product(root, info, id):
        return Product.objects.get(pk=id)

    def resolve_order(root, info, id):
        return (
            Order.objects.select_related("customer")
            .prefetch_related("products")
            .get(pk=id)
        )


# ----------------------
# Root Mutation
# ----------------------
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
