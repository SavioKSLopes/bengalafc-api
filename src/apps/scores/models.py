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
    team = models.CharField(max_length=100, blank=True)  # time do usuário no fantasy

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
        ('falta_sofrida', 'Falta sofrida'),
        ('falta_cometida', 'Falta cometida'),
        ('passe_errado', 'Passe errado'),
        ('penalti_sofrido', 'Penalti sofrido'),
        ('finalizacao_fora', 'Finalização (fora/trave)'),
        ('finalizacao_alvo', 'Finalização no alvo'),
    ]

    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='score_events')
    event_type = models.CharField(max_length=25, choices=EVENT_CHOICES)
    points = models.DecimalField(max_digits=5, decimal_places=2)  # aceita valores como 1.5
    match_id = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.player.user.username} - {self.get_event_type_display()} (+{self.points})"