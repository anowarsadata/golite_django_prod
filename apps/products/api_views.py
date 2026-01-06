from rest_framework import generics
from apps.products.models import Product
from .serializers import ProductSerializer

class ProductListAPI(generics.ListCreateAPIView):
    queryset = Product.objects.all().order_by('-id')
    serializer_class = ProductSerializer


class ProductDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'slug'
