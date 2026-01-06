from rest_framework import serializers
from apps.products.models import Product, ProductVariant, ProductImage

class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ['id', 'attributes', 'price', 'stock']


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'is_main']


class ProductSerializer(serializers.ModelSerializer):
    variants = ProductVariantSerializer(many=True)
    images = ProductImageSerializer(many=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'slug',
            'description',
            'price',
            'variants',
            'images',
            'created_at'
        ]

    def create(self, validated_data):
        variants_data = validated_data.pop('variants', [])
        images_data = validated_data.pop('images', [])

        product = Product.objects.create(**validated_data)

        for variant in variants_data:
            ProductVariant.objects.create(product=product, **variant)

        for image in images_data:
            ProductImage.objects.create(product=product, **image)

        return product
