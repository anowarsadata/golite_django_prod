from django.urls import path
from apps.coupons.views import apply_coupon

urlpatterns = [
    path("apply_coupon", apply_coupon),
]
