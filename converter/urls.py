from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (
    ConvertFileAPIView,
    ConvertTextAPIView,
    StatsAPIView,
    WordExceptionViewSet,
    index_view,
)

router = DefaultRouter()
router.register(r"exceptions", WordExceptionViewSet, basename="exceptions")

urlpatterns = [
    path("", index_view, name="index"),
    path("api/v1/convert/", ConvertTextAPIView.as_view(), name="api_convert"),
    path("api/v1/convert-file/", ConvertFileAPIView.as_view(), name="api_convert_file"),
    path("api/v1/stats/", StatsAPIView.as_view(), name="api_stats"),
    path("api/v1/", include(router.urls)),
]
