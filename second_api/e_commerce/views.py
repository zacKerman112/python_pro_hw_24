from decimal import Decimal
from typing import Any, Literal

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from ninja import NinjaAPI, Schema

from .models import Cart, CartItem, Order, OrderItem, Product

api = NinjaAPI(title="E-commerce API", version="1.0.0")


class ProductIn(Schema):
    name: str
    description: str
    price: Decimal


class ProductUpdate(Schema):
    name: str | None = None
    description: str | None = None
    price: Decimal | None = None


class ProductOut(Schema):
    id: int
    name: str
    description: str
    price: Decimal


class CartIn(Schema):
    product_id: int
    quantity: int

class CartOut(Schema):
    id: int
    product: ProductOut
    quantity: int


class OrderStatusUpdate(Schema):
    status: Literal["processing", "shipped", "delivered"]


@api.get("/products", response=list[ProductOut])
@login_required
def list_products(request: HttpRequest) -> Any:
    """Return all products."""
    return Product.objects.all()


@api.get("/products/{product_id}", response=ProductOut)
@login_required
def get_product(request: HttpRequest, product_id: int) -> Any:
    """Return a single product by ID."""
    return get_object_or_404(Product, id=product_id)


@api.post("/products", response=ProductOut)
@login_required
def create_product(request: HttpRequest, payload: ProductIn) -> Any:
    """Create a new product."""
    return Product.objects.create(**payload.dict())


@api.put("/products/{product_id}", response=ProductOut)
@login_required
def update_product(request: HttpRequest, product_id: int, payload: ProductIn) -> Any:
    """Replace an existing product."""
    product = get_object_or_404(Product, id=product_id)
    product.name = payload.name
    product.description = payload.description
    product.price = payload.price
    product.save()
    return product


@api.patch("/products/{product_id}", response=ProductOut)
@login_required
def patch_product(
    request: HttpRequest,
    product_id: int,
    payload: ProductUpdate,
) -> Any:
    """Partially update an existing product."""
    product = get_object_or_404(Product, id=product_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(product, attr, value)
    product.save()
    return product

@api.delete("/products/{product_id}")
@login_required
def delete_product(request: HttpRequest, product_id: int) -> dict[str, bool]:
    """Delete a product."""
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return {"success": True}


@api.get("/cart", response=list[CartOut])
@login_required
def list_cart(request: HttpRequest) -> Any:
    """Return all cart items."""
    return CartItem.objects.all()

@api.get("/cart/items/{item_id}", response=CartOut)
@login_required
def get_cart_item(request: HttpRequest, item_id: int) -> Any:
    """Return a single cart item by ID."""
    return get_object_or_404(CartItem, id=item_id)

@api.post("/cart/items", response=CartOut)
@login_required
def create_cart_item(request: HttpRequest, payload: CartIn) -> Any:
    """Add a product to the cart."""
    cart, _ = Cart.objects.get_or_create(id=1)
    return CartItem.objects.create(
        cart=cart,
        product_id=payload.product_id,
        quantity=payload.quantity,
    )

@api.put("/cart/items/{product_id}", response=CartOut)
@login_required
def update_cart_item(
    request: HttpRequest,
    product_id: int,
    payload: CartIn,
) -> Any:
    """Update a cart item quantity."""
    cart_item = get_object_or_404(CartItem, product_id=product_id)
    cart_item.quantity = payload.quantity
    cart_item.save()
    return cart_item

@api.delete("/cart/items/{product_id}")
@login_required
def delete_cart_item(request: HttpRequest, product_id: int) -> dict[str, bool]:
    """Remove a product from the cart."""
    cart_item = get_object_or_404(CartItem, product_id=product_id)
    cart_item.delete()
    return {"success": True}


@api.post("/orders/checkout")
@login_required
def checkout(request: HttpRequest) -> dict[str, Any]:
    """Create an order from cart items."""
    cart, _ = Cart.objects.get_or_create(id=1)
    cart_items = CartItem.objects.filter(cart=cart)

    if not cart_items.exists():
        return {"error": "Cart is empty"}

    order = Order.objects.create(status="processing")

    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price,
        )

    cart_items.delete()

    return {"success": True, "order_id": order.id}


@api.patch("/orders/{order_id}/status")
@login_required
def update_order_status(
    request: HttpRequest,
    order_id: int,
    payload: OrderStatusUpdate,
) -> dict[str, Any]:
    """Update an order status."""
    order = get_object_or_404(Order, id=order_id)
    order.status = payload.status
    order.save()
    return {"id": order.id, "status": order.status}