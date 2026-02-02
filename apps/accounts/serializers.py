from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate

from apps.accounts.models import UserProfile


# ---------------- REGISTER ----------------
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)
    vc_enrollment_id = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True
    )

    class Meta:
        model = User
        fields = ("email", "username", "password", "password2", "vc_enrollment_id")

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Passwords do not match"})
        if User.objects.filter(email=attrs["email"]).exists():
            raise serializers.ValidationError({"email": "Email already registered"})
        return attrs

    def create(self, validated_data):
        vc_id = validated_data.pop("vc_enrollment_id", None)

        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            is_active=False
        )

        UserProfile.objects.create(
            user=user,
            vc_enrollment_id=vc_id
        )

        return user


# ---------------- LOGIN ----------------
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        try:
            user_obj = User.objects.get(email=data["email"])
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials")

        user = authenticate(
            username=user_obj.username,
            password=data["password"]
        )

        if not user:
            raise serializers.ValidationError("Invalid credentials")

        if not user.is_active:
            raise serializers.ValidationError("Account not activated")

        return user


# ---------------- FORGOT PASSWORD ----------------
class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


# ---------------- RESET PASSWORD ----------------
class ResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Passwords do not match"})
        return attrs


# ---------------- UPDATE PROFILE ----------------
class UpdateUserSerializer(serializers.ModelSerializer):
    vc_enrollment_id = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True
    )

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "vc_enrollment_id"]

    def update(self, instance, validated_data):
        vc_id = validated_data.pop("vc_enrollment_id", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if vc_id is not None:
            profile, _ = UserProfile.objects.get_or_create(user=instance)
            profile.vc_enrollment_id = vc_id
            profile.save()

        return instance

    def validate_email(self, value):
        user = self.context["request"].user
        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError("Email already in use")
        return value
