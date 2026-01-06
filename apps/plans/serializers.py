from rest_framework import serializers
from .models import Plan, PlanFeature


class PlanFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanFeature
        fields = ['title']


class PlanSerializer(serializers.ModelSerializer):
    features = PlanFeatureSerializer(many=True)
    final_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = Plan
        fields = [
            'id',
            'name',
            'slug',
            'short_description',
            'description',
            'price',
            'sale_price',
            'final_price',
            'duration_days',
            'sim_type',
            'is_popular',

            # SEO
            'meta_title',
            'meta_description',
            'meta_keywords',
            'canonical_url',
            'og_title',
            'og_description',
            'og_image',
            'og_type',
            'twitter_title',
            'twitter_description',
            'twitter_image',
            'schema_markup',

            'features'
        ]
