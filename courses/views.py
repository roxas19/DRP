from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Course, WeeklyModule, Enrollment
from .serializers import CourseSerializer, WeeklyModuleSerializer, EnrollmentSerializer
from categories.models import Category


@api_view(['GET'])
def get_courses(request):
    courses = Course.objects.all()
    serializer = CourseSerializer(courses, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_courses_by_category(request, name):
    category = get_object_or_404(Category, name__iexact=name.replace("-", " "))
    courses = Course.objects.filter(category=category)
    serializer = CourseSerializer(courses, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    serializer = CourseSerializer(course)
    return Response(serializer.data)


@api_view(['GET'])
def get_weekly_modules(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    weekly_modules = WeeklyModule.objects.filter(course=course).order_by('order')
    serializer = WeeklyModuleSerializer(weekly_modules, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_enrollments(request):
    enrollments = Enrollment.objects.all()
    serializer = EnrollmentSerializer(enrollments, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def create_enrollment(request):
    student = request.user  # Assuming the user is authenticated and represents the student
    course_id = request.data.get('course_id')
    course = get_object_or_404(Course, id=course_id)

    enrollment, created = Enrollment.objects.get_or_create(student=student, course=course)
    if not created:
        return Response({"detail": "Already enrolled in this course."}, status=400)

    serializer = EnrollmentSerializer(enrollment)
    return Response(serializer.data, status=201)
