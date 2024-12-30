from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .serializers import DiscussionPostSerializer, CommentSerializer
from courses.models import WeeklyModule, Course
from courses.views import is_enrolled  # Helper function
from django.contrib.contenttypes.models import ContentType
from .models import DiscussionPost, Comment, Flag
from rest_framework.pagination import PageNumberPagination
from .permissions import IsInstructorOrAuthor
from django.db.models import Count

# Helper Function: Check if a user is the author or an instructor
def is_author_or_instructor(user, instance):
    return user == instance.author or user.is_instructor()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_posts(request, course_id, week_number):
    """
    Fetch all discussion posts for a specific course and module order (week), grouped with their comments.
    """
    try:
        # Fetch weekly module based on course_id and order
        weekly_module = WeeklyModule.objects.get(course_id=course_id, order=week_number)

        # Fetch discussion posts for the module
        posts = DiscussionPost.objects.filter(weekly_module=weekly_module).prefetch_related('comments')

        # Pagination
        paginator = PageNumberPagination()
        paginator.page_size = 10  # Adjust page size if needed
        paginated_posts = paginator.paginate_queryset(posts, request)

        # Serialize posts with context for user-specific flag status
        serialized_posts = DiscussionPostSerializer(
            paginated_posts,
            many=True,
            context={'request': request}
        )

        return paginator.get_paginated_response(serialized_posts.data)
    except WeeklyModule.DoesNotExist:
        return Response({"error": "Weekly module not found for the specified course and module order."}, status=404)
    except DiscussionPost.DoesNotExist:
        return Response({"error": "No posts found for the specified module."}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=400)


# Fetch details of a single post, including its comments
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_post_detail(request, post_id):
    """
    Fetch the details of a single discussion post, including its comments.
    Excludes comments flagged more than 10 times.
    """
    post = get_object_or_404(DiscussionPost, id=post_id)
    weekly_module = post.weekly_module
    if not is_enrolled(request.user, weekly_module.course):
        return Response({"detail": "You are not enrolled in this course."}, status=status.HTTP_403_FORBIDDEN)

    # Fetch comments, excluding those flagged more than twice
    comments = Comment.objects.filter(
        post=post,
        flag_count__lte=10  # Exclude comments flagged more than 10 times
    ).order_by('created_at')

    # Serialize post and comments
    serializer = DiscussionPostSerializer(post, context={'request': request})
    data = serializer.data
    data['comments'] = CommentSerializer(comments, many=True, context={'request': request}).data
    return Response(data, status=status.HTTP_200_OK)


# Create a new discussion post
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_post(request):
    """
    Allow an enrolled student or instructor to create a discussion post.
    """
    serializer = DiscussionPostSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        weekly_module = serializer.validated_data['weekly_module']
        if not is_enrolled(request.user, weekly_module.course):
            return Response({"detail": "You are not enrolled in this course."}, status=status.HTTP_403_FORBIDDEN)

        serializer.save(author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Add a comment to a discussion post
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_comment(request):
    """
    Allow users to add a comment to a discussion post.
    """
    serializer = CommentSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        post = serializer.validated_data['post']
        weekly_module = post.weekly_module
        if not is_enrolled(request.user, weekly_module.course):
            return Response({"detail": "You are not enrolled in this course."}, status=status.HTTP_403_FORBIDDEN)

        serializer.save(author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Edit an existing post
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def edit_post(request, post_id):
    """
    Allow the author or an instructor to edit a discussion post.
    """
    post = get_object_or_404(DiscussionPost, id=post_id)
    if not is_author_or_instructor(request.user, post):
        return Response({"detail": "You do not have permission to edit this post."}, status=status.HTTP_403_FORBIDDEN)

    serializer = DiscussionPostSerializer(post, data=request.data, partial=True, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Delete an existing post
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_post(request, post_id):
    """
    Allow the author or an instructor to delete a discussion post.
    """
    post = get_object_or_404(DiscussionPost, id=post_id)
    if not is_author_or_instructor(request.user, post):
        return Response({"detail": "You do not have permission to delete this post."}, status=status.HTTP_403_FORBIDDEN)

    post.delete()
    return Response({"detail": "Post deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


# Edit an existing comment
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def edit_comment(request, comment_id):
    """
    Allow the author or an instructor to edit a comment.
    """
    comment = get_object_or_404(Comment, id=comment_id)
    if not is_author_or_instructor(request.user, comment):
        return Response({"detail": "You do not have permission to edit this comment."}, status=status.HTTP_403_FORBIDDEN)

    serializer = CommentSerializer(comment, data=request.data, partial=True, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Delete an existing comment
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_comment(request, comment_id):
    """
    Allow the author or an instructor to delete a comment.
    """
    comment = get_object_or_404(Comment, id=comment_id)
    if not is_author_or_instructor(request.user, comment):
        return Response({"detail": "You do not have permission to delete this comment."}, status=status.HTTP_403_FORBIDDEN)

    comment.delete()
    return Response({"detail": "Comment deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def flag_post(request, post_id):
    post = get_object_or_404(DiscussionPost, id=post_id)
    content_type = ContentType.objects.get_for_model(DiscussionPost)

    # Check if the flag already exists
    existing_flag = Flag.objects.filter(
        user=request.user,
        content_type=content_type,
        object_id=post_id
    )

    if existing_flag.exists():
        # Remove the flag (unflagging)
        existing_flag.delete()
        post.flag_count = Flag.objects.filter(content_type=content_type, object_id=post_id).count()
        post.save()
        user_flagged = False
    else:
        # Add a new flag
        Flag.objects.create(user=request.user, content_object=post)
        post.flag_count = Flag.objects.filter(content_type=content_type, object_id=post_id).count()
        post.save()
        user_flagged = True

    # Return only necessary fields
    return Response({
        "id": post.id,
        "user_flagged": user_flagged,
        "flag_count": post.flag_count
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def flag_comment(request, comment_id):
    """
    Toggles the flag state for a comment and returns updated state.
    """
    comment = get_object_or_404(Comment, id=comment_id)
    content_type = ContentType.objects.get_for_model(Comment)

    # Check if the flag already exists
    existing_flag = Flag.objects.filter(
        user=request.user,
        content_type=content_type,
        object_id=comment_id
    )

    if existing_flag.exists():
        # Remove the flag (unflagging)
        existing_flag.delete()
        comment.flag_count = Flag.objects.filter(content_type=content_type, object_id=comment_id).count()
        comment.save()
        user_flagged = False
    else:
        # Add a new flag
        Flag.objects.create(user=request.user, content_object=comment)
        comment.flag_count = Flag.objects.filter(content_type=content_type, object_id=comment_id).count()
        comment.save()
        user_flagged = True

    # Return only necessary fields
    return Response({
        "id": comment.id,
        "user_flagged": user_flagged,
        "flag_count": comment.flag_count
    })
from rest_framework.pagination import PageNumberPagination

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_flagged_content(request, course_id):
    """
    Fetch flagged or all posts and their flagged comments for moderation.
    Supports pagination and filtering via query parameters.
    """
    if not request.user.is_instructor():
        return Response({"detail": "You do not have permission to view this content."}, status=status.HTTP_403_FORBIDDEN)

    # Query Parameters
    flagged_only = request.query_params.get('flagged_only', 'false').lower() == 'true'

    # Fetch posts for the course
    posts_query = DiscussionPost.objects.filter(weekly_module__course_id=course_id)
    if flagged_only:
        posts_query = posts_query.filter(flag_count__gt=2)  # Only flagged posts

    # Pagination
    paginator = PageNumberPagination()
    paginator.page_size = 10  # Customize the page size as needed
    paginated_posts = paginator.paginate_queryset(posts_query, request)

    # Serialize posts and include flagged comments
    data = []
    for post in paginated_posts:
        serialized_post = DiscussionPostSerializer(post, context={'request': request}).data
        if flagged_only:
            # Include only flagged comments
            flagged_comments = Comment.objects.filter(post=post, flag_count__gt=2)
        else:
            # Include all comments
            flagged_comments = Comment.objects.filter(post=post)
        serialized_post['comments'] = CommentSerializer(flagged_comments, many=True, context={'request': request}).data
        data.append(serialized_post)

    return paginator.get_paginated_response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_comments_for_post(request, post_id):
    """
    Fetch all comments for a specific discussion post.
    Supports optional filtering for flagged comments only.
    """
    # Query Parameters
    flagged_only = request.query_params.get('flagged_only', 'false').lower() == 'true'

    # Fetch the post
    post = get_object_or_404(DiscussionPost, id=post_id)

    # Ensure the user is enrolled in the course associated with the post
    weekly_module = post.weekly_module
    if not is_enrolled(request.user, weekly_module.course):
        return Response({"detail": "You are not enrolled in this course."}, status=status.HTTP_403_FORBIDDEN)

    # Fetch comments
    comments_query = Comment.objects.filter(post=post)
    if flagged_only:
        comments_query = comments_query.filter(flag_count__gt=2)  # Only flagged comments

    # Serialize and return the comments
    serializer = CommentSerializer(comments_query, many=True, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def reset_flag_count(request, content_type, object_id):
    """
    Reset flag count for a post or comment.
    """
    if not request.user.is_instructor():
        return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

    # Get the content type
    try:
        model = ContentType.objects.get(model=content_type).model_class()
    except ContentType.DoesNotExist:
        return Response({"detail": "Invalid content type."}, status=status.HTTP_400_BAD_REQUEST)

    # Fetch the object (DiscussionPost or Comment)
    try:
        instance = model.objects.get(id=object_id)
    except model.DoesNotExist:
        return Response({"detail": "Object not found."}, status=status.HTTP_404_NOT_FOUND)

    # Delete all related flags
    Flag.objects.filter(content_type=ContentType.objects.get_for_model(model), object_id=object_id).delete()

    # Reset the flag_count field
    instance.flag_count = 0
    instance.save()

    return Response({
        "detail": "Flag count reset successfully.",
        "id": instance.id,
        "flag_count": instance.flag_count,
        "type": content_type
    }, status=status.HTTP_200_OK)



@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def toggle_hidden(request, content_type, object_id):
    """
    Toggle hidden status for a post or comment.
    """
    try:
        if content_type == 'discussionpost':
            instance = DiscussionPost.objects.get(id=object_id)
        elif content_type == 'comment':
            instance = Comment.objects.get(id=object_id)
        else:
            return Response({"error": "Invalid content type."}, status=400)

        # Toggle hidden status
        instance.is_flagged = not instance.is_flagged
        instance.save()

        return Response({
            "id": instance.id,
            "hidden": instance.is_flagged,
            "type": content_type
        }, status=200)
    except (DiscussionPost.DoesNotExist, Comment.DoesNotExist):
        return Response({"error": "Content not found."}, status=404)
