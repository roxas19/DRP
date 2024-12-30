# Generated by Django 5.1.1 on 2024-12-29 15:59

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('profile_photo', models.ImageField(blank=True, null=True, upload_to='users/')),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
                ('roles', models.ManyToManyField(related_name='users', to='users.role')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='InstructorProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bio', models.TextField(blank=True, null=True)),
                ('qualification', models.CharField(max_length=255)),
                ('teaching_experience', models.IntegerField(default=0)),
                ('specialization', models.CharField(blank=True, max_length=255, null=True)),
                ('rating', models.FloatField(default=0.0)),
                ('video_intro', models.URLField(blank=True, null=True)),
                ('availability', models.CharField(blank=True, max_length=255, null=True)),
                ('languages_spoken', models.CharField(blank=True, max_length=255, null=True)),
                ('teaching_style', models.TextField(blank=True, null=True)),
                ('course_count', models.IntegerField(default=0)),
                ('achievements', models.TextField(blank=True, null=True)),
                ('certified', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('total_live_hours', models.FloatField(default=0.0)),
                ('total_streams', models.IntegerField(default=0)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='instructor_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='StudentProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('learning_goals', models.TextField(blank=True, null=True)),
                ('progress', models.JSONField(blank=True, null=True)),
                ('completed_courses_count', models.IntegerField(default=0)),
                ('achievements', models.TextField(blank=True, null=True)),
                ('preferred_language', models.CharField(blank=True, max_length=50, null=True)),
                ('timezone', models.CharField(blank=True, max_length=50, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='student_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
