from django.db import models


class NewsletterSubscriber(models.Model):
    name = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=False, unique=True)
    isactive = models.BooleanField(blank=False)

    class Meta:
        verbose_name = "Newsletter Subscriber"
        verbose_name_plural = "Newsletter Subscribers"

    def __str__(self):
        return f'{self.email} - {self.name}'
