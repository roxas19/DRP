import logging  # Import for logging
from googleapiclient.errors import HttpError  # Import for YouTube API errors
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from django.conf import settings
from django.shortcuts import redirect
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils.timezone import now
from .models import Livestream
from .serializers import LivestreamCreateSerializer, LivestreamSerializer
from .utils import notify_websocket  # Import the WebSocket helper
from users.models import InstructorProfile
from courses.models import Course, WeeklyModule
from .models import YouTubeToken
import datetime
from google.auth.transport.requests import Request


logger = logging.getLogger(__name__)

# Helper: Fetch YouTube API Client with Updated Token
def get_youtube_client():
    """
    Fetch the authenticated YouTube client, refreshing the token if expired.
    If no token exists, redirect to OAuth flow for authentication.
    """
    token = YouTubeToken.objects.first()
    
    # If no token exists, redirect to OAuth flow
    if not token:
        raise Exception("YouTube account not linked. Visit /api/ytlive/oauth/ to authenticate.")

    # Build credentials using the stored token
    credentials = Credentials(
        token=token.access_token,
        refresh_token=token.refresh_token,
        client_id=settings.YOUTUBE_CLIENT_ID,
        client_secret=settings.YOUTUBE_CLIENT_SECRET,
        token_uri="https://oauth2.googleapis.com/token",
    )

    # Refresh the token if expired
    if credentials.expired:
        credentials.refresh(Request())
        token.access_token = credentials.token
        token.expires_at = now() + datetime.timedelta(seconds=3600)
        token.save()

    return build("youtube", "v3", credentials=credentials)


def youtube_auth(request):
    """
    OAuth flow to authenticate the platform's YouTube account.
    """
    flow = Flow.from_client_config(
        client_config={
            "web": {
                "client_id": settings.YOUTUBE_CLIENT_ID,
                "client_secret": settings.YOUTUBE_CLIENT_SECRET,
                "redirect_uris": [settings.YOUTUBE_REDIRECT_URI],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=settings.YOUTUBE_API_SCOPES,
    )
    flow.redirect_uri = settings.YOUTUBE_REDIRECT_URI

    if 'code' not in request.GET:
        # Redirect to Google's OAuth consent screen
        auth_url, _ = flow.authorization_url(prompt='consent')
        return redirect(auth_url)

    # Fetch tokens after user authorizes the app
    flow.fetch_token(authorization_response=request.build_absolute_uri())
    credentials = flow.credentials

    # Save the credentials to the database
    YouTubeToken.objects.update_or_create(
        id=1,  # Single record
        defaults={
            "access_token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "expires_at": credentials.expiry,  # Use credentials.expiry directly
        }
    )

    return JsonResponse({
        "message": "YouTube account linked successfully!",
        "access_token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "expires_at": credentials.expiry,
    })


# Step 2: Create a Livestream
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_livestream(request):
    """
    Create a new YouTube livestream and bind it to a course and weekly module.
    """
    serializer = LivestreamCreateSerializer(data=request.data, context={'request': request})
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data

    try:
        youtube = get_youtube_client()

        # Step 1: Create a YouTube Broadcast
        broadcast = youtube.liveBroadcasts().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": data['title'],
                    "description": data['description'],
                    "scheduledStartTime": data['scheduled_start_time'].isoformat(),
                },
                "status": {"privacyStatus": "public"},
            },
        ).execute()

        # Step 2: Create the Livestream for RTMP
        stream = youtube.liveStreams().insert(
            part="snippet,cdn",
            body={
                "snippet": {"title": f"Stream for {broadcast['id']}"},
                "cdn": {
                    "frameRate": "30fps",
                    "ingestionType": "rtmp",
                    "resolution": "720p",
                },
            },
        ).execute()

        # Step 3: Bind the broadcast to the livestream
        youtube.liveBroadcasts().bind(
            part="id,contentDetails",
            id=broadcast['id'],
            streamId=stream['id'],
        ).execute()

        # Save Livestream to the database
        livestream = Livestream.objects.create(
            title=data['title'],
            description=data['description'],
            instructor=request.user.instructor_profile,
            course=data['course'],
            weekly_module=data['weekly_module'],
            playlist_id="your-course-playlist-id",
            broadcast_id=broadcast['id'],
            stream_key=stream['cdn']['ingestionInfo']['streamName'],
            rtmp_url=stream['cdn']['ingestionInfo']['ingestionAddress'],
            status="SCHEDULED",
            scheduled_start_time=data['scheduled_start_time'],
        )

        return Response(LivestreamSerializer(livestream).data, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_livestreams_for_course(request, course_id):
    """
    Fetch all livestreams associated with a course.
    """
    try:
        # Validate course existence
        course = Course.objects.get(id=course_id)

        # Check if the user is authorized
        if not (
            request.user.is_instructor() or
            course.enrollments.filter(student=request.user.student_profile).exists()
        ):
            return Response(
                {"error": "You are not authorized to access this course's livestreams."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Fetch and serialize livestreams
        livestreams = Livestream.objects.filter(course=course).order_by('-scheduled_start_time')
        serializer = LivestreamSerializer(livestreams, many=True)
        return Response(serializer.data)

    except Course.DoesNotExist:
        return Response({"error": "Course not found."}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_livestream_details(request, livestream_id):
    """
    Fetch details of a specific livestream.
    """
    try:
        # Fetch the livestream
        livestream = Livestream.objects.select_related('course').filter(id=livestream_id).first()
        if not livestream:
            return Response({"error": "Livestream not found."}, status=status.HTTP_404_NOT_FOUND)

        # Validate the user's access
        course = livestream.course
        if not (
            request.user.is_instructor() or
            course.enrollments.filter(student=request.user.student_profile).exists()
        ):
            return Response(
                {"error": "You are not authorized to access this livestream."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Serialize and return the livestream details
        serializer = LivestreamSerializer(livestream)
        return Response(serializer.data)

    except Course.DoesNotExist:
        return Response({"error": "Course not found."}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_livestream(request, livestream_id):
    """
    Start a YouTube livestream and update its status in the database.
    """
    try:
        livestream = Livestream.objects.get(id=livestream_id, instructor=request.user.instructor_profile)

        youtube = get_youtube_client()
        youtube.liveBroadcasts().transition(
            broadcastStatus="live",
            id=livestream.broadcast_id,
            part="status"
        ).execute()

        livestream.status = "LIVE"
        livestream.started_at = now()
        livestream.save()

        # Notify via WebSocket
        notify_websocket(f"livestream_{livestream.id}", {
            "status": "LIVE",
            "message": "The livestream has started.",
            "livestream_id": livestream.id
        })

        # Log event
        logger.info(f"Livestream {livestream.id} started by instructor {request.user.id}.")

        return Response({
            "message": "Livestream started successfully!",
            "status": "LIVE",
            "livestream_id": livestream.id,
            "rtmp_url": livestream.rtmp_url,
            "stream_key": livestream.stream_key
        }, status=status.HTTP_200_OK)

    except Livestream.DoesNotExist:
        return Response({
            "error": "Livestream not found or access denied.",
            "details": "Ensure you are the instructor of this livestream."
        }, status=status.HTTP_404_NOT_FOUND)

    except HttpError as e:
        return Response({
            "error": "YouTube API error.",
            "details": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        return Response({
            "error": "An unexpected error occurred.",
            "details": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def end_livestream(request, livestream_id):
    """
    End a YouTube livestream and update its status in the database.
    """
    try:
        livestream = Livestream.objects.get(id=livestream_id, instructor=request.user.instructor_profile)

        youtube = get_youtube_client()
        youtube.liveBroadcasts().transition(
            broadcastStatus="complete",
            id=livestream.broadcast_id,
            part="status"
        ).execute()

        livestream.status = "COMPLETED"
        livestream.ended_at = now()
        livestream.save()

        # Notify via WebSocket
        notify_websocket(f"livestream_{livestream.id}", {
            "status": "COMPLETED",
            "message": "The livestream has ended.",
            "livestream_id": livestream.id
        })

        # Log event
        logger.info(f"Livestream {livestream.id} ended by instructor {request.user.id}.")

        return Response({
            "message": "Livestream ended successfully!",
            "status": "COMPLETED",
            "livestream_id": livestream.id
        }, status=status.HTTP_200_OK)

    except Livestream.DoesNotExist:
        return Response({
            "error": "Livestream not found or access denied.",
            "details": "Ensure you are the instructor of this livestream."
        }, status=status.HTTP_404_NOT_FOUND)

    except HttpError as e:
        return Response({
            "error": "YouTube API error.",
            "details": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        return Response({
            "error": "An unexpected error occurred.",
            "details": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

