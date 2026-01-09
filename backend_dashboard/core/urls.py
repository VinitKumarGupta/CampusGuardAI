from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from dashboard import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Dashboard Tabs
    path('', views.tab_all_entries, name='home'), # Default to Tab 1
    path('all/', views.tab_all_entries, name='tab_all'),
    path('violations/', views.tab_violations, name='tab_violations'),
    path('rewards/', views.tab_rewards, name='tab_rewards'),
    
    # API endpoint for the button
    path('send_alert/<int:track_id>/', views.send_alert, name='send_alert'),
]

# This magic line allows Django to serve your violation images locally
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)