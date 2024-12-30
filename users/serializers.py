from rest_framework import serializers
from .models import User, InstructorProfile, StudentProfile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'password', 'roles']
        extra_kwargs = {
            'password': {'write_only': True},  # To ensure password is not visible in responses
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


class InstructorProfileSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.name")
    profile_photo = serializers.ImageField(source="user.profile_photo")  # Include profile_photo

    class Meta:
        model = InstructorProfile
        fields = [
            "id",
            "user_name",
            "profile_photo",  # Add this field
            "bio",
            "qualification",
            "teaching_experience",
            "specialization",
            "rating",
            "created_at",
            "updated_at",
            "is_active",
            "certified",
            "availability",
            "languages_spoken",
        ]


class StudentProfileSerializer(serializers.ModelSerializer):
    courses_enrolled = serializers.SerializerMethodField()

    class Meta:
        model = StudentProfile
        fields = [
            'id', 'user', 'learning_goals', 'profile_photo', 'courses_enrolled',
            'progress', 'preferred_language', 'completed_courses_count', 'achievements', 'timezone'
        ]

    def get_courses_enrolled(self, obj):
        # Assuming a ManyToMany relationship or similar logic to fetch enrolled courses
        from courses.models import Enrollment
        enrollments = Enrollment.objects.filter(student=obj.user)
        return [enrollment.course.title for enrollment in enrollments]


class EnrollAsTutorSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstructorProfile
        fields = ['bio', 'qualification', 'teaching_experience', 'availability']

    def validate(self, data):
        user = self.context['request'].user
        # Check if the user is already an instructor
        if user.is_instructor():
            raise serializers.ValidationError("You are already enrolled as an instructor.")
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        # Explicitly remove any existing user field from validated_data to avoid conflicts
        validated_data.pop('user', None)
        # Create the InstructorProfile
        instructor_profile = InstructorProfile.objects.create(user=user, **validated_data)
        return instructor_profile

