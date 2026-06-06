from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class RankingUserSerializer(serializers.ModelSerializer):
    position = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'points', 'position')

    def get_position(self, obj):
        # posição vem injetada no queryset pela view
        return getattr(obj, 'position', None)