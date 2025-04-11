from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenVerifyView, TokenRefreshView
from authentication import views

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("user", views.AuthUserViewSet, basename="user")

urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path("verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path('signup/', views.AuthView.as_view(), name='signup'),
    path('reactivate/', views.ReactivateView.as_view(), name='reactivate'),
    path("", include(router.urls))
]