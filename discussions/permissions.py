from rest_framework.permissions import BasePermission

class IsInstructorOrAuthor(BasePermission):
    """
    Allow only instructors or the author to perform edits/deletions.
    """
    def has_object_permission(self, request, view, obj):
        return request.user == obj.author or request.user.is_instructor()
