from decimal import Decimal

from django.shortcuts import get_object_or_404
from ninja import NinjaAPI, Schema

from .models import Item

api = NinjaAPI(title="Items API", version="1.0.0")


class ItemIn(Schema):
    name: str
    description: str
    price: Decimal


class ItemUpdate(Schema):
    name: str | None = None
    description: str | None = None
    price: Decimal | None = None


class ItemOut(Schema):
    id: int
    name: str
    description: str
    price: Decimal


@api.get("/items", response=list[ItemOut])
def list_items(request):
    return Item.objects.all()


@api.get("/items/{item_id}", response=ItemOut)
def get_item(request, item_id: int):
    return get_object_or_404(Item, id=item_id)


@api.post("/items", response=ItemOut)
def create_item(request, payload: ItemIn):
    return Item.objects.create(**payload.dict())


@api.put("/items/{item_id}", response=ItemOut)
def update_item(request, item_id: int, payload: ItemIn):
    item = get_object_or_404(Item, id=item_id)

    item.name = payload.name
    item.description = payload.description
    item.price = payload.price
    item.save()

    return item


@api.patch("/items/{item_id}", response=ItemOut)
def patch_item(request, item_id: int, payload: ItemUpdate):
    item = get_object_or_404(Item, id=item_id)

    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(item, attr, value)

    item.save()
    return item


@api.delete("/items/{item_id}")
def delete_item(request, item_id: int):
    item = get_object_or_404(Item, id=item_id)
    item.delete()
    return {"success": True}