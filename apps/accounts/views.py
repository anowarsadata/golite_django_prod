from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token

from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import redirect

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

        user = serializer.save(is_active=False)

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        frontend_origin = request.headers.get(
            "X-Frontend-Origin",
            f"{request.scheme}://{request.get_host()}"
        )

        verification_link = (
            f"{request.build_absolute_uri('/')[:-1]}"
            f"/api/accounts/verify/{uid}/{token}/"
            f"?frontend={frontend_origin}"
        )

        send_mail(
            subject="Verify your email",
            message=f"Click link:\n{verification_link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        return Response({
            "message": "Registered successfully. Check email for verification."
        })


# ---------------- VERIFY EMAIL ----------------
class VerifyEmailAPI(APIView):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except:
            return Response({"error": "Invalid link"}, status=400)

        if not default_token_generator.check_token(user, token):
            return Response({"error": "Invalid or expired token"}, status=400)

        user.is_active = True
        user.save()

        frontend = request.GET.get(
            "frontend",
            f"{request.scheme}://{request.get_host()}"
        )

        return redirect(f"{frontend}/login?verified=1")


# ---------------- LOGIN ----------------
class LoginAPI(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data
        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            "message": "Login successful",
            "token": token.key,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "vc_enrollment_id": getattr(user.profile, "vc_enrollment_id", None)
            }
        })


# ---------------- LOGOUT ----------------
class LogoutAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response({"message": "Logged out"})


# ---------------- DASHBOARD ----------------
class DashboardAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "vc_enrollment_id": getattr(user.profile, "vc_enrollment_id", None)
        })


# ---------------- FORGOT PASSWORD ----------------
class ForgotPasswordAPI(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"message": "If email exists, reset link sent"})

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        frontend = request.headers.get(
            "X-Frontend-Origin",
            f"{request.scheme}://{request.get_host()}"
        )

        reset_link = f"{frontend}/reset-password/{uid}/{token}"

        send_mail(
            subject="Reset Password",
            message=f"Click link:\n{reset_link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        return Response({"message": "Reset link sent"})


# ---------------- RESET PASSWORD ----------------
class ResetPasswordAPI(APIView):
    def post(self, request, uidb64, token):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except:
            return Response({"error": "Invalid link"}, status=400)

        if default_token_generator.check_token(user, token):
            user.set_password(serializer.validated_data["password"])
            user.save()
            return Response({"message": "Password reset successful"})

        return Response({"error": "Invalid or expired token"}, status=400)


# ---------------- UPDATE PROFILE ----------------
class UpdateUserAPI(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = UpdateUserSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "message": "Profile updated",
            "user": {
                **serializer.data,
                "vc_enrollment_id": getattr(request.user.profile, "vc_enrollment_id", None)
            }
        })
