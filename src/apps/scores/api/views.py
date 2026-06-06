from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import PlayerSerializer, ScoreEventSerializer
from apps.scores.models import Player, ScoreEvent
from apps.scores.services import create_player, process_fixture_scores


class PlayerViewSet(viewsets.GenericViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = PlayerSerializer

    @action(detail=False, methods=['post'])
    def create_profile(self, request):
        if Player.objects.filter(user=request.user).exists():
            return Response({'detail': 'Perfil já existe.'}, status=400)

        position = request.data.get('position')
        football_player_id = request.data.get('football_player_id')  # external_id da API

        player = create_player(request.user, position, football_player_id)
        return Response(PlayerSerializer(player).data, status=201)

    @action(detail=False, methods=['get'])
    def me(self, request):
        try:
            player = request.user.player_profile
            return Response(PlayerSerializer(player).data)
        except Player.DoesNotExist:
            return Response({'detail': 'Perfil não encontrado.'}, status=404)


class ScoreEventViewSet(viewsets.GenericViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ScoreEventSerializer

    def get_queryset(self):
        return ScoreEvent.objects.filter(
            player__user=self.request.user
        ).select_related('fixture')

    @action(detail=False, methods=['get'])
    def my_scores(self, request):
        """Lista todos os eventos de pontuação do usuário"""
        events = self.get_queryset()
        serializer = self.get_serializer(events, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def total(self, request):
        """Retorna o total de pontos do usuário"""
        return Response({'points': request.user.points})