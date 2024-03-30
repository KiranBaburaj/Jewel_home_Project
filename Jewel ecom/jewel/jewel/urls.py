from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('user.urls')),
    path('', include('wishlist.urls')),
    path('', include('coupon.urls')),
    path('', include('cadmin.urls')),
    path('', include('user.urls')),
    path('accounts/', include('allauth.urls')),  # Include allauth URLs
     path('', include('payments.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)