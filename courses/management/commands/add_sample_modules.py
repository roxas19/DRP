from django.core.management.base import BaseCommand
from courses.models import Course, WeeklyModule

class Command(BaseCommand):
    help = "Add sample weekly modules to the Tamil Basics course"

    def handle(self, *args, **kwargs):
        # Get the course instance
        course_title = "Tamil Basics"
        try:
            course = Course.objects.get(title=course_title)
        except Course.DoesNotExist:
            self.stderr.write(f"Course '{course_title}' does not exist.")
            return

        # Sample weekly module data
        sample_modules = [
            {"title": "Introduction to Tamil Grammar", "description": "Basic sentence structure.", "order": 1},
            {"title": "Sangam Era Literature", "description": "Explore ancient Tamil texts.", "order": 2},
            {"title": "Tamil Festivals", "description": "Cultural celebrations in Tamil Nadu.", "order": 3},
            {"title": "Tamil Cuisine", "description": "A dive into traditional dishes.", "order": 4},
            {"title": "Tamil Nadu History", "description": "Explore the rich history of Tamil Nadu.", "order": 5},
            {"title": "Tamil Music", "description": "Dive into traditional Tamil music.", "order": 6},
            {"title": "Modern Tamil Literature", "description": "Understand modern contributions.", "order": 7},
            {"title": "Tamil Poetry", "description": "An overview of Tamil poetic forms.", "order": 8},
            {"title": "Tamil Scripts", "description": "Learn about the evolution of Tamil scripts.", "order": 9},
            {"title": "Tamil Prose", "description": "Introduction to Tamil prose forms.", "order": 10},
            {"title": "Tamil Philosophy", "description": "Philosophical texts and their impact.", "order": 11},
            {"title": "Tamil Diaspora", "description": "Tamil culture around the world.", "order": 12},
        ]

        # Add each module to the course
        for module_data in sample_modules:
            WeeklyModule.objects.create(course=course, **module_data)

        self.stdout.write(f"Sample weekly modules added to the course '{course_title}'!")
