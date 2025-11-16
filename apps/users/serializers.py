from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.core.models import Profile, Role

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','username','email','first_name','last_name')


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), required=False)

    class Meta:
        model = Profile
        fields = ('user','role','phone','city','avatar','bio','is_verified')
