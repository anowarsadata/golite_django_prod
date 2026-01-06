from django.urls import path
from .api_views import PlanListAPI, PlanDetailAPI

urlpatterns = [
    path('plans/', PlanListAPI.as_view(), name='plan-list'),
    path('plans/<slug:slug>/', PlanDetailAPI.as_view(), name='plan-detail'),
]
