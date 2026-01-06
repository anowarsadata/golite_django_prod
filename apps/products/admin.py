from django.contrib import admin
from .models import Product, ProductVariant, ProductImage
from django import forms
import json

# Inline for variants
class ProductVariantInlineForm(forms.ModelForm):
    class Meta:
        model = ProductVariant
        fields = ['attributes', 'price', 'stock']
        widgets = {
            'attributes': forms.Textarea(attrs={'rows': 3, 'cols': 40}),
        }
        help_texts = {
            'attributes': 'Enter attributes as JSON. Example: {"storage": "128GB", "colours": ["Silver", "Violet", "White"], "condition": ["B1-Stock", "B2-Stock", "RC2-Stock"]}'
        }

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    form = ProductVariantInlineForm
    extra = 1
    fields = ['attributes', 'price', 'stock']
    show_change_link = True  # Allows editing variant in its own page if needed

# Inline for images
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'is_main']
    show_change_link = True

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'slug', 'created_at', 'updated_at']
    search_fields = ['name', 'slug']
    list_filter = ['created_at', 'updated_at']
    inlines = [ProductVariantInline, ProductImageInline]
    prepopulated_fields = {'slug': ('name',)}  # Optional: lets admin see slug while typing

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ['product', 'attributes', 'price', 'stock']
    search_fields = ['product__name', 'attributes']
    list_filter = ['product']
    form = ProductVariantInlineForm  # Use same help_text in separate admin view

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'image', 'is_main']
    search_fields = ['product__name']
    list_filter = ['is_main']
