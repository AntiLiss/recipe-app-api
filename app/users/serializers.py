from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext as _
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["email", "password", "name"]
        extra_kwargs = {
            "password": {"write_only": True, "min_length": 6},
        }

    def create(self, validated_data):
        """Create and return user with encrypted password"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update and return user with encrypted password"""
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        # Updating password separately to hash it
        if password:
            user.set_password(password)
            user.save()
        return user


class AuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        style={"input_type": "password"},
        trim_whitespace=False,
    )

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        user = authenticate(username=email, password=password)
        if not user:
            message = _("Unable to authenticate with provided credentials")
            raise serializers.ValidationError(message, code="authorization")
        attrs["user"] = user
        return attrs
