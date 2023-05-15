from django.core.handlers.wsgi import WSGIRequest
from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views import View
from django.views.decorators.http import require_POST
from taggit.models import Tag

from config.settings import EMAIL_HOST_USER
from .forms import EmailPostForm, CommitForm, SearchForm
from .models import Post


class PostListView(View):
    TEMP_NAME = 'blog/post/list.html'

    def get(self, request: WSGIRequest,
            tag_slug: str | None = None) -> HttpResponse:
        posts = Post.published.all()
        tag = None
        if tag_slug:
            tag = get_object_or_404(Tag, slug=tag_slug)
            posts = posts.filter(tags__in=[tag])
        paginator = Paginator(posts, 3)
        page_number = request.GET.get('page', 1)
        try:
            posts_per_page = paginator.page(page_number)
        except EmptyPage:
            posts_per_page = paginator.page(paginator.num_pages)
        except PageNotAnInteger:
            posts_per_page = paginator.page(1)
        context = {'posts': posts_per_page, 'tag': tag}
        return render(request, self.TEMP_NAME, context)


def post_detail(request: WSGIRequest, year: int, month: int,
                day: int, slug: str) -> HttpResponse:
    post = get_object_or_404(
        Post, status=Post.Status.PUBLISHED, slug=slug,
        publish__month=month, publish__day=day, publish__year=year
    )
    comments = post.comments.filter(active=True)
    form = CommitForm()

    allowed_tags_id = post.tags.values_list('id', flat=True)
    similar_posts = Post.objects.filter(tags__in=allowed_tags_id)\
                                .exclude(pk=post.pk)
    similar_posts = similar_posts.annotate(tags_count=Count('tags'))\
                                 .order_by('-tags_count', '-publish')[:4]

    context = {'post': post, 'comments': comments, 'form': form,
               'similar_posts': similar_posts}

    return render(request, 'blog/post/detail.html', context)


class PostShare(View):
    TEMP_NAME = 'blog/post/share.html'

    def get(self, request: WSGIRequest, post_id: int) -> HttpResponse:
        post = get_object_or_404(Post, pk=post_id)
        form = EmailPostForm()
        context = {'post': post, 'form': form}
        return render(request,  self.TEMP_NAME, context)

    def post(self, request: WSGIRequest, post_id: int) -> HttpResponse:
        post = get_object_or_404(Post, pk=post_id)
        sent = False
        if (form := EmailPostForm(request.POST)).is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you read {post.title}"
            message = f"Read {post.title} at {post_url}\n\n" \
                      f"{cd['name']}\'s comments: {cd['content']}'"
            send_mail(subject, message, EMAIL_HOST_USER, [cd["to"]])
            sent = True
        context = {'post': post, 'form': form, 'sent': sent}
        return render(request, self.TEMP_NAME, context)


@require_POST
def post_comment(request: WSGIRequest, post_id: int) -> HttpResponse:
    post = get_object_or_404(Post, pk=post_id)
    comment = False
    if (form := CommitForm(request.POST)).is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()
    context = {'post': post, 'form': form, 'comment': comment}
    return render(request, 'blog/post/comment.html', context)


def post_search(request: WSGIRequest) -> HttpResponse:
    results = []
    form = SearchForm()
    query = None

    if request.GET.get('query'):
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            # search_query = SearchQuery(query)
            # search_vector = (SearchVector('title', weight='A') +
            #                  SearchVector('content', weight='B'))
            # results = Post.published.annotate(
            #     rank=SearchRank(vector=search_vector, query=search_query)
            # ).filter(rank__gt=0.3).order_by('-rank')
            # results = Post.published.annotate(
            #     similarity=TrigramSimolarity
            # )

    context = {'form': form, 'query': query, 'results': results}
    print(context)
    return render(request, 'blog/post/search.html', context)
