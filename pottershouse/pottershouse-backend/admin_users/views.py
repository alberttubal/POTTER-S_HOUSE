from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.exceptions import ValidationError
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from core.utils import error_response
from email_outbox.models import EmailOutbox
from .serializers import AdminUserSerializer, AdminLoginSerializer, AdminPasswordForgotSerializer, AdminPasswordResetSerializer

User = get_user_model()

def _serializer_error_details(serializer):
    details = []
    for field, messages in serializer.errors.items():
        details.append({'field': field, 'message': messages})
    return details


class AdminLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = AdminLoginSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                code='validation_error',
                message='Validation failed',
                details=_serializer_error_details(serializer),
                status=400,
            )

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        user = User.objects.filter(email__iexact=email).first()
        if not user or not user.check_password(password):
            return error_response(
                code='invalid_credentials',
                message='Invalid email or password',
                details=[],
                status=401,
            )
        if not user.is_active:
            return error_response(
                code='inactive_account',
                message='Account is inactive',
                details=[],
                status=401,
            )

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        expires_in = int(settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds())
        payload = {
            'token': access_token,
            'expires_in': expires_in,
            'admin': AdminUserSerializer(user).data,
        }
        response = Response(payload, status=200)
        if getattr(settings, 'USE_REFRESH_COOKIE', True):
            response.set_cookie(
                settings.REFRESH_COOKIE_NAME,
                str(refresh),
                max_age=settings.REFRESH_COOKIE_MAX_AGE,
                httponly=True,
                secure=settings.REFRESH_COOKIE_SECURE,
                samesite=settings.REFRESH_COOKIE_SAMESITE,
                path=settings.REFRESH_COOKIE_PATH,
            )
        return response


class AdminRefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        if getattr(settings, 'USE_REFRESH_COOKIE', True):
            refresh_token = request.COOKIES.get(settings.REFRESH_COOKIE_NAME)
        else:
            refresh_token = request.data.get('refresh')

        if not refresh_token:
            return error_response(
                code='missing_refresh_token',
                message='Refresh token is required',
                details=[],
                status=401,
            )

        try:
            refresh = RefreshToken(refresh_token)
        except TokenError:
            return error_response(
                code='invalid_refresh_token',
                message='Invalid or expired refresh token',
                details=[],
                status=401,
            )

        user_id = refresh.get('user_id')
        user = User.objects.filter(id=user_id).first()
        if not user or not user.is_active:
            return error_response(
                code='invalid_refresh_token',
                message='Invalid or expired refresh token',
                details=[],
                status=401,
            )

        access_token = str(refresh.access_token)
        expires_in = int(settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds())
        payload = {
            'token': access_token,
            'expires_in': expires_in,
            'admin': AdminUserSerializer(user).data,
        }
        response = Response(payload, status=200)
        if getattr(settings, 'USE_REFRESH_COOKIE', True):
            response.set_cookie(
                settings.REFRESH_COOKIE_NAME,
                str(refresh),
                max_age=settings.REFRESH_COOKIE_MAX_AGE,
                httponly=True,
                secure=settings.REFRESH_COOKIE_SECURE,
                samesite=settings.REFRESH_COOKIE_SAMESITE,
                path=settings.REFRESH_COOKIE_PATH,
            )
        return response


class AdminPasswordForgotView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = AdminPasswordForgotSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                code='validation_error',
                message='Validation failed',
                details=_serializer_error_details(serializer),
                status=400,
            )

        email = serializer.validated_data['email']
        user = User.objects.filter(email__iexact=email, is_active=True).first()
        if user:
            token = PasswordResetTokenGenerator().make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_url = f"{settings.FRONTEND_PASSWORD_RESET_URL}?uid={uid}&token={token}"
            EmailOutbox.objects.create(
                to_email=user.email,
                subject='Password reset',
                template='admin_password_reset',
                payload={'reset_url': reset_url, 'admin_email': user.email},
            )
        return Response({'status': 'ok'}, status=200)


class AdminPasswordResetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = AdminPasswordResetSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                code='validation_error',
                message='Validation failed',
                details=_serializer_error_details(serializer),
                status=400,
            )

        uid = serializer.validated_data['uid']
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']

        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
        except Exception:
            return error_response(
                code='invalid_reset_token',
                message='Invalid or expired reset token',
                details=[],
                status=401,
            )

        if not PasswordResetTokenGenerator().check_token(user, token):
            return error_response(
                code='invalid_reset_token',
                message='Invalid or expired reset token',
                details=[],
                status=401,
            )

        try:
            validate_password(new_password, user)
        except ValidationError as exc:
            return error_response(
                code='validation_error',
                message='Validation failed',
                details=[{'field': 'new_password', 'message': exc.messages}],
                status=400,
            )

        user.set_password(new_password)
        user.save(update_fields=['password', 'updated_at'])
        return Response({'status': 'ok'}, status=200)
