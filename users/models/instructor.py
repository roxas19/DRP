from django.db import models
from django.conf import settings

class Instructor(models.Model):
    # Link to the User model (instructors are also users)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    bio = models.TextField()
    profile_photo = models.ImageField(upload_to='instructors/', blank=True, null=True)
    qualification = models.CharField(max_length=255)
    teaching_experience = models.IntegerField(default=0)  # Number of years
    specialization = models.CharField(max_length=255, null=True, blank=True) 
    rating = models.FloatField(default=0.0)  # Average rating by students
    video_intro = models.URLField(blank=True, null=True)  # Link to intro video
    availability = models.CharField(max_length=255, blank=True, null=True)  # Example: "Monday, Wednesday, Friday"
    languages_spoken = models.CharField(max_length=255, blank=True, null=True)
    teaching_style = models.TextField(blank=True, null=True)
    course_count = models.IntegerField(default=0)  # Number of courses taught
    achievements = models.TextField(blank=True, null=True)  # Notable achievements or awards
    contact_info = models.EmailField(blank=True, null=True)  # Optional contact info
    social_media_links = models.JSONField(blank=True, null=True)  # Links to social media profiles
    certified = models.BooleanField(default=False)  # Certified or not

    def __str__(self):
        return self.user.name  # Display the instructor's name from the User model
