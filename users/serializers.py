# users/serializers.py
from rest_framework import serializers
from .models import User, Instructor, Student


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}  # To ensure password is not visible in responses
        }

    def create(self, validated_data):
        # Custom user creation logic to handle password hashing
        user = User.objects.create(
            name=validated_data['name'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class InstructorSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = Instructor
        fields = ['id', 'user_name', 'bio', 'qualification', 'teaching_experience', 'specialization', 'rating']

    def get_user_name(self, obj):
        return obj.user.name  # Access the 'name' field from the related User object

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'user', 'learning_goals', 'profile_photo', 'courses_enrolled', 'activity_level', 'achievements', 'preferred_language', 'completed_courses_count']
