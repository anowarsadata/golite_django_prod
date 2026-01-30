from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static

def home(request):
    return HttpResponse("Golite Django API is running")

urlpatterns = [
    path('', home),  # 👈 ROOT URL
    path('admin/', admin.site.urls),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
    path('api/blog/', include('apps.blog.api_urls', namespace='blog_api')),
    path('api/products/', include('apps.products.api_urls', namespace='products_api')),
    path('api/plans/', include('apps.plans.api_urls')),
    path('api/accounts/', include('apps.accounts.urls')),
    path("api/students/", include("apps.student_discount.urls")),
    path("api/responder/", include("apps.first_responder.urls")),

    
    path('api/v1/', include('apps.coupons.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
