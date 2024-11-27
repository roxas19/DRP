from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Category
from .serializers import CategorySerializer
from django.shortcuts import get_object_or_404

@api_view(['GET'])
def get_categories(request):
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_category_by_name(request, name):
    # Fetch the category by name, replacing dashes with spaces for URL compatibility
    category = get_object_or_404(Category, name__iexact=name.replace("-", " "))

    # Serialize the category
    serializer = CategorySerializer(category)
    return Response(serializer.data)