from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    # path("auth/", include('djoser.urls.jwt')),
    path("v1/auth/", include('authentication.urls')),
    path("v1/profile/", include('user_profile.urls')),
    path("v1/public/", include('public.urls')),
    
    path('admin/', admin.site.urls)
]
