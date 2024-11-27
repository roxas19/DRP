from django.db import models
from users.models import Instructor
from categories.models import Category

class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='courses/')
    duration = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    level = models.CharField(max_length=50, choices=[('Beginner', 'Beginner'), ('Advanced', 'Advanced')])
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    instructor = models.ForeignKey(Instructor, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class WeeklyModule(models.Model):
    course = models.ForeignKey(Course, related_name='weekly_modules', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    video = models.FileField(upload_to='weekly_modules/videos/', null=True, blank=True)
    resources = models.FileField(upload_to='weekly_modules/resources/', null=True, blank=True)  # Optional resources like PDFs
    quiz = models.TextField(blank=True)  # Placeholder for quiz content
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ['order']  # Ensures consistent ordering

    def __str__(self):
        return f"{self.title} - {self.course.title}"


class Enrollment(models.Model):
    student = models.ForeignKey('users.Student', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name='enrollments', on_delete=models.CASCADE)
    progress = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)  # Percentage completion
    enrolled_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} enrolled in {self.course}"
