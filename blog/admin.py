from django.contrib import admin
from .models import Post, Comment, Profile, Category


class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'date_of_birth', 'photo']


admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Category)