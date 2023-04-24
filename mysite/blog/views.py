from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView

from blog.forms import EmailPostForm
from blog.models import Post


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
    return render(request, 'blog/post/detail.html', {'post': post})


def post_share(request: WSGIRequest, post_id: int) -> HttpResponse:
    post = get_object_or_404(Post, pk=post_id)
    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            # send email
            print(cd)
    else:
        form = EmailPostForm()
    print(form)
    return render(request, 'blog/post/share.html', {'form': form, 'post': post})
