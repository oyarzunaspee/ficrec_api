from django.urls import path, include
from rest_framework_simplejwt.views import TokenVerifyView, TokenRefreshView
from authentication import views

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("user", views.AuthUserViewSet, basename="user")

urlpatterns = [
    # path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    path('signup/', views.AuthView.as_view(), name='signup'),
    path("login/", views.CustomTokenObtainView.as_view(), name="token_obtain_pair"),
    path("verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("refresh/", views.CustomTokenRefreshView.as_view(), name="token_refresh"),
    path('reactivate/', views.ReactivateView.as_view(), name='reactivate'),
    path("", include(router.urls))
]