from django.urls import path

from .views import PostListView, post_detail, PostShare, post_comment

app_name = 'blog'

urlpatterns = (
    path('', PostListView.as_view(), name='post_list'),
    path('<int:year>/<int:month>/<int:day>/<slug:slug>/',
         post_detail, name='post_detail'),
    path('<int:post_id>/share', PostShare.as_view(), name='post_share'),
    path('<int:post_id>/comment', post_comment, name='post_comment')
)
