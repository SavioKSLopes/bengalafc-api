from rest_framework import serializers
from .models import Player, ScoreEvent


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ('id', 'position', 'team', 'user')
        read_only_fields = ('user',)


class ScoreEventSerializer(serializers.ModelSerializer):
    event_display = serializers.CharField(source='get_event_type_display', read_only=True)

    class Meta:
        model = ScoreEvent
        fields = ('id', 'event_type', 'event_display', 'points', 'match_id', 'created_at')
        read_only_fields = ('points',)


class AddScoreEventSerializer(serializers.Serializer):
    event_type = serializers.CharField()
    match_id = serializers.CharField(required=False, allow_blank=True)