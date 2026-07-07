import uuid
import random
from django.core.cache import cache
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, throttling
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from apps.core.models import Profile, Role
from .serializers import UserSerializer, ProfileSerializer

User = get_user_model()


class SendOTPThrottle(throttling.UserRateThrottle):
    rate = '10/min'


class SendOTPView(APIView):
    throttle_classes = [SendOTPThrottle]
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        identifier = request.data.get('phone') or request.data.get('email')
        if not identifier:
            return Response({'detail': 'phone or email required'}, status=400)
        otp = f"{random.randint(0,999999):06d}"
        token = str(uuid.uuid4())
        # store both otp and the identifier so verify can locate the correct user
        cache.set(f'otp:{token}', {'otp': otp, 'identifier': identifier}, timeout=5 * 60)
        # In dev log OTP (mask identifier partly)
        masked = identifier
        if '@' in identifier:
            local, domain = identifier.split('@', 1)
            masked = local[:2] + '***@' + domain
        else:
            masked = '***' + identifier[-4:]
        print(f"[DEV OTP] token={token} otp={otp} identifier={masked}")
        return Response({'otp_token': token})


class VerifyOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        otp_token = request.data.get('otp_token')
        otp = request.data.get('otp')
        role_name = request.data.get('role')

        # Development: allow bypassing OTP for quick login by passing `bypass_otp=true` when DEBUG=True
        if settings.DEBUG and request.data.get('bypass_otp'):
            phone = request.data.get('phone') or request.data.get('email')
            if not phone:
                return Response({'detail': 'phone or email required when bypassing OTP'}, status=400)
            # create a predictable username from the phone/email for dev convenience
            username = f'user_{phone}'.replace('@', '_at_').replace('+', '')
            user, created = User.objects.get_or_create(username=username, defaults={'email': f'{username}@example.com'})
        else:
            if not otp_token or not otp:
                return Response({'detail':'otp_token and otp required'}, status=400)
            cached = cache.get(f'otp:{otp_token}')
            identifier = request.data.get('phone') or request.data.get('email')

            # Support cached structure {otp, identifier} or legacy plain otp string
            if isinstance(cached, dict):
                cached_otp = cached.get('otp')
                cached_identifier = cached.get('identifier')
            else:
                cached_otp = cached
                cached_identifier = identifier

            if not cached_otp or cached_otp != otp:
                return Response({'detail': 'invalid otp'}, status=400)

            # Determine identifier to use (email or phone)
            final_identifier = cached_identifier or identifier

            # Find or create user by email or phone
            if final_identifier and '@' in final_identifier:
                # email-based
                username_base = final_identifier.split('@')[0]
                username = f'user_{username_base}'
                user, created = User.objects.get_or_create(
                    email=final_identifier,
                    defaults={'username': username}
                )
                # ensure phone blank if not provided
                if created:
                    user.email = final_identifier
                    user.save()
            else:
                # phone-based (use `phone` field on CustomUser)
                phone_val = final_identifier or ''
                username = f'user_{(phone_val[-8:] if phone_val else otp_token[:8])}'
                user_qs = User.objects.filter(phone=phone_val)
                if user_qs.exists():
                    user = user_qs.first()
                    created = False
                else:
                    user, created = User.objects.get_or_create(
                        username=username,
                        defaults={'email': f'{username}@example.com', 'phone': phone_val}
                    )
        profile, _ = Profile.objects.get_or_create(user=user)
        if role_name:
            role, _ = Role.objects.get_or_create(name=role_name)
            profile.role = role
            profile.save()

        refresh = RefreshToken.for_user(user)
        return Response({'access': str(refresh.access_token), 'refresh': str(refresh), 'user': UserSerializer(user).data})
