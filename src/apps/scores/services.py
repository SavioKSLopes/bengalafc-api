from django.contrib.auth import get_user_model
from django.db import models as django_models
from .models import Player, ScoreEvent

User = get_user_model()

POSITION_POINTS = {
    'goleiro': {
        'grande_defesa': 4.0,
        'jogo_sem_sofrer_gol': 5.0,
        'gols_sofridos': -2.0,
    },
    'zagueiro': {'jogo_sem_sofrer_gol': 5.0},
    'lateral': {'jogo_sem_sofrer_gol': 5.0},
    'meia': {},
    'atacante': {},
}

GENERAL_POINTS = {
    'cartao_amarelo': -2.0,
    'cartao_vermelho': -5.0,
    'gol': 8.0,
    'assistencia': 5.0,
    'desarme': 1.5,
    'finalizacao_fora': 1.0,
    'finalizacao_alvo': 3.0,
}

# Mapeamento: campo do PlayerStatistic → event_type do ScoreEvent
STAT_TO_EVENT = {
    'goals':           ('gol', 'general'),
    'assists':         ('assistencia', 'general'),
    'tackles':         ('desarme', 'general'),
    'yellow_cards':    ('cartao_amarelo', 'general'),
    'red_cards':       ('cartao_vermelho', 'general'),
    'shots_on_target': ('finalizacao_alvo', 'general'),
}


def calculate_from_statistic(player: Player, stat) -> float:
    """Calcula pontos de um PlayerStatistic e cria os ScoreEvents."""
    position = player.position
    total_points = 0.0

    for stat_field, (event_type, _) in STAT_TO_EVENT.items():
        quantity = getattr(stat, stat_field, 0) or 0
        if quantity == 0:
            continue

        # Pontos gerais
        base = GENERAL_POINTS.get(event_type, 0.0)
        # Bônus de posição (se existir)
        bonus = POSITION_POINTS.get(position, {}).get(event_type, 0.0)
        points_per_event = base + bonus

        # Para eventos negativos (cartão) não multiplica
        if event_type in ('cartao_amarelo', 'cartao_vermelho'):
            quantity = min(quantity, 1)  # 1 cartão por vez

        total = points_per_event * quantity

        # Cria ou ignora (unique_together evita duplicatas)
        ScoreEvent.objects.get_or_create(
            player=player,
            event_type=event_type,
            fixture=stat.fixture,
            defaults={'points': total}
        )
        total_points += total

    # Finalização fora = shots totais - shots_on_target
    shots_fora = (stat.shots or 0) - (stat.shots_on_target or 0)
    if shots_fora > 0:
        pts = GENERAL_POINTS['finalizacao_fora'] * shots_fora
        ScoreEvent.objects.get_or_create(
            player=player,
            event_type='finalizacao_fora',
            fixture=stat.fixture,
            defaults={'points': pts}
        )
        total_points += pts

    # Jogo sem sofrer gol (via TeamStatistic)
    if position in ('goleiro', 'zagueiro', 'lateral'):
        team_stat = stat.fixture.team_statistics.filter(
            team=stat.player.team
        ).first()
        if team_stat and team_stat.goals_conceded == 0:
            pts = POSITION_POINTS[position].get('jogo_sem_sofrer_gol', 0)
            ScoreEvent.objects.get_or_create(
                player=player,
                event_type='jogo_sem_sofrer_gol',
                fixture=stat.fixture,
                defaults={'points': pts}
            )
            total_points += pts

    return total_points


def process_fixture_scores(fixture):
    """
    Processa todos os ScoreEvents de uma partida.
    Chame isso após o sync_statistics do app football.
    """
    from apps.football.models import PlayerStatistic

    stats = PlayerStatistic.objects.filter(fixture=fixture).select_related('player')

    for stat in stats:
        # Busca o fantasy player que tem esse football_player vinculado
        fantasy_players = Player.objects.filter(
            football_player=stat.player
        ).select_related('user')

        for player in fantasy_players:
            points = calculate_from_statistic(player, stat)

            # Atualiza pontos totais do usuário
            player.user.points = django_models.F('points') + points
            player.user.save(update_fields=['points'])


def create_player(user, position, football_player_id=None):
    """Cria perfil de jogador para um usuário"""
    from apps.football.models import Player as FootballPlayer

    football_player = None
    if football_player_id:
        football_player = FootballPlayer.objects.filter(
            external_id=football_player_id
        ).first()

    return Player.objects.create(
        user=user,
        position=position,
        football_player=football_player
    )