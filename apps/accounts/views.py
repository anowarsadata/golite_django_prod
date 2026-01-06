from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail

from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
    UpdateUserSerializer
)


# ---------------- REGISTER ----------------
class RegisterAPI(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Send verification email
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        current_site = get_current_site(request).domain
        verification_link = f"http://{current_site}/api/accounts/verify/{uid}/{token}/"
        
        send_mail(
            "Verify your email",
            f"Click here to verify: {verification_link}",
            "noreply@example.com",
            [user.email],
        )

        return Response({"message": "User registered successfully. Check your email for verification."})


# ---------------- VERIFY EMAIL ----------------
class VerifyEmailAPI(APIView):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"error": "Invalid link"}, status=400)

        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({"message": "Email verified successfully"})
        return Response({"error": "Invalid or expired token"}, status=400)


# ---------------- LOGIN ----------------
class LoginAPI(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data
        token, _ = Token.objects.get_or_create(user=user)

        # return all user fields dynamically
        user_data = {
            field.name: getattr(user, field.name)
            for field in user._meta.fields
        }

        return Response({
            "message": "Login successful",
            "token": token.key,
            "user": user_data
        })



# ---------------- LOGOUT ----------------
class LogoutAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response({"message": "Logged out successfully"})


# ---------------- DASHBOARD ----------------
class DashboardAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        # Return all fields dynamically
        data = {field.name: getattr(user, field.name) for field in user._meta.fields}
        return Response(data)


# ---------------- FORGOT PASSWORD ----------------
class ForgotPasswordAPI(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "Email not found"}, status=404)

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        current_site = get_current_site(request).domain
        reset_link = f"http://{current_site}/api/accounts/reset-password/{uid}/{token}/"

        send_mail(
            "Reset your password",
            f"Click here to reset your password: {reset_link}",
            "noreply@example.com",
            [user.email],
        )

        return Response({"message": "Password reset link sent to email"})


# ---------------- RESET PASSWORD ----------------
class ResetPasswordAPI(APIView):
    def post(self, request, uidb64, token):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"error": "Invalid link"}, status=400)

        if default_token_generator.check_token(user, token):
            user.set_password(serializer.validated_data['password'])
            user.save()
            return Response({"message": "Password reset successful"})
        return Response({"error": "Invalid or expired token"}, status=400)


# ---------------- UPDATE PROFILE ----------------
class UpdateUserAPI(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user
        serializer = UpdateUserSerializer(
            user, data=request.data, partial=True, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Profile updated successfully", "user": serializer.data})
