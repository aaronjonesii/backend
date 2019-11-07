from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Post, Category, Status, Tag, NewsletterSubscriber

admin.site.register(User, UserAdmin)
admin.site.register(Post)
admin.site.register(Category)
admin.site.register(Status)
admin.site.register(Tag)
admin.site.register(NewsletterSubscriber)
