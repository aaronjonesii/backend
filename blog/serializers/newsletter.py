from rest_framework import serializers
from ..models import NewsletterSubscriber


class NewsletterSerializer(serializers.ModelSerializer):

    class Meta:
        model = NewsletterSubscriber
        fields = ['email', 'name']
        extra_kwargs = {'email': {'validators': []}, }  # Bypass unique validator to handle myself

    def create(self, validated_data):
        email = validated_data['email']
        potentialnewsletterSubscriber = NewsletterSubscriber.objects.all().filter(email=email)
        if potentialnewsletterSubscriber.exists():
            existingSubscriber = potentialnewsletterSubscriber.first()
            if existingSubscriber.name != validated_data.get('name', ''):
                existingSubscriber.name = validated_data.get('name', '')
            existingSubscriber.isactive = True
            existingSubscriber.save()
            return existingSubscriber
        else:
            newsletterSubscriber = NewsletterSubscriber.objects.create(**validated_data)
            print('Created new Newsletter Subscriber... -> ', newsletterSubscriber)
            return newsletterSubscriber
