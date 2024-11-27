from rest_framework import serializers
from .models import Course, WeeklyModule, Enrollment


class WeeklyModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeeklyModule
        fields = ['id', 'title', 'description', 'video', 'resources', 'quiz', 'order']


class CourseSerializer(serializers.ModelSerializer):
    weekly_modules = WeeklyModuleSerializer(many=True, read_only=True)  # Include related weekly modules

    class Meta:
        model = Course
        fields = [
            'id', 
            'title', 
            'description', 
            'image', 
            'duration', 
            'price', 
            'level', 
            'category', 
            'instructor', 
            'created_at', 
            'weekly_modules'
        ]


class EnrollmentSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)  # Include course details in enrollment data

    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'course', 'progress', 'enrolled_on']
