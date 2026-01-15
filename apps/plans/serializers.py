from rest_framework import serializers
from .models import Plan, PlanFeature


class PlanFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanFeature
        fields = ("id", "title")


class PlanSerializer(serializers.ModelSerializer):
    features = PlanFeatureSerializer(many=True, read_only=True)
    final_price = serializers.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        model = Plan
        fields = "__all__"
