# Generated by Django 5.1.1 on 2024-12-29 15:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('courses', '0001_initial'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='YouTubeToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('access_token', models.TextField()),
                ('refresh_token', models.TextField()),
                ('expires_at', models.DateTimeField(help_text='Access token expiry time.')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Livestream',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('playlist_id', models.CharField(help_text='YouTube Playlist ID for archiving livestreams', max_length=255)),
                ('broadcast_id', models.CharField(help_text='Unique YouTube Broadcast ID', max_length=255, unique=True)),
                ('stream_key', models.CharField(blank=True, help_text='RTMP Stream Key', max_length=255, null=True)),
                ('rtmp_url', models.CharField(blank=True, help_text='RTMP Ingestion URL', max_length=255, null=True)),
                ('status', models.CharField(choices=[('SCHEDULED', 'Scheduled'), ('LIVE', 'Live'), ('COMPLETED', 'Completed')], default='SCHEDULED', help_text='Current status of the livestream', max_length=20)),
                ('scheduled_start_time', models.DateTimeField(blank=True, null=True)),
                ('started_at', models.DateTimeField(blank=True, null=True)),
                ('ended_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('view_count', models.PositiveIntegerField(default=0, help_text='Total number of views')),
                ('average_watch_time', models.FloatField(default=0.0, help_text='Average watch time in minutes')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='livestreams', to='courses.course')),
                ('instructor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='livestreams', to='users.instructorprofile')),
                ('weekly_module', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='livestream', to='courses.weeklymodule')),
            ],
        ),
    ]
