from rest_framework import serializers
from ..models import Post, Tag


class TagPostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = ['title',]


class TagNameSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ['name',]
        extra_kwargs = {'name': {'validators': []}, }  # Bypass unique validator to handle myself


class TagSerializer(serializers.ModelSerializer):
    # posts = serializers.HyperlinkedRelatedField(many=True, required=False, read_only=True, view_name='post-detail')  # Uncomment to enable posts

    class Meta:
        model = Tag
        # fields = ['name', 'posts']  # Uncomment to enable posts
        fields = ['name']
        # read_only_fields = ('posts',)  # Uncomment to enable posts
        extra_kwargs = { 'name': {'validators': []}, }  # Bypass unique validator to handle myself
