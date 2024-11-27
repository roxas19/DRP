from django.core.management.base import BaseCommand
from courses.models import Course
from categories.models import Category
from users.models import Instructor

class Command(BaseCommand):
    help = 'Add sample courses data'

    def handle(self, *args, **kwargs):
        # Fetch categories by name
        try:
            tamil_basics_category = Category.objects.get(name="Tamil Basics")
            culinary_arts_category = Category.objects.get(name="Culinary Arts")
            performance_arts_category = Category.objects.get(name="Performance Arts")
        except Category.DoesNotExist as e:
            self.stdout.write(self.style.ERROR(f"Category not found: {e}"))
            return

        # Fetch instructors by ID (Adjust IDs based on your existing data)
        try:
            instructor_1 = Instructor.objects.get(id=10)
            instructor_2 = Instructor.objects.get(id=11)
            instructor_3 = Instructor.objects.get(id=12)
        except Instructor.DoesNotExist as e:
            self.stdout.write(self.style.ERROR(f"Instructor not found: {e}"))
            return

        # Create courses with categories and instructors
        Course.objects.get_or_create(
            title="Introduction to Tamil Language",
            defaults={
                "description": "Learn the basics of Tamil language.",
                "image": "courses/IMG_2246.jpg",
                "duration": "10 weeks",
                "price": 50.00,
                "level": "Beginner",
                "category": tamil_basics_category,
                "instructor": instructor_1
            }
        )

        Course.objects.get_or_create(
            title="Traditional Tamil Cooking",
            defaults={
                "description": "Explore traditional Tamil dishes.",
                "image": "courses/IMG_2247.jpg",
                "duration": "8 weeks",
                "price": 60.00,
                "level": "Intermediate",
                "category": culinary_arts_category,
                "instructor": instructor_2
            }
        )

        Course.objects.get_or_create(
            title="Tamil Dance Fundamentals",
            defaults={
                "description": "Learn the fundamentals of Tamil dance.",
                "image": "courses/IMG_2248.jpg",
                "duration": "12 weeks",
                "price": 70.00,
                "level": "Beginner",
                "category": performance_arts_category,
                "instructor": instructor_3
            }
        )

        self.stdout.write(self.style.SUCCESS('Successfully added sample courses'))
