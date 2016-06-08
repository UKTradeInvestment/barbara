from django.conf.urls import url, include
from django.views.generic import TemplateView

from rest_framework.routers import DefaultRouter

from interactions.views import InteractionViewSet

router = DefaultRouter()
router.register(r"interactions", InteractionViewSet)

urlpatterns = [

    url(
        r"^$",
        TemplateView.as_view(template_name="interactions/timeline.html")
    ),

    url(r"^api/", include(router.urls, namespace="drf")),
    url(r"^auth/", include('rest_framework.urls', namespace="rest_framework")),

]
