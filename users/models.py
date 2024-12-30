from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.timezone import now


# Custom User Manager
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('The Email field must be set')

        email = self.normalize_email(email)
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Creates and saves a superuser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


# Role Model
class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


# Custom User Model
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    profile_photo = models.ImageField(upload_to='users/', blank=True, null=True)
    roles = models.ManyToManyField(Role, related_name='users')  # Flexible role system

    is_active = models.BooleanField(default=True)  # Can log in
    is_staff = models.BooleanField(default=False)  # Can access admin site

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    objects = UserManager()

    def __str__(self):
        return self.name

    def is_student(self):
        return self.roles.filter(name="Student").exists()

    def is_instructor(self):
        return self.roles.filter(name="Instructor").exists()


# Student Profile Model
class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    learning_goals = models.TextField(blank=True, null=True)
    progress = models.JSONField(blank=True, null=True)  # Stores progress for courses
    completed_courses_count = models.IntegerField(default=0)
    achievements = models.TextField(blank=True, null=True)
    preferred_language = models.CharField(max_length=50, blank=True, null=True)
    timezone = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"Student Profile for {self.user.name}"


# Instructor Profile Model
class InstructorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='instructor_profile')
    bio = models.TextField(blank=True, null=True)
    qualification = models.CharField(max_length=255)
    teaching_experience = models.IntegerField(default=0)  # Number of years
    specialization = models.CharField(max_length=255, blank=True, null=True)
    rating = models.FloatField(default=0.0)  # Average rating by students
    video_intro = models.URLField(blank=True, null=True)  # Link to intro video
    availability = models.CharField(max_length=255, blank=True, null=True)  # Example: "Monday, Wednesday, Friday"
    languages_spoken = models.CharField(max_length=255, blank=True, null=True)
    teaching_style = models.TextField(blank=True, null=True)
    course_count = models.IntegerField(default=0)  # Number of courses taught
    achievements = models.TextField(blank=True, null=True)
    certified = models.BooleanField(default=False)  # Certified or not

    # New fields for tracking and validation
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)  # Optional: Deactivate instructors if needed

    total_live_hours = models.FloatField(default=0.0)  # Total hours of live teaching
    total_streams = models.IntegerField(default=0)

    def __str__(self):
        return f"Instructor Profile for {self.user.name}"

    def save(self, *args, **kwargs):
        # Prevent duplicate InstructorProfiles
        if InstructorProfile.objects.filter(user=self.user).exists() and not self.pk:
            raise ValueError("An InstructorProfile already exists for this user.")
        super().save(*args, **kwargs)

