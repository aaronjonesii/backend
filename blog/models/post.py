from django.conf import settings
from django.db import models
from .status import Status
from .category import Category


class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.PROTECT,
                               help_text="User who created the Blog Post.")
    category = models.ForeignKey(Category,
                                 on_delete=models.CASCADE,
                                 blank=True, null=True)
    title = models.CharField(max_length=64, unique=True)                                    # REQUIRED
    symbol = models.CharField(max_length=2, blank=True)
    byline = models.CharField(max_length=255, blank=True)
    background_image = models.URLField(blank=True)
    slug = models.SlugField(max_length=128)                                                 # REQUIRED
    content = models.TextField(null=True)                                                   # REQUIRED
    read_time = models.IntegerField(null=True)                                              # REQUIRED
    updated_on = models.DateTimeField(auto_now=True)                                        # REQUIRED
    created_on = models.DateTimeField(auto_now_add=True)                                    # REQUIRED
    publish_on = models.DateField(null=True, blank=True)
    status = models.ForeignKey(Status, on_delete=models.CASCADE, related_name='status')     # REQUIRED

    class Meta:
        verbose_name = "Post"
        verbose_name_plural = "Posts"

    def __str__(self):
        return self.title

    @property
    def tags(self):
        return self.tag_set.all()
