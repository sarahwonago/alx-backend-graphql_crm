import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.db import transaction
from django.core.exceptions import ValidationError
from django.db import IntegrityError
import re
from .models import Customer, Product, Order
from .filters import CustomerFilter, ProductFilter, OrderFilter


# GraphQL Types
class CustomerType(DjangoObjectType):
    """
    Represents a customer in the system.
    """

    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone", "created_at")


class ProductType(DjangoObjectType):
    """
    Represents a product in the system.
    """

    class Meta:
        model = Product
        fields = ("id", "name", "price", "stock", "created_at")


class OrderType(DjangoObjectType):
    """
    Represents an order in the system.
    """

    class Meta:
        model = Order
        fields = ("id", "customer", "products", "total_amount", "order_date")


# Input Types for Filtering
class CustomerFilterInput(graphene.InputObjectType):
    """
    Input type for filtering customers.
    """

    name = graphene.String()
    email = graphene.String()
    created_at__gte = graphene.Date()
    created_at__lte = graphene.Date()
    phone_pattern = graphene.String()


class ProductFilterInput(graphene.InputObjectType):
    """
    Input type for filtering products.
    """

    name = graphene.String()
    price__gte = graphene.Decimal()
    price__lte = graphene.Decimal()
    stock__gte = graphene.Int()
    stock__lte = graphene.Int()
    stock = graphene.Int()
    low_stock = graphene.Boolean()


class OrderFilterInput(graphene.InputObjectType):
    """
    Input type for filtering orders.
    """

    total_amount__gte = graphene.Decimal()
    total_amount__lte = graphene.Decimal()
    order_date__gte = graphene.Date()
    order_date__lte = graphene.Date()
    customer_name = graphene.String()
    product_name = graphene.String()
    product_id = graphene.Int()


# Input Types for Mutations
class CustomerInput(graphene.InputObjectType):
    """
    Represents the input fields for creating or updating a customer.
    """

    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()


class ProductInput(graphene.InputObjectType):
    """
    Represents the input fields for creating or updating a product.
    """

    name = graphene.String(required=True)
    price = graphene.Decimal(required=True)
    stock = graphene.Int()


class OrderInput(graphene.InputObjectType):
    """
    Represents the input fields for creating or updating an order.
    """

    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime()


# Mutation Classes
class CreateCustomer(graphene.Mutation):
    """
    Creates a new customer.
    """

    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(self, info, input):
        try:
            if input.phone:
                phone_pattern = r"^\+?1?\d{9,15}$|\d{3}-\d{3}-\d{4}$"
                if not re.match(phone_pattern, input.phone):
                    raise ValidationError(
                        "Phone number must be in the format +1234567890 or 123-456-7890"
                    )
            customer = Customer(name=input.name, email=input.email, phone=input.phone)
            customer.full_clean()
            customer.save()
            return CreateCustomer(
                customer=customer, message="Customer created successfully"
            )
        except IntegrityError:
            raise Exception("Email already exists.")
        except ValidationError as e:
            if "phone" in str(e):
                raise Exception(
                    "Phone number must be in the format +1234567890 or 123-456-7890"
                )
            else:
                raise Exception(f"Validation error: {e.message_dict}")


class BulkCreateCustomers(graphene.Mutation):
    """
    Creates multiple new customers.
    """

    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        customers = []
        errors = []

        with transaction.atomic():
            for customer_data in input:
                try:
                    customer = Customer(
                        name=customer_data.name,
                        email=customer_data.email,
                        phone=customer_data.phone,
                    )
                    customer.full_clean()
                    customer.save()
                    customers.append(customer)
                except Exception as e:
                    errors.append(
                        f"Error creating customer {customer_data.name}: {str(e)}"
                    )

        return BulkCreateCustomers(customers=customers, errors=errors)


class CreateProduct(graphene.Mutation):
    """
    Create a new product.
    """

    class Arguments:
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)

    def mutate(self, info, input):
        try:
            if input.price <= 0:
                raise ValidationError("Price must be positive")

            stock_value = input.stock if input.stock is not None else 0
            if stock_value < 0:
                raise ValidationError("Stock cannot be negative")

            product = Product(
                name=input.name, price=input.price, stock=input.stock or 0
            )
            product.full_clean()
            product.save()
            return CreateProduct(product=product)
        except ValidationError as e:
            raise Exception(f"Validation error: {str(e)}")


class CreateOrder(graphene.Mutation):
    """
    Create an order.
    """

    class Arguments:
        input = OrderInput(required=True)

    order = graphene.Field(OrderType)

    def mutate(self, info, input):
        try:
            # Validate customer exists
            customer = Customer.objects.get(id=input.customer_id)

            # Validate at least one product is provided
            if not input.product_ids or len(input.product_ids) == 0:
                raise Exception("At least one product must be selected")

            # Validate products exist
            products = Product.objects.filter(id__in=input.product_ids)
            if len(products) != len(input.product_ids):
                raise Exception("Some product IDs are invalid")

            # Calculate total amount
            total_amount = sum(product.price for product in products)

            # Create order
            order = Order.objects.create(customer=customer, total_amount=total_amount)
            order.products.set(products)

            return CreateOrder(order=order)
        except Customer.DoesNotExist:
            raise Exception("Customer not found")
        except Exception as e:
            raise Exception(str(e))


# Define Query and Mutation classes
class Query(graphene.ObjectType):
    customers = graphene.List(CustomerType)
    products = graphene.List(ProductType)
    orders = graphene.List(OrderType)

    all_customers = graphene.List(
        CustomerType,
        filters=CustomerFilterInput(),
        order_by=graphene.String(
            description="Order by field (name, email, created_at). Prefix with '-' for descending order."
        ),
    )
    all_products = graphene.List(
        ProductType,
        filters=ProductFilterInput(),
        order_by=graphene.String(
            description="Order by field (name, price, stock, created_at). Prefix with '-' for descending order."
        ),
    )
    all_orders = graphene.List(
        OrderType,
        filters=OrderFilterInput(),
        order_by=graphene.String(
            description="Order by field (total_amount, order_date). Prefix with '-' for descending order."
        ),
    )

    def resolve_customers(self, info):
        return Customer.objects.all()

    def resolve_products(self, info):
        return Product.objects.all()

    def resolve_orders(self, info):
        return Order.objects.all()

    def resolve_all_customers(self, info, filters=None, order_by=None):
        """
        Resolve filtered and ordered customers.
        """
        queryset = Customer.objects.all()

        if filters:
            filter_instance = CustomerFilter(filters, queryset=queryset)
            queryset = filter_instance.qs

        if order_by:
            valid_order_fields = [
                "name",
                "email",
                "created_at",
                "-name",
                "-email",
                "-created_at",
            ]
            if order_by in valid_order_fields:
                queryset = queryset.order_by(order_by)

        return queryset

    def resolve_all_products(self, info, filters=None, order_by=None):
        """
        Resolve filtered and ordered products.
        """
        queryset = Product.objects.all()

        if filters:
            filter_instance = ProductFilter(filters, queryset=queryset)
            queryset = filter_instance.qs

        if order_by:
            valid_order_fields = [
                "name",
                "price",
                "stock",
                "created_at",
                "-name",
                "-price",
                "-stock",
                "-created_at",
            ]
            if order_by in valid_order_fields:
                queryset = queryset.order_by(order_by)

        return queryset

    def resolve_all_orders(self, info, filters=None, order_by=None):
        """
        Resolve filtered and ordered orders.
        """
        queryset = Order.objects.all()

        if filters:
            filter_instance = OrderFilter(filters, queryset=queryset)
            queryset = filter_instance.qs

        if order_by:
            valid_order_fields = [
                "total_amount",
                "order_date",
                "-total_amount",
                "-order_date",
            ]
            if order_by in valid_order_fields:
                queryset = queryset.order_by(order_by)

        return queryset.distinct()


class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
