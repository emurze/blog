from django.urls import path

from .feeds import LatestPostFeed
from .views import PostListView, post_detail, PostShare, post_comment, \
    post_search

app_name = 'blog'

urlpatterns = (
    path('', PostListView.as_view(), name='post_list'),
    path('tags/<slug:tag_slug>/', PostListView.as_view(),
         name="post_list_by_tag"),
    path('<int:year>/<int:month>/<int:day>/<slug:slug>/',
         post_detail, name='post_detail'),
    path('<int:post_id>/share', PostShare.as_view(), name='post_share'),
    path('<int:post_id>/comment', post_comment, name='post_comment'),
    path('feed/', LatestPostFeed(), name='post_feed'),
    path('search/', post_search, name='post_search'),
)
