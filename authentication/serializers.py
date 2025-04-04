from authentication.models import Reader
from django.contrib.auth.models import User
from rest_framework import serializers

class ReactivateSerializer(serializers.Serializer):
    username = serializers.CharField(min_length=4, trim_whitespace=True)
    password = serializers.CharField(required=True, write_only=True, min_length=6)

    def save(self):
        try:
            user = User._default_manager.get_by_natural_key(self.validated_data["username"])
        except User.DoesNotExist:
            return serializers.ValidationError("User does not exist")
        check_password = user.check_password(self.validated_data["password"])
        if check_password:
            user.is_active = True
            user.save()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=True, write_only=True, min_length=6)
    password_check = serializers.CharField(required=True, write_only=True, min_length=6)
    class Meta:
        model = User
        fields = ["username", "password", "password_check"]

    def validate(self, data):
        if data["password"] != data["password_check"]:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def save(self):
        new_user = User.objects.create(
            username = self.validated_data["username"].lower(),
            password = self.validated_data["password"]
        )
        new_user.set_password(self.validated_data["password"])
        new_user.save()
        Reader.objects.create(user = new_user)

class ResetPasswordSerializer(RegisterSerializer):
    current_password = serializers.CharField(required=True, write_only=True, min_length=6)

    def save(self):
        user = self.context["view"].get_object()
        user.set_password(self.validated_data["password"])
        user.save()

class ResetUsernameSerializer(serializers.Serializer):
    new_username = serializers.CharField(min_length=4, trim_whitespace=True)

    def validate(self, data):
        if User.objects.filter(username=data["new_username"].lower()):
            raise serializers.ValidationError("Username already taken")
        return data
    
    def save(self):
        user = self.context["view"].get_object()
        user.username = self.validated_data["new_username"].lower()
        user.save()