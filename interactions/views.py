from rest_framework import filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import ModelViewSet

from .models import Interaction
from .serializers import InteractionSerializer


class StandardPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = "page-size"


class InteractionViewSet(ModelViewSet):

    model = Interaction
    queryset = Interaction.objects.all()
    serializer_class = InteractionSerializer
    pagination_class = StandardPagination
    filter_backends = (filters.DjangoFilterBackend, filters.OrderingFilter)
    ordering_fields = ("pk", "created")
    http_method_names = ("get",)
