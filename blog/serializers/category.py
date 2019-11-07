from rest_framework import serializers
from ..models import Category


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ['name']
        extra_kwargs = {'name': {'validators': []}, }  # Bypass unique validator to handle myself
