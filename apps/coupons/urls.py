from django.urls import path
from apps.coupons.views import apply_coupon, preview_coupon

urlpatterns = [
    path("apply-coupon/", apply_coupon, name="apply_coupon"),
    path("preview-coupon/", preview_coupon, name="preview_coupon"),
]
