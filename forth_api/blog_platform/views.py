from datetime import datetime
from typing import Any

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from ninja import Schema, NinjaAPI

from .models import Comment, Post, Tag


api = NinjaAPI(title="Blog Platform API", version="1.0.0")


class PostIn(Schema):
    author_id: int
    title: str
    content: str


class PostUpdate(Schema):
    title: str | None = None
    content: str | None = None


class PostOut(Schema):
    id: int
    author_id: int
    title: str
    content: str
    created_at: datetime


class CommentIn(Schema):
    post_id: int
    content: str


class CommentOut(Schema):
    id: int
    post_id: int
    content: str
    created_at: datetime


class TagIn(Schema):
    name: str


class TagOut(Schema):
    id: int
    name: str


@api.post("/posts", response=PostOut)
@login_required
def create_post(request: HttpRequest, payload: PostIn) -> Any:
    """Create a new blog post."""
    get_object_or_404(User, id=payload.author_id)
    return Post.objects.create(
        author_id=payload.author_id,
        title=payload.title,
        content=payload.content,
    )


@api.get("/posts", response=list[PostOut])
@login_required
def list_posts(request: HttpRequest) -> Any:
    """Return all blog posts."""
    return Post.objects.all()


@api.get('/posts/{post_id}', response=PostOut)
@login_required
def get_post(request: HttpRequest, post_id: int) -> Any:
    """Return a single blog post by ID."""
    return get_object_or_404(Post, id=post_id)


@api.patch('/posts/{post_id}', response=PostOut)
@login_required
def patch_post(request: HttpRequest, post_id: int, payload: PostUpdate) -> Any:
    """Partially update a blog post."""
    post = get_object_or_404(Post, id=post_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(post, attr, value)
    post.save()
    return post


@api.put('/posts/{post_id}', response=PostOut)
@login_required
def update_post(request: HttpRequest, post_id: int, payload: PostIn) -> Any:
    """Replace a blog post."""
    get_object_or_404(User, id=payload.author_id)
    post = get_object_or_404(Post, id=post_id)
    for attr, value in payload.dict().items():
        setattr(post, attr, value)
    post.save()
    return post


@api.delete('/posts/{post_id}')
@login_required
def delete_post(request: HttpRequest, post_id: int) -> dict[str, str]:
    """Delete a blog post."""
    post = get_object_or_404(Post, id=post_id)
    post.delete()
    return {"message": "Post deleted successfully"}


@api.post("/comments", response=CommentOut)
@login_required
def create_comment(request: HttpRequest, payload: CommentIn) -> Any:
    """Create a comment for a blog post."""
    get_object_or_404(Post, id=payload.post_id)
    return Comment.objects.create(
        post_id=payload.post_id,
        content=payload.content,
    )


@api.get("/tags", response=list[TagOut])
@login_required
def list_tags(request: HttpRequest) -> Any:
    """Return all tags."""
    return Tag.objects.all()


@api.post("/tags", response=TagOut)
@login_required
def create_tag(request: HttpRequest, payload: TagIn) -> Any:
    """Create a new tag."""
    return Tag.objects.create(**payload.dict())


@api.post("/posts/{post_id}/tags/{tag_id}")
@login_required
def add_tag_to_post(
    request: HttpRequest,
    post_id: int,
    tag_id: int,
) -> dict[str, bool]:
    """Attach a tag to a blog post."""
    post = get_object_or_404(Post, id=post_id)
    tag = get_object_or_404(Tag, id=tag_id)

    post.tags.add(tag)

    return {"success": True}


@api.delete("/posts/{post_id}/tags/{tag_id}")
@login_required
def remove_tag_from_post(
    request: HttpRequest,
    post_id: int,
    tag_id: int,
) -> dict[str, bool]:
    """Remove a tag from a blog post."""
    post = get_object_or_404(Post, id=post_id)
    tag = get_object_or_404(Tag, id=tag_id)

    post.tags.remove(tag)

    return {"success": True}