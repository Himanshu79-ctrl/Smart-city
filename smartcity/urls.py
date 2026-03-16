from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
import debug_toolbar

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('accounts/social/', include('allauth.urls')),  # Google login
    path('reports/', include('reports.urls')),
    path('rewards/', include('rewards.urls')),
    path('notifications/', include('notifications.urls')),
    path('', include('reports.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    #urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]