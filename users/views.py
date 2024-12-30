from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import User, InstructorProfile, StudentProfile, Role
from .serializers import (
    UserSerializer,
    InstructorProfileSerializer,
    StudentProfileSerializer,
    EnrollAsTutorSerializer,
)
from courses.models import Enrollment
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken


# API endpoint to fetch all instructors
@api_view(['GET'])
def get_instructors(request):
    instructors = InstructorProfile.objects.all()
    serializer = InstructorProfileSerializer(instructors, many=True)
    return Response(serializer.data)


# API endpoint to fetch a specific instructor by ID
@api_view(['GET'])
def get_instructor_by_id(request, id):
    instructor = get_object_or_404(InstructorProfile, id=id)
    serializer = InstructorProfileSerializer(instructor)
    return Response(serializer.data)


# API endpoint to fetch all students
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_students(request):
    students = StudentProfile.objects.all()
    serializer = StudentProfileSerializer(students, many=True)
    return Response(serializer.data)


# API endpoint to fetch a specific student by ID
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_student_by_id(request, id):
    student = get_object_or_404(StudentProfile, id=id)
    serializer = StudentProfileSerializer(student)
    return Response(serializer.data)


# Register a new user and assign the "Student" role
@api_view(['POST'])
def register_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        with transaction.atomic():
            user = serializer.save()

            # Assign the "Student" role
            student_role, _ = Role.objects.get_or_create(
                name="Student", defaults={"description": "Default role for students"}
            )
            user.roles.add(student_role)

            # Automatically create a StudentProfile for the user
            StudentProfile.objects.get_or_create(user=user)

        return Response({"message": "User registered successfully!"}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Custom Token Obtain Pair View
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token['name'] = user.name
        token['roles'] = [role.name for role in user.roles.all()]  # Include user roles in the token
        return token


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


# Get authenticated user's information with enrollment and role data
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_info(request):
    user = request.user
    enrollments = (
        Enrollment.objects.filter(student=user.student_profile)
        .select_related("course")
        .only("course__id", "course__title", "progress")
    )
    enrollment_data = [
        {"course_id": enrollment.course.id, "course_title": enrollment.course.title, "progress": enrollment.progress}
        for enrollment in enrollments
    ]

    return Response(
        {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "roles": [role.name for role in user.roles.all()],
            "enrollments": enrollment_data,
        }
    )


# Logout by blacklisting the refresh token
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Blacklist the refresh token to log out the user.
    """
    try:
        refresh_token = request.data.get("refresh")
        token = OutstandingToken.objects.get(token=refresh_token)
        BlacklistedToken.objects.create(token=token)
        return Response({"message": "Logged out successfully."}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Enroll as Tutor API endpoint
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def enroll_as_tutor(request):
    user = request.user

    # Check if the user already has an InstructorProfile
    if hasattr(user, 'instructor_profile') and user.instructor_profile is not None:
        return Response({"error": "You are already enrolled as an instructor."}, status=status.HTTP_400_BAD_REQUEST)

    # Check if the user has the "Instructor" role without a profile
    if user.roles.filter(name="Instructor").exists():
        return Response({"error": "You have the Instructor role but no profile. Please contact support."}, status=status.HTTP_400_BAD_REQUEST)

    # Validate and create the InstructorProfile
    serializer = EnrollAsTutorSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        with transaction.atomic():
            # Assign the "Instructor" role
            instructor_role, _ = Role.objects.get_or_create(name="Instructor", defaults={"description": "Role for instructors"})
            user.roles.add(instructor_role)

            # Create the InstructorProfile
            serializer.save(user=user)

        return Response({"message": "You are now enrolled as an instructor!"}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

