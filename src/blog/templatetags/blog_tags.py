from typing import TypeAlias

import markdown
from django import template
from django.db.models import Count, QuerySet
from django.utils.safestring import mark_safe, SafeString

from blog.models import Post

register = template.Library()
Context: TypeAlias = dict


@register.simple_tag
def total_posts_count() -> QuerySet:
    return Post.published.count()


@register.inclusion_tag('blog/post/latest_posts.html')
def show_latest_posts(count: int = 5) -> Context:
    latest_posts = Post.published.order_by('-publish')[:count]
    return {'latest_posts': latest_posts}


@register.simple_tag
def show_most_commented_posts(count: int = 5) -> QuerySet:
    return Post.published.annotate(
        comments_count=Count('comments')
    ).order_by('-comments_count')[:count]


@register.filter(name='markdown')
def markdown_filter(text: str) -> SafeString:
    return mark_safe(markdown.markdown(text))
