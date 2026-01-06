from django.contrib import admin
from .models import Plan, PlanFeature


class PlanFeatureInline(admin.TabularInline):
    model = PlanFeature
    extra = 1


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'price',
        'sale_price',
        'final_price',
        'sim_type',
        'is_popular',
        'is_active',
    )
    list_filter = ('sim_type', 'is_active', 'is_popular')
    search_fields = ('name', 'short_description', 'description')

    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'slug', 'short_description', 'description')
        }),
        ('Pricing', {
            'fields': ('price', 'sale_price', 'duration_days', 'sim_type')
        }),
        ('SEO – Meta', {
            'fields': (
                'meta_title',
                'meta_description',
                'meta_keywords',
                'canonical_url'
            )
        }),
        ('SEO – Open Graph', {
            'fields': (
                'og_title',
                'og_description',
                'og_image',
                'og_type'
            )
        }),
        ('SEO – Twitter', {
            'fields': (
                'twitter_title',
                'twitter_description',
                'twitter_image'
            )
        }),
        ('SEO – Schema', {
            'fields': ('schema_markup',)
        }),
        ('Status', {
            'fields': ('is_popular', 'is_active')
        }),
    )

    inlines = [PlanFeatureInline]
