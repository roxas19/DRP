from rest_framework import serializers
from .models import Course, WeeklyModule, Enrollment, Task, TaskCompletion, Resource
from users.serializers import InstructorProfileSerializer


class TaskSerializer(serializers.ModelSerializer):
    completed = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ['id', 'title', 'completed']

    def get_completed(self, obj):
        request = self.context.get('request', None)
        if request and request.user and request.user.is_authenticated:
            task_completion = TaskCompletion.objects.filter(task=obj, user=request.user).first()
            return task_completion.completed if task_completion else False
        return False


class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = ['id', 'title', 'description', 'file', 'link', 'created_at']


class WeeklyModuleSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()

    class Meta:
        model = WeeklyModule
        fields = ['id', 'title', 'description', 'order', 'status']

    def get_status(self, obj):
        request = self.context.get('request', None)
        if request and request.user and request.user.is_authenticated:
            return "Completed" if obj.all_tasks_completed_for_user(request.user) else "In Progress"
        return "Not Started"


class DetailedWeeklyModuleSerializer(serializers.ModelSerializer):
    tasks = serializers.SerializerMethodField()
    resources = ResourceSerializer(many=True, read_only=True)
    status = serializers.SerializerMethodField()

    class Meta:
        model = WeeklyModule
        fields = [
            'id',
            'title',
            'description',
            'video',
            'resources',
            'quiz_title',
            'quiz_description',
            'order',
            'tasks',
            'status',
        ]

    def get_tasks(self, obj):
        request = self.context.get('request', None)
        if request and request.user and request.user.is_authenticated:
            tasks = Task.objects.filter(module=obj)
            return TaskSerializer(tasks, many=True, context=self.context).data
        return []

    def get_status(self, obj):
        request = self.context.get('request', None)
        if request and request.user and request.user.is_authenticated:
            return "Completed" if obj.all_tasks_completed_for_user(request.user) else "In Progress"
        return "Not Started"


class CourseSerializer(serializers.ModelSerializer):
    weekly_modules = WeeklyModuleSerializer(many=True, read_only=True)
    instructors = InstructorProfileSerializer(many=True, read_only=True)

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
            'instructors',
            'created_at',
            'weekly_modules',
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request', None)
        if request:
            for module in representation.get('weekly_modules', []):
                module['status'] = WeeklyModuleSerializer(
                    instance.weekly_modules.filter(id=module['id']).first(),
                    context=self.context
                ).data.get('status')
        return representation


class EnrollmentSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)

    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'course', 'progress', 'completed_weeks', 'enrolled_on']
