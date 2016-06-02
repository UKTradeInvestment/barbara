from django.conf.urls import url, include

from rest_framework.routers import DefaultRouter

from interactions.views import InteractionViewSet

router = DefaultRouter()
router.register(r"interactions", InteractionViewSet)

urlpatterns = [
    url(r"^", include(router.urls, namespace="drf")),
    url(r"^auth/", include('rest_framework.urls', namespace="rest_framework")),
]
