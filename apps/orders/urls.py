from django.urls import path
from .views import VCareOrderCreateAPIView

urlpatterns = [
    path("create", VCareOrderCreateAPIView.as_view()),
]
