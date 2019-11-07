from django.utils import timezone
from rest_framework import serializers
from .tag import TagNameSerializer
from .status import StatusSerializer
from .category import CategorySerializer
from ..models import Post, Tag, Category


def create_tags(tags, post_instance):
    """
    Check for tag existence and assign to posts, respectively.
    """
    for tag in tags:
        if Tag.objects.filter(name=tag['name']).exists():
            existing_tag = Tag.objects.filter(name=tag['name']).first()
            existing_tag.posts.add(post_instance)
        else:
            new_tag = Tag.objects.create(**tag)
            new_tag.posts.add(post_instance)


def create_category(category, post_instance):
    """
    Check for category existence and assign to post, respectively.
    """
    if Category.objects.filter(name=category.get('name')).exists():
        existing_cat = Category.objects.filter(name=category.get('name')).first()
        existing_cat.post_set.add(post_instance)
    else:
        new_cat = Category.objects.create(**category)
        new_cat.post_set.add(post_instance)


def update_post_fields(new_post_data, instance):
    instance.title = new_post_data.get('title', instance.title)
    instance.symbol = new_post_data.get('symbol', instance.symbol)
    instance.byline = new_post_data.get('byline', instance.byline)
    instance.background_image = new_post_data.get('background_image', instance.background_image)
    instance.slug = new_post_data.get('slug', instance.slug)
    instance.content = new_post_data.get('content', instance.content)
    instance.read_time = new_post_data.get('read_time', instance.read_time)
    instance.updated_on = timezone.now()
    instance.publish_on = new_post_data.get('publish_on', instance.publish_on)
    instance.status = new_post_data.get('status', instance.status)


def update_tags(update_tags, post_instance):
    keep_tags = []
    for tag in update_tags:
        if Tag.objects.filter(name=tag.get('name')).exists():
            existing_tag = Tag.objects.filter(name=tag.get('name')).first()
            existing_tag.posts.add(post_instance)
            keep_tags.append(existing_tag.name)
        else:
            new_tag = Tag.objects.create(**tag)
            new_tag.posts.add(post_instance)
            keep_tags.append(new_tag.name)
    for old_tag in post_instance.tags:
        if old_tag.name not in keep_tags:
            post_instance.tag_set.remove(old_tag)


def update_category(update_category, post_instance):
    if post_instance.category is None:
        if update_category:
            if Category.objects.filter(name=update_category.get('name')).exists():
                existing_cat = Category.objects.filter(name=update_category.get('name')).first()
                existing_cat.post_set.add(post_instance)
            else:
                new_cat = Category.objects.create(**update_category)
                new_cat.post_set.add(post_instance)
        elif not update_category:
            post_instance.category = None
    if post_instance.category:
        if not update_category:
            post_instance.category = None
        elif update_category:
            if post_instance.category.name != update_category.get('name'):
                if Category.objects.filter(name=update_category.get('name')).exists():
                    existing_cat = Category.objects.filter(name=update_category.get('name')).first()
                    existing_cat.post_set.add(post_instance)
                else:
                    new_cat = Category.objects.create(**update_category)
                    new_cat.post_set.add(post_instance)


class PostSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field='username', required=False, read_only=True)
    tags = TagNameSerializer(many=True, required=False)
    status = StatusSerializer
    category = CategorySerializer(required=False, allow_null=True)

    class Meta:
        model = Post
        fields = '__all__'

    def create(self, validated_data):
        tags_exists = False; category_exists = False
        if 'tags' in validated_data:
            tags = validated_data.pop('tags')
            tags_exists = True
        if 'category' in validated_data:
            category = validated_data.pop('category')
            category_exists = True
        post = Post.objects.create(**validated_data)
        if tags_exists: create_tags(tags, post)
        if category_exists: create_category(category, post)
        return post

    def update(self, instance, validated_data):
        new_post_tags = validated_data.pop('tags')
        new_post_category = validated_data.pop('category')

        update_post_fields(validated_data, instance)

        update_category(new_post_category, instance)
        update_tags(new_post_tags, instance)

        instance.save()
        return instance
