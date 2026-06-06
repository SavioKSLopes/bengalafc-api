from django.contrib.auth import get_user_model
from .models import Player, ScoreEvent
from django.db import models

User = get_user_model()

# Valores por posição
POSITION_POINTS = {
    'goleiro': {
        'grande_defesa': 4.0,
        'jogo_sem_sofrer_gol': 5.0,
        'gols_sofridos': -2.0,
    },
    'zagueiro': {
        'jogo_sem_sofrer_gol': 5.0,
    },
    'lateral': {
        'jogo_sem_sofrer_gol': 5.0,
    },
    'volante': {},
    'meia': {},
    'atacante': {},
}

# Valores gerais (todos)
GENERAL_POINTS = {
    'cartao_amarelo': -2.0,
    'cartao_vermelho': -5.0,
    'gol': 8.0,
    'assistencia': 5.0,
    'desarme': 1.5,
    'falta_sofrida': 1.0,
    'falta_cometida': -0.5,
    'passe_errado': -0.75,
    'penalti_sofrido': 2.0,
    'finalizacao_fora': 1.0,
    'finalizacao_alvo': 3.0,
}


def get_points_for_event(event_type, position):
    """Retorna os pontos considerando posição + gerais"""
    points = GENERAL_POINTS.get(event_type, 0.0)

    # Se a posição tem Bonus específico, adiciona
    position_bonus = POSITION_POINTS.get(position, {}).get(event_type, 0.0)
    points += position_bonus

    return points


def add_score_event(user, event_type, match_id=''):
    """Adiciona evento de pontuação e atualiza total do usuário"""
    try:
        player = user.player_profile
    except Player.DoesNotExist:
        return None  # usuário não tem perfil de jogador ainda

    points = get_points_for_event(event_type, player.position)

    event = ScoreEvent.objects.create(
        player=player,
        event_type=event_type,
        points=points,
        match_id=match_id
    )

    user.points += points
    user.save(update_fields=['points'])

    return event


def create_player(user, position, team=''):
    """Cria perfil de jogador para um usuário"""
    player = Player.objects.create(
        user=user,
        position=position,
        team=team
    )
    return player


def calculate_user_points(user):
    """Recalcula pontos do zero"""
    try:
        player = user.player_profile
        total = player.score_events.aggregate(
            total=models.Sum('points', default=0)
        )['total']

        user.points = total or 0
        user.save(update_fields=['points'])
        return total
    except Player.DoesNotExist:
        return 0