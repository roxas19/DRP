# Generated by Django 5.1.1 on 2024-12-29 15:59

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('courses', '0001_initial'),
        ('users', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='instructors',
            field=models.ManyToManyField(related_name='courses', to='users.instructorprofile'),
        ),
        migrations.AddField(
            model_name='enrollment',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='enrollments', to='courses.course'),
        ),
        migrations.AddField(
            model_name='enrollment',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.studentprofile'),
        ),
        migrations.AddField(
            model_name='taskcompletion',
            name='task',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='completions', to='courses.task'),
        ),
        migrations.AddField(
            model_name='taskcompletion',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='task_completions', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='weeklymodule',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='weekly_modules', to='courses.course'),
        ),
        migrations.AddField(
            model_name='task',
            name='module',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='courses.weeklymodule'),
        ),
        migrations.AddField(
            model_name='resource',
            name='module',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='resources', to='courses.weeklymodule'),
        ),
        migrations.AlterUniqueTogether(
            name='enrollment',
            unique_together={('student', 'course')},
        ),
        migrations.AlterUniqueTogether(
            name='taskcompletion',
            unique_together={('user', 'task')},
        ),
    ]
