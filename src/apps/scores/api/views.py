from rest_framework import viewsets, mixins, permissions, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from ..models import Player, ScoreEvent
from .serializers import PlayerSerializer, ScoreEventSerializer, AddScoreEventSerializer
from ..services import add_score_event, create_player, get_points_for_event

User = get_user_model()


class PlayerViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.RetrieveModelMixin):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = PlayerSerializer

    def get_object(self):
        return self.request.user.player_profile

    @action(detail=False, methods=['post'], url_path='create')
    def create_player(self, request):
        """Cria perfil de jogador para o usuário"""
        serializer = AddScoreEventSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        position = serializer.validated_data.get('event_type')  # hack: usa event_type como position
        team = request.data.get('team', '')

        if Player.objects.filter(user=request.user).exists():
            return Response({'detail': 'Perfil já existe.'}, status=400)

        player = create_player(request.user, position, team)
        return Response(PlayerSerializer(player).data, status=201)


class ScoreEventViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.ListModelMixin):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ScoreEventSerializer

    def get_queryset(self):
        return ScoreEvent.objects.filter(player__user=self.request.user)

    @action(detail=False, methods=['post'])
    def add(self, request):
        """Adiciona evento de pontuação"""
        serializer = AddScoreEventSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        event_type = serializer.validated_data['event_type']
        match_id = serializer.validated_data.get('match_id', '')

        try:
            player = request.user.player_profile
        except Player.DoesNotExist:
            return Response(
                {'detail': 'Crie seu perfil de jogador primeiro.'},
                status=400
            )

        event = add_score_event(request.user, event_type, match_id)

        if not event:
            return Response({'detail': 'Erro ao adicionar evento.'}, status=400)

        return Response(ScoreEventSerializer(event).data, status=201)