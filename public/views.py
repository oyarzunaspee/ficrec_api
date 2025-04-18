from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from authentication.models import Reader
from user_profile.models import Collection, Rec
from rest_framework import viewsets, mixins, authentication
from public import serializers
from utils.mixins import ForbidListMixin
from rest_framework.decorators import action

class PublicProfileViewSet(ForbidListMixin, viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    authentication_classes = [authentication.BasicAuthentication]
    queryset = Reader.objects.filter(user__is_active=True)
    serializer_class = serializers.PublicUserSerializer
    lookup_field = "user__username"

class PublicCollectionViewSet(ForbidListMixin, viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    authentication_classes = [authentication.BasicAuthentication]
    queryset = Collection.objects.filter(deleted=False, private=False, reader__user__is_active=True)
    serializer_class = serializers.PublicCollectionSerializer
    lookup_field = "uid"

class SaveRecViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = serializers.PublicSavedSerializer
    queryset = Rec.objects.filter(deleted=False, collection__deleted=False, collection__private=False)
    lookup_field = "uid"

    @action(methods=["POST"], detail=True)
    def save_rec(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_201_CREATED)