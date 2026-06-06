from rest_framework import viewsets, mixins, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from apps.ranking.models import Friendship
from .serializers import RankingUserSerializer

User = get_user_model()


class RankingViewSet(viewsets.GenericViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = RankingUserSerializer

    @action(detail=False, methods=['get'], url_path='global')
    def global_ranking(self, request):
        # Todos os usuários ordenados por pontos
        queryset = User.objects.order_by('-points')

        # Injeta a posição em cada objeto
        users_with_position = []
        for index, user in enumerate(queryset, start=1):
            user.position = index
            users_with_position.append(user)

        serializer = self.get_serializer(users_with_position, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='friends')
    def friends_ranking(self, request):
        # Pega os IDs dos amigos do usuário logado
        friend_ids = Friendship.objects.filter(
            from_user=request.user
        ).values_list('to_user_id', flat=True)

        # Inclui o próprio usuário no ranking de amigos
        queryset = User.objects.filter(
            id__in=list(friend_ids) + [request.user.id]
        ).order_by('-points')

        users_with_position = []
        for index, user in enumerate(queryset, start=1):
            user.position = index
            users_with_position.append(user)

        serializer = self.get_serializer(users_with_position, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='friends/add')
    def add_friend(self, request):
        # Adiciona amigo pelo username
        username = request.data.get('username')
        if not username:
            return Response({'detail': 'username é obrigatório.'}, status=400)

        try:
            to_user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'detail': 'Usuário não encontrado.'}, status=404)

        if to_user == request.user:
            return Response({'detail': 'Você não pode adicionar a si mesmo.'}, status=400)

        friendship, created = Friendship.objects.get_or_create(
            from_user=request.user,
            to_user=to_user
        )

        if not created:
            return Response({'detail': 'Amizade já existe.'}, status=400)

        return Response({'detail': f'{username} adicionado com sucesso.'}, status=201)