import uuid
import random
from django.core.cache import cache
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, throttling
from rest_framework_simplejwt.tokens import RefreshToken
from apps.core.models import Profile, Role
from .serializers import UserSerializer, ProfileSerializer

User = get_user_model()


class SendOTPThrottle(throttling.UserRateThrottle):
    rate = '10/min'


class SendOTPView(APIView):
    throttle_classes = [SendOTPThrottle]
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        phone = request.data.get('phone') or request.data.get('email')
        if not phone:
            return Response({'detail':'phone or email required'}, status=400)
        otp = f"{random.randint(0,999999):06d}"
        token = str(uuid.uuid4())
        cache.set(f'otp:{token}', otp, timeout=5*60)
        # In dev log OTP
        print(f"[DEV OTP] token={token} otp={otp}")
        return Response({'otp_token': token})


class VerifyOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        otp_token = request.data.get('otp_token')
        otp = request.data.get('otp')
        role_name = request.data.get('role')
        if not otp_token or not otp:
            return Response({'detail':'otp_token and otp required'}, status=400)
        cached = cache.get(f'otp:{otp_token}')
        if not cached or cached != otp:
            return Response({'detail':'invalid otp'}, status=400)
        # For demo we create a user per token
        username = f'user_{otp_token[:8]}'
        user, created = User.objects.get_or_create(username=username, defaults={'email': f'{username}@example.com'})
        profile, _ = Profile.objects.get_or_create(user=user)
        if role_name:
            role, _ = Role.objects.get_or_create(name=role_name)
            profile.role = role
            profile.save()

        refresh = RefreshToken.for_user(user)
        return Response({'access': str(refresh.access_token), 'refresh': str(refresh), 'user': UserSerializer(user).data})
