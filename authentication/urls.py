from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView
from authentication import views

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("user", views.AuthUserViewSet, basename="user")

urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('signup/', views.AuthView.as_view(), name='signup'),
    path('reactivate/', views.ReactivateView.as_view(), name='reactivate'),
    path("", include(router.urls))
]