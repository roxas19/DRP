# courses/management/commands/seed_courses.py
from django.core.management.base import BaseCommand
from courses.models import Course, Week
from categories.models import Category
from users.models import Instructor, User  # Import User model

class Command(BaseCommand):
    help = 'Seed the database with sample course and weekly content for Tamil Basics'

    def handle(self, *args, **options):
        # Create or get the category and instructor
        category, _ = Category.objects.get_or_create(name="Tamil Language")
        
        # Replace 'username' with 'name' or 'email' (based on your model's fields)
        user, _ = User.objects.get_or_create(
            name="Sample Instructor",  # Adjust the field name here as needed
            defaults={
                "email": "sample@instructor.com",
                "is_instructor": True
            }
        )

        instructor, _ = Instructor.objects.get_or_create(user=user)

        # Create the Course
        course, created = Course.objects.get_or_create(
            title="Tamil Basics",
            defaults={
                "description": "A foundational course in Tamil language for beginners.",
                "image": "path/to/sample_image.jpg",  # Adjust path to an actual image path if needed
                "duration": "10 Weeks",
                "price": 99.99,
                "level": "Beginner",
                "category": category,
                "instructor": instructor,
            }
        )

        # Define the weekly data
        weeks_data = [
            {"title": "Week 1: Introduction to Tamil Script and Sounds", "description": "Learn the basics of Tamil script...", "order": 1},
            {"title": "Week 2: Basic Greetings and Everyday Phrases", "description": "Explore common greetings and phrases...", "order": 2},
            {"title": "Week 3: Family and Relationships Vocabulary", "description": "Understand vocabulary related to family members...", "order": 3},
            {"title": "Week 4: Numbers and Counting", "description": "Learn to count from 1 to 100...", "order": 4},
            {"title": "Week 5: Days, Months, and Time Expressions", "description": "Familiarize yourself with days, months...", "order": 5},
            {"title": "Week 6: Common Verbs and Simple Sentences", "description": "Learn frequently used verbs...", "order": 6},
            {"title": "Week 7: Food and Dining Vocabulary", "description": "Master essential vocabulary for Tamil cuisine...", "order": 7},
            {"title": "Week 8: Colors, Shapes, and Adjectives", "description": "Study vocabulary for colors, shapes...", "order": 8},
            {"title": "Week 9: Simple Conversations and Role-Playing", "description": "Engage in simple dialogues...", "order": 9},
            {"title": "Week 10: Tamil Culture and Expressions", "description": "Learn culturally relevant expressions...", "order": 10},
        ]

        # Create weeks for the course
        for week_data in weeks_data:
            Week.objects.get_or_create(course=course, **week_data)

        self.stdout.write(self.style.SUCCESS('Successfully seeded the Tamil Basics course and weekly content'))
