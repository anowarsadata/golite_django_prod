from rest_framework import serializers

class ApplyCouponSerializer(serializers.Serializer):
    coupon_code = serializers.CharField()
