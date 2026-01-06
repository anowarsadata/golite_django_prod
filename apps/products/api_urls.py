from django.urls import path
from . import api_views

app_name = 'products_api'

urlpatterns = [
    path('products/', api_views.ProductListAPI.as_view(), name='product_list_api'),
    path('products/<slug:slug>/', api_views.ProductDetailAPI.as_view(), name='product_detail_api'),
]
