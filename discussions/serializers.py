from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from .models import DiscussionPost, Comment, Flag
from users.serializers import UserSerializer
from courses.models import WeeklyModule
from courses.views import is_enrolled  # Helper function


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for the Comment model, representing threaded replies to discussion posts.
    """
    author = serializers.SerializerMethodField()
    is_author = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()
    can_delete = serializers.SerializerMethodField()
    needs_moderation = serializers.SerializerMethodField()
    user_flagged = serializers.SerializerMethodField()
    flag_count = serializers.ReadOnlyField()  # Directly from the model field

    class Meta:
        model = Comment
        fields = [
            'id', 'content', 'author', 'post', 'created_at', 'updated_at',
            'is_flagged', 'flag_count', 'is_author', 'can_edit', 'can_delete',
            'needs_moderation', 'user_flagged',
        ]
        read_only_fields = [
            'author', 'created_at', 'updated_at', 'is_flagged', 'flag_count',
            'is_author', 'can_edit', 'can_delete', 'needs_moderation', 'user_flagged',
        ]

    def get_author(self, obj):
        return obj.author.name

    def get_is_author(self, obj):
        request = self.context.get('request')
        return request and request.user == obj.author

    def get_can_edit(self, obj):
        request = self.context.get('request')
        return request and (request.user == obj.author or request.user.is_instructor())

    def get_can_delete(self, obj):
        request = self.context.get('request')
        return request and (request.user == obj.author or request.user.is_instructor())

    def get_needs_moderation(self, obj):
        return obj.flag_count > 2  # Use the model's field directly

    def get_user_flagged(self, obj):
        """
        Determine if the logged-in user has flagged this comment.
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            content_type = ContentType.objects.get_for_model(Comment)
            return Flag.objects.filter(
                user=request.user,
                content_type=content_type,
                object_id=obj.id
            ).exists()
        return False


class DiscussionPostSerializer(serializers.ModelSerializer):
    """
    Serializer for the DiscussionPost model, representing discussion threads.
    """
    author = serializers.SerializerMethodField()
    is_author = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()  # Dynamically include comments based on the view's logic
    can_edit = serializers.SerializerMethodField()
    can_delete = serializers.SerializerMethodField()
    needs_moderation = serializers.SerializerMethodField()
    user_flagged = serializers.SerializerMethodField()
    flag_count = serializers.ReadOnlyField()  # Directly from the model field

    class Meta:
        model = DiscussionPost
        fields = [
            'id', 'title', 'content', 'author', 'weekly_module', 'created_at',
            'updated_at', 'is_flagged', 'flag_count', 'is_author', 'can_edit',
            'can_delete', 'comments', 'needs_moderation', 'user_flagged',
        ]
        read_only_fields = [
            'author', 'created_at', 'updated_at', 'is_flagged', 'flag_count',
            'is_author', 'can_edit', 'can_delete', 'comments', 'needs_moderation', 'user_flagged',
        ]

    def get_author(self, obj):
        return obj.author.name

    def get_is_author(self, obj):
        request = self.context.get('request')
        return request and request.user == obj.author

    def get_can_edit(self, obj):
        request = self.context.get('request')
        return request and (request.user == obj.author or request.user.is_instructor())

    def get_can_delete(self, obj):
        request = self.context.get('request')
        return request and (request.user == obj.author or request.user.is_instructor())

    def get_needs_moderation(self, obj):
        return obj.flag_count > 2  # Use the model's field directly

    def get_user_flagged(self, obj):
        """
        Determine if the logged-in user has flagged this post.
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            content_type = ContentType.objects.get_for_model(DiscussionPost)
            return Flag.objects.filter(
                user=request.user,
                content_type=content_type,
                object_id=obj.id
            ).exists()
        return False

    def get_comments(self, obj):
        """
        Dynamically fetch comments based on the context provided by the view.
        """
        request = self.context.get('request')
        flagged_only = request.query_params.get('flagged_only', 'false').lower() == 'true'

        comments_query = Comment.objects.filter(post=obj)
        if flagged_only:
            comments_query = comments_query.filter(flag_count__gt=2)

        return CommentSerializer(comments_query, many=True, context=self.context).data

    def validate_weekly_module(self, value):
        """
        Validate that the weekly module exists and the user is enrolled in the associated course.
        """
        request = self.context.get('request')
        if not request:
            raise serializers.ValidationError("Request context is required.")
        if not WeeklyModule.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("The specified weekly module does not exist.")
        if not is_enrolled(request.user, value.course):
            raise serializers.ValidationError("You must be enrolled in the course to create a post.")
        return value
