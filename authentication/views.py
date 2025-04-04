from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from authentication import serializers

from rest_framework import viewsets, mixins, generics
from rest_framework.authentication import BasicAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated


class AuthView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    authentication_classes = [BasicAuthentication]
    serializer_class = serializers.RegisterSerializer


class ReactivateView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    authentication_classes = [BasicAuthentication]
    serializer_class = serializers.ReactivateSerializer
    

class AuthUserViewSet(mixins.DestroyModelMixin, viewsets.GenericViewSet):
    permission_classes      = [IsAuthenticated]
    authentication_classes  = [JWTAuthentication]
    serializer_class = serializers.RegisterSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(pk=self.request.user.pk)
        return queryset
    
    def get_object(self):
        return self.request.user
    
    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()

    @action(["post"], detail=False, url_path="password", serializer_class=serializers.ResetPasswordSerializer)
    def change_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not request.user.check_password(serializer.validated_data["password"]):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(["post"], detail=False, url_path="username", serializer_class=serializers.ResetUsernameSerializer)
    def change_username(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)