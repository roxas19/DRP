from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from .models import Course, WeeklyModule, Enrollment, Task, TaskCompletion, Resource, User
from .serializers import (
    CourseSerializer,
    WeeklyModuleSerializer,
    DetailedWeeklyModuleSerializer,
    EnrollmentSerializer,
    TaskSerializer,
    ResourceSerializer,
)
from organisations.models import Category

# Helper function to check enrollment and instructor access
def is_instructor_of_course(user, course):
    """
    Check if the user is one of the instructors of the course.
    """
    return user.is_instructor() and course.instructors.filter(user=user).exists()

def is_enrolled(user, course):
    """
    Check if the user is enrolled in a course or is an instructor.
    """
    if user.is_anonymous:
        return False
    if is_instructor_of_course(user, course):
        return True
    return Enrollment.objects.filter(student=user.student_profile, course=course).exists()

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_instructor_courses(request):
    print(f"User: {request.user}, Is Instructor: {hasattr(request.user, 'is_instructor')}")
    print(f"User Roles: {request.user.roles.all()}")

    if not request.user.is_instructor():
        return Response({"detail": "You are not authorized to access this."}, status=status.HTTP_403_FORBIDDEN)

    courses = Course.objects.filter(instructors__user=request.user)
    serializer = CourseSerializer(courses, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
def get_courses(request):
    """
    Fetch all courses.
    """
    courses = Course.objects.all()
    serializer = CourseSerializer(courses, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
def get_courses_by_category(request, name):
    """
    Fetch courses by category.
    """
    category = get_object_or_404(Category, name__iexact=name.replace("-", " "))
    courses = Course.objects.filter(category=category)
    serializer = CourseSerializer(courses, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
def get_course_detail(request, course_id):
    """
    Fetch detailed information about a specific course.
    """
    course = get_object_or_404(Course, id=course_id)
    serializer = CourseSerializer(course, context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_weekly_modules(request, course_id):
    """
    Fetch all weekly modules for a specific course for the logged-in user or instructor.
    """
    course = get_object_or_404(Course, id=course_id)

    if not is_enrolled(request.user, course):
        return Response({"detail": "You are not authorized to access this course."}, status=status.HTTP_403_FORBIDDEN)

    weekly_modules = WeeklyModule.objects.filter(course=course).order_by('order')
    serializer = WeeklyModuleSerializer(weekly_modules, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_weekly_module_details(request, course_id, week_number):
    """
    Fetch detailed information about a specific weekly module.
    """
    course = get_object_or_404(Course, id=course_id)

    if not is_enrolled(request.user, course):
        return Response({"detail": "You are not authorized to access this course."}, status=status.HTTP_403_FORBIDDEN)

    weekly_module = get_object_or_404(WeeklyModule, course=course, order=week_number)
    serializer = DetailedWeeklyModuleSerializer(weekly_module, context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_tasks(request, course_id, week_number):
    """
    Fetch all tasks for the logged-in user for a specific weekly module.
    """
    course = get_object_or_404(Course, id=course_id)

    if not is_enrolled(request.user, course):
        return Response({"detail": "You are not authorized to access this course."}, status=status.HTTP_403_FORBIDDEN)

    weekly_module = get_object_or_404(WeeklyModule, course=course, order=week_number)
    tasks = Task.objects.filter(module=weekly_module)
    serializer = TaskSerializer(tasks, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_task_completed(request, course_id, week_number, task_id):
    """
    Toggle the completion status of a specific task within a weekly module for the logged-in user.
    """
    course = get_object_or_404(Course, id=course_id)

    if not is_enrolled(request.user, course):
        return Response({"detail": "You are not authorized to access this course."}, status=status.HTTP_403_FORBIDDEN)

    weekly_module = get_object_or_404(WeeklyModule, course=course, order=week_number)
    task = get_object_or_404(Task, id=task_id, module=weekly_module)
    task_completion, created = TaskCompletion.objects.get_or_create(user=request.user, task=task)

    # Validate and toggle the "completed" status
    completed = request.data.get("completed")
    if not isinstance(completed, bool):
        return Response({"detail": "Invalid value for 'completed'. Must be a boolean."}, status=status.HTTP_400_BAD_REQUEST)

    task_completion.completed = completed
    task_completion.completed_at = now() if completed else None
    task_completion.save()

    # Check if the module is completed for the user
    if weekly_module.all_tasks_completed_for_user(request.user):
        weekly_module.mark_completed_for_user(request.user)

    return Response({
        "detail": "Task status updated.",
        "task": {"id": task.id, "completed": task_completion.completed}
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_task(request, course_id, week_number):
    """
    Create a new task in a specific weekly module.
    """
    course = get_object_or_404(Course, id=course_id)
    if not is_instructor_of_course(request.user, course):
        return Response({"detail": "You are not authorized to add tasks to this course."}, status=status.HTTP_403_FORBIDDEN)

    weekly_module = get_object_or_404(WeeklyModule, course=course, order=week_number)
    serializer = TaskSerializer(data=request.data)
    if serializer.is_valid():
        task = serializer.save(module=weekly_module)  # Save the task
        
        # Create TaskCompletion for all enrolled users
        enrolled_users = Enrollment.objects.filter(course=course).values_list('student__user', flat=True)
        for user_id in enrolled_users:
            TaskCompletion.objects.get_or_create(user_id=user_id, task=task)

        # Recalculate module status for all enrolled users
        for user_id in enrolled_users:
            if weekly_module.all_tasks_completed_for_user(User.objects.get(id=user_id)):
                weekly_module.mark_completed_for_user(User.objects.get(id=user_id))

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_task(request, course_id, week_number, task_id):
    """
    Update an existing task in a specific weekly module.
    """
    course = get_object_or_404(Course, id=course_id)
    if not is_instructor_of_course(request.user, course):
        return Response({"detail": "You are not authorized to update tasks in this course."}, status=status.HTTP_403_FORBIDDEN)

    task = get_object_or_404(Task, id=task_id, module__course=course, module__order=week_number)
    serializer = TaskSerializer(task, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_task(request, course_id, week_number, task_id):
    """
    Delete a task from a specific weekly module.
    """
    course = get_object_or_404(Course, id=course_id)
    if not is_instructor_of_course(request.user, course):
        return Response({"detail": "You are not authorized to delete tasks from this course."}, status=status.HTTP_403_FORBIDDEN)

    task = get_object_or_404(Task, id=task_id, module__course=course, module__order=week_number)
    task.delete()
    return Response({"detail": "Task deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_resources(request, course_id, week_number):
    """
    Fetch all resources for a specific weekly module.
    """
    course = get_object_or_404(Course, id=course_id)
    weekly_module = get_object_or_404(WeeklyModule, course=course, order=week_number)
    resources = Resource.objects.filter(module=weekly_module)
    serializer = ResourceSerializer(resources, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_resource(request, course_id, week_number):
    """
    Add a new resource to a specific weekly module.
    """
    course = get_object_or_404(Course, id=course_id)
    if not is_instructor_of_course(request.user, course):
        return Response({"detail": "You are not authorized to add resources to this course."}, status=status.HTTP_403_FORBIDDEN)

    weekly_module = get_object_or_404(WeeklyModule, course=course, order=week_number)
    serializer = ResourceSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(module=weekly_module)  # Associate resource with the correct module
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_resource(request, course_id, week_number, resource_id):
    """
    Update an existing resource in a specific weekly module.
    """
    course = get_object_or_404(Course, id=course_id)
    if not is_instructor_of_course(request.user, course):
        return Response({"detail": "You are not authorized to update resources in this course."}, status=status.HTTP_403_FORBIDDEN)

    resource = get_object_or_404(Resource, id=resource_id, module__course=course, module__order=week_number)
    serializer = ResourceSerializer(resource, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_resource(request, course_id, week_number, resource_id):
    """
    Delete a resource from a specific weekly module.
    """
    course = get_object_or_404(Course, id=course_id)
    if not is_instructor_of_course(request.user, course):
        return Response({"detail": "You are not authorized to delete resources from this course."}, status=status.HTTP_403_FORBIDDEN)

    resource = get_object_or_404(Resource, id=resource_id, module__course=course, module__order=week_number)
    resource.delete()
    return Response({"detail": "Resource deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_enrollment(request):
    """
    Create an enrollment for the logged-in user in a specific course.
    """
    if not hasattr(request.user, 'student_profile'):
        return Response({"detail": "Student profile not found."}, status=status.HTTP_400_BAD_REQUEST)

    student = request.user.student_profile
    course_id = request.data.get('course_id')
    course = get_object_or_404(Course, id=course_id)

    enrollment, created = Enrollment.objects.get_or_create(student=student, course=course)
    if not created:
        return Response({"detail": "Already enrolled in this course."}, status=status.HTTP_400_BAD_REQUEST)

    # Create task completions for all modules in the course
    for module in course.weekly_modules.all():
        for task in module.tasks.all():
            TaskCompletion.objects.get_or_create(user=request.user, task=task)

    serializer = EnrollmentSerializer(enrollment, context={'request': request})
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_enrollments(request):
    """
    Fetch all enrollments for the logged-in user.
    """
    enrollments = Enrollment.objects.filter(student=request.user.student_profile)
    serializer = EnrollmentSerializer(enrollments, many=True, context={'request': request})
    return Response(serializer.data)
