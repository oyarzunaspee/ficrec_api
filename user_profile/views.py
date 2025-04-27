from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from user_profile.models import Collection, Rec
from django.db.models.query import QuerySet
from rest_framework.decorators import action
from public.models import Saved
from authentication.models import Reader
from rest_framework import mixins, viewsets
from user_profile import serializers
from utils.mixins import CustomDestroyMixin
from utils.serializers import RecSerializer


class ProfileViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.UpdateModelMixin):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = serializers.ReaderSerializer
    queryset = Reader.objects.filter(user__is_active=True)

    def get_queryset(self):
        queryset = self.queryset
        if isinstance(queryset, QuerySet):
            queryset = queryset.filter(user=self.request.user)
        return queryset

    def get_object(self):
        reader = self.get_queryset().get(user=self.request.user.pk)
        return reader
    
    def list(self, request, format=None):
        serializer = self.get_serializer(self.request.user.user_reader)
        return Response(serializer.data)

    
class CollectionViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, CustomDestroyMixin):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = serializers.CollectionSerializer
    queryset = Collection.objects.filter(deleted=False)
    lookup_field = "uid"

    def get_queryset(self):
        queryset = self.queryset
        if isinstance(queryset, QuerySet):
            queryset = queryset.filter(reader__user=self.request.user)
        return queryset

    @action(["patch"], detail=True, url_path="toggle", serializer_class=serializers.ToggleSerializer)
    def toggle_field(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(["post"], detail=True, url_path="add/rec", serializer_class=serializers.PrepareRecSerializer)
    def add_rec(self, request, uid=None, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        rec_serializer = serializer.save()

        headers = self.get_success_headers(rec_serializer.data)
        return Response(rec_serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    

class RecViewSet(viewsets.GenericViewSet, CustomDestroyMixin, mixins.ListModelMixin, mixins.UpdateModelMixin):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    queryset = Rec.objects.filter(deleted=False, collection__deleted=False, collection__reader__user__is_active=True)
    serializer_class = RecSerializer
    lookup_field = "uid"

    def get_queryset(self):
        queryset = self.queryset
        if isinstance(queryset, QuerySet):
            col_uid = self.kwargs["collection_uid"]
            queryset = queryset.filter(collection__reader__user=self.request.user, collection__uid=col_uid)
        return queryset
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = serializers.EditRecSerializer
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    
 
class SavedViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, CustomDestroyMixin):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    queryset = Saved.objects.filter(deleted=False, rec__deleted=False, rec__collection__deleted=False, rec__collection__private=False, rec__collection__reader__user__is_active=True)
    serializer_class = serializers.SavedSerializer
    lookup_field = "uid"

    def get_queryset(self):
        queryset = self.queryset
        if isinstance(queryset, QuerySet):
            queryset = queryset.filter(saved_by__user=self.request.user)
        return queryset

    @action(["patch"], detail=True, url_path="toggle")
    def mark_as_read(self, request, uid=None):
        instance = self.get_object()
        instance.read = not instance.read
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT, headers=headers)