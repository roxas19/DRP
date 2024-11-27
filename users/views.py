# users/views.py
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import User, Instructor, Student
from .serializers import UserSerializer, InstructorSerializer, StudentSerializer
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


# API endpoint to fetch all instructors
@api_view(['GET'])
def get_instructors(request):
    instructors = Instructor.objects.all()
    serializer = InstructorSerializer(instructors, many=True)
    return Response(serializer.data)

# API endpoint to fetch a specific instructor by ID
@api_view(['GET'])
def get_instructor_by_id(request, id):
    instructor = get_object_or_404(Instructor, id=id)
    serializer = InstructorSerializer(instructor)
    return Response(serializer.data)

# API endpoint to fetch all students
@api_view(['GET'])
def get_students(request):
    students = Student.objects.all()
    serializer = StudentSerializer(students, many=True)
    return Response(serializer.data)

# API endpoint to fetch a specific student by ID
@api_view(['GET'])
def get_student_by_id(request, id):
    student = get_object_or_404(Student, id=id)
    serializer = StudentSerializer(student)
    return Response(serializer.data)


@api_view(['POST'])
def register_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'User registered successfully!'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims here
        token['name'] = user.name
        return token

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
