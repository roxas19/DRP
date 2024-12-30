from django.db import models
from users.models import InstructorProfile
from courses.models import Course, WeeklyModule
from django.utils.timezone import now


# Model for YouTube OAuth Token Storage
class YouTubeToken(models.Model):
    """
    Stores OAuth credentials for accessing the YouTube API.
    Only a single record is required as all livestreams use the same YouTube channel.
    """
    access_token = models.TextField()
    refresh_token = models.TextField()
    expires_at = models.DateTimeField(help_text="Access token expiry time.")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "YouTube API Token"


class Livestream(models.Model):
    """
    Represents a YouTube livestream associated with a course and weekly module.
    """
    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('LIVE', 'Live'),
        ('COMPLETED', 'Completed'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    instructor = models.ForeignKey(
        InstructorProfile, on_delete=models.CASCADE, related_name='livestreams'
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='livestreams'
    )
    weekly_module = models.OneToOneField(
        WeeklyModule, on_delete=models.CASCADE, related_name='livestream', null=True, blank=True
    )
    playlist_id = models.CharField(
        max_length=255, help_text="YouTube Playlist ID for archiving livestreams"
    )
    broadcast_id = models.CharField(
        max_length=255, unique=True, help_text="Unique YouTube Broadcast ID"
    )
    stream_key = models.CharField(
        max_length=255, help_text="RTMP Stream Key", blank=True, null=True
    )
    rtmp_url = models.CharField(
        max_length=255, help_text="RTMP Ingestion URL", blank=True, null=True
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='SCHEDULED',
        help_text="Current status of the livestream"
    )
    scheduled_start_time = models.DateTimeField(blank=True, null=True)
    started_at = models.DateTimeField(blank=True, null=True)
    ended_at = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    # Analytics fields
    view_count = models.PositiveIntegerField(default=0, help_text="Total number of views")
    average_watch_time = models.FloatField(default=0.0, help_text="Average watch time in minutes")

    def __str__(self):
        return f"{self.title} - {self.status}"

    def is_live(self):
        """
        Check if the livestream is currently live.
        """
        return self.status == 'LIVE'

    def mark_as_completed(self):
        """
        Mark the livestream as completed and set the end time.
        """
        self.status = 'COMPLETED'
        self.ended_at = now()
        self.save()
