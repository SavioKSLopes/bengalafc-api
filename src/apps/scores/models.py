from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Player(models.Model):
    POSITION_CHOICES = [
        ('goleiro', 'Goleiro'),
        ('zagueiro', 'Zagueiro'),
        ('lateral', 'Lateral'),
        ('meia', 'Meia'),
        ('atacante', 'Atacante'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='player_profile')
    position = models.CharField(max_length=10, choices=POSITION_CHOICES)

    # Liga o jogador do usuário ao jogador real da API de futebol
    football_player = models.ForeignKey(
        'football.Player',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='fantasy_players',
        verbose_name='Jogador Real'
    )

    def __str__(self):
        return f"{self.user.username} - {self.get_position_display()}"


class ScoreEvent(models.Model):
    EVENT_CHOICES = [
        ('grande_defesa', 'Grande defesa'),
        ('jogo_sem_sofrer_gol', 'Jogo sem sofrer gol'),
        ('gols_sofridos', 'Gols sofridos'),
        ('cartao_amarelo', 'Cartão Amarelo'),
        ('cartao_vermelho', 'Cartão Vermelho'),
        ('gol', 'Gol'),
        ('assistencia', 'Assistência'),
        ('desarme', 'Desarme'),
        ('finalizacao_fora', 'Finalização (fora/trave)'),
        ('finalizacao_alvo', 'Finalização no alvo'),
    ]

    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='score_events')
    event_type = models.CharField(max_length=25, choices=EVENT_CHOICES)
    points = models.DecimalField(max_digits=5, decimal_places=2)
    # Agora guarda a referência direta à partida real
    fixture = models.ForeignKey(
        'football.Fixture',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Partida'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Evita processar a mesma partida duas vezes
        unique_together = ('player', 'event_type', 'fixture')

    def __str__(self):
        return f"{self.player.user.username} - {self.get_event_type_display()} ({self.points}pts)"