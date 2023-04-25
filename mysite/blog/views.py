from django.core.handlers.wsgi import WSGIRequest
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views import View
from django.views.decorators.http import require_POST
from django.views.generic import ListView

from mysite.settings import EMAIL_HOST_USER
from .forms import EmailPostForm, CommitForm
from .models import Post


class PostListView(ListView):
    template_name = 'blog/post/list.html'
    context_object_name = 'posts'
    queryset = Post.published.all()
    paginate_by = 3


def post_detail(request: WSGIRequest, year: int, month: int,
                day: int, slug: str) -> HttpResponse:
    post = get_object_or_404(
        Post, status=Post.Status.PUBLISHED, slug=slug,
        publish__month=month, publish__day=day, publish__year=year
    )
    comments = post.comments.filter(active=True)
    form = CommitForm()
    context = {'post': post, 'comments': comments, 'form': form}
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
