from django.contrib import admin

from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'author', 'publish', 'status']
    list_filter = ['status', 'created', 'publish']
    search_fields = ['title', 'content']
    prepopulated_fields = {"slug": ('title',)}
    date_hierarchy = 'publish'
    raw_id_fields = ['author']
    ordering = ['-status', 'publish']
