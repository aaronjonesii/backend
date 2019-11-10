from django.db import models
from.post import Post


class Tag(models.Model):
    name = models.CharField(unique=True, blank=False)
    posts = models.ManyToManyField(Post, blank=True)

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"

    def __str__(self):
        return self.name
