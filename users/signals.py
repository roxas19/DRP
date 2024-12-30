from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import InstructorProfile, Role

@receiver(post_delete, sender=InstructorProfile)
def remove_instructor_role(sender, instance, **kwargs):
    """
    Remove the "Instructor" role from a user when their InstructorProfile is deleted.
    """
    instructor_role = Role.objects.filter(name="Instructor").first()
    if instructor_role and instance.user.roles.filter(id=instructor_role.id).exists():
        instance.user.roles.remove(instructor_role)
