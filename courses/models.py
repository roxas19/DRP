from django.db import models
from users.models import InstructorProfile, StudentProfile, User
from organisations.models import Category
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.timezone import now

# Course model for managing courses.
class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to="courses/")
    duration = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.0)])
    level = models.CharField(max_length=50, choices=[("Beginner", "Beginner"), ("Advanced", "Advanced")])
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="courses")
    instructors = models.ManyToManyField(
        InstructorProfile,  # Allow multiple instructors for a course
        related_name="courses"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return self.title


# WeeklyModule manages course-specific weekly modules.
class WeeklyModule(models.Model):
    course = models.ForeignKey(Course, related_name="weekly_modules", on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    video = models.FileField(upload_to="weekly_modules/videos/", null=True, blank=True)
    quiz_title = models.CharField(max_length=200, blank=True)  # Added for quizzes
    quiz_description = models.TextField(blank=True)  # Added for quizzes
    order = models.PositiveIntegerField()
    status = models.CharField(
        max_length=20, choices=[("Completed", "Completed"), ("In Progress", "In Progress")], default="In Progress"
    )
    start_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.title} - {self.course.title}"

    def mark_completed_for_user(self, user):
        """
        Mark the module as completed for a user if all related tasks are completed.
        """
        if self.all_tasks_completed_for_user(user):
            enrollment = Enrollment.objects.get(student__user=user, course=self.course)
            if self.order not in enrollment.completed_weeks:
                enrollment.completed_weeks.append(self.order)
                enrollment.update_progress()
                enrollment.save()

    def all_tasks_completed_for_user(self, user):
        """
        Check if all tasks in the module are completed for a specific user.
        """
        task_completions = TaskCompletion.objects.filter(task__module=self, user=user)
        if not task_completions.exists():
            return False
        return all(tc.completed for tc in task_completions)


# Task serves as a static template for tasks in a module.
class Task(models.Model):
    module = models.ForeignKey(WeeklyModule, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(default=now)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.title} - {self.module.title}"


# TaskCompletion tracks user-specific task completion.
class TaskCompletion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="task_completions")
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="completions")
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("user", "task")

    def __str__(self):
        return f"{self.task.title} - {'Completed' if self.completed else 'Pending'}"


# Resource model for managing module resources.
class Resource(models.Model):
    module = models.ForeignKey(WeeklyModule, on_delete=models.CASCADE, related_name="resources")
    title = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(blank=True,null=True)
    file = models.FileField(upload_to="weekly_modules/resources/", null=True, blank=True)
    link = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.module.title}"


# Enrollment links students to courses.
class Enrollment(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name="enrollments", on_delete=models.CASCADE)
    progress = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    completed_weeks = models.JSONField(default=list)
    enrolled_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-enrolled_on"]
        unique_together = ("student", "course")

    def __str__(self):
        return f"{self.student} enrolled in {self.course}"

    def update_progress(self):
        """
        Updates course progress based on completed weeks.
        """
        total_modules = self.course.weekly_modules.count()
        self.progress = (len(self.completed_weeks) / total_modules) * 100
        self.save()
