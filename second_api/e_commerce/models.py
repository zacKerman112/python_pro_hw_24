from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name}\n{self.description}\n{self.price}"


class Cart(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart {self.id}\nCreated at: {self.created_at}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def __str__(self):
        return f"CartItem {self.id}\n{self.cart.id}\n{self.product.id}\n{self.quantity}"


class Order(models.Model):
    STATUS_CHOICES = [
        ("processing", "In process"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="processing",
    )
    created_at = models.DateTimeField(auto_now_add=True)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)