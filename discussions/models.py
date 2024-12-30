from django.db import models
from users.models import User
from courses.models import WeeklyModule
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class DiscussionPost(models.Model):
    """
    Represents a post in the discussion section of a weekly module.
    """
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="discussion_posts")
    weekly_module = models.ForeignKey(WeeklyModule, on_delete=models.CASCADE, related_name="discussion_posts")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_flagged = models.BooleanField(default=False)
    flag_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.title} by {self.author.name} in {self.weekly_module.title}"

    class Meta:
        ordering = ['-created_at']


class Comment(models.Model):
    """
    Represents a comment or reply in a threaded discussion post.
    """
    post = models.ForeignKey(DiscussionPost, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_flagged = models.BooleanField(default=False)
    flag_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Comment by {self.author.name} on {self.post.title}"

    class Meta:
        ordering = ['created_at']

class Flag(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='flags')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    flagged_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'content_type', 'object_id')  # Prevent duplicate flags
        ordering = ['-flagged_at']

    def __str__(self):
        return f"{self.user} flagged {self.content_object}"