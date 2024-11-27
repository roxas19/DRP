from django.db import models
from django.conf import settings

class Student(models.Model):
    # Link to the User model (students are also users)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    profile_photo = models.ImageField(upload_to='students/', blank=True, null=True)
    learning_goals = models.TextField(blank=True, null=True)

    # Instead of importing `Course` at the top, import it inside the method that needs it
    def courses_enrolled(self):
        from courses.models import Course  # Lazy import
        return self.courses.all()
    
    progress = models.JSONField(blank=True, null=True)
    preferred_language = models.CharField(max_length=50, blank=True, null=True)
    activity_level = models.IntegerField(default=0)
    achievements = models.TextField(blank=True, null=True)
    feedback = models.TextField(blank=True, null=True)
    learning_style = models.CharField(max_length=100, blank=True, null=True)
    preferred_course_type = models.CharField(max_length=50, blank=True, null=True)
    start_date = models.DateField(auto_now_add=True)
    completed_courses_count = models.IntegerField(default=0)
    timezone = models.CharField(max_length=50, blank=True, null=True)
    contact_info = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.user.name  # Display the student's name from the User model
