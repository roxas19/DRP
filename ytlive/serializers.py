from rest_framework import serializers
from .models import Livestream
from users.models import InstructorProfile
from courses.models import Course, WeeklyModule
from django.utils.timezone import now



class LivestreamCreateSerializer(serializers.Serializer):
    """
    Serializer for creating a new livestream.
    """
    title = serializers.CharField(
        max_length=255,
        help_text="The title of the livestream."
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="A brief description of the livestream."
    )
    scheduled_start_time = serializers.DateTimeField(
        required=False,
        default=None,
        help_text="The scheduled start time for the livestream (in ISO format)."
    )
    course_id = serializers.IntegerField(help_text="The ID of the course for the livestream.")
    weekly_module_id = serializers.IntegerField(help_text="The ID of the weekly module for the livestream.")

    def validate(self, data):
        """
        Validate course and weekly module association and instructor permissions.
        """
        user = self.context['request'].user

        # Check if the user is an instructor
        if not hasattr(user, 'instructor_profile'):
            raise serializers.ValidationError("Only instructors can create livestreams.")

        # Validate course
        try:
            course = Course.objects.get(id=data['course_id'], instructors__user=user)
        except Course.DoesNotExist:
            raise serializers.ValidationError("You are not an instructor of this course.")

        # Validate weekly module
        try:
            weekly_module = WeeklyModule.objects.get(id=data['weekly_module_id'], course=course)
        except WeeklyModule.DoesNotExist:
            raise serializers.ValidationError("Invalid weekly module for this course.")

        # Ensure scheduled_start_time is in the future
        if 'scheduled_start_time' in data and data['scheduled_start_time'] < now():
            raise serializers.ValidationError("Scheduled start time must be in the future.")

        data['course'] = course
        data['weekly_module'] = weekly_module
        return data



class LivestreamSerializer(serializers.ModelSerializer):
    """
    Serializer for returning livestream details.
    """
    instructor_name = serializers.CharField(source='instructor.user.name', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)
    weekly_module_order = serializers.IntegerField(source='weekly_module.order', read_only=True)

    class Meta:
        model = Livestream
        fields = [
            'id', 'title', 'description', 'status', 'scheduled_start_time',
            'started_at', 'ended_at', 'playlist_id', 'broadcast_id',
            'rtmp_url', 'stream_key', 'instructor_name', 'course_title', 'weekly_module_order',
            'view_count', 'average_watch_time'
        ]

    def __init__(self, *args, **kwargs):
        """
        Dynamically include/exclude fields based on user context.
        """
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and not hasattr(request.user, 'instructor_profile'):
            # Exclude sensitive fields for non-instructors
            self.fields.pop('stream_key')
            self.fields.pop('rtmp_url')
