from django.db import models


class Team(models.Model):
    """Representa uma seleção/equipe de futebol."""

    external_id = models.IntegerField(unique=True, db_index=True)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=10, null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    logo = models.URLField(max_length=500, null=True, blank=True)
    founded = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name


class Player(models.Model):
    """Representa um jogador."""

    external_id = models.IntegerField(unique=True, db_index=True)
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="players",
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=255)
    firstname = models.CharField(max_length=255, null=True, blank=True)
    lastname = models.CharField(max_length=255, null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    nationality = models.CharField(max_length=255, null=True, blank=True)
    height = models.CharField(max_length=50, null=True, blank=True)
    weight = models.CharField(max_length=50, null=True, blank=True)
    photo = models.URLField(max_length=500, null=True, blank=True)
    position = models.CharField(max_length=100, null=True, blank=True)
    number = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name


class Competition(models.Model):
    """Representa um torneio/competição."""

    external_id = models.IntegerField(unique=True, db_index=True)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=100, null=True, blank=True)
    logo = models.URLField(max_length=500, null=True, blank=True)
    season = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.name} ({self.season})"


class Stage(models.Model):
    """Representa fases da competição (ex: Grupo A, Oitavas, Final)."""

    competition = models.ForeignKey(
        Competition, on_delete=models.CASCADE, related_name="stages"
    )
    name = models.CharField(max_length=255)
    order = models.IntegerField(default=0)

    class Meta:
        unique_together = ("competition", "name")
        ordering = ["order", "name"]

    def __str__(self) -> str:
        return f"{self.name} - {self.competition.name}"


class Fixture(models.Model):
    """Representa uma partida."""

    external_id = models.IntegerField(unique=True, db_index=True)
    competition = models.ForeignKey(
        Competition, on_delete=models.CASCADE, related_name="fixtures"
    )
    stage = models.ForeignKey(
        Stage,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="fixtures",
    )
    home_team = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name="home_fixtures"
    )
    away_team = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name="away_fixtures"
    )
    kickoff_at = models.DateTimeField()
    status = models.CharField(max_length=50)
    home_score = models.IntegerField(null=True, blank=True)
    away_score = models.IntegerField(null=True, blank=True)
    venue = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.home_team} vs {self.away_team} ({self.status})"


class PlayerStatistic(models.Model):
    """Estatísticas de um jogador em uma partida específica."""

    player = models.ForeignKey(
        Player, on_delete=models.CASCADE, related_name="statistics"
    )
    fixture = models.ForeignKey(
        Fixture, on_delete=models.CASCADE, related_name="player_statistics"
    )

    minutes = models.IntegerField(default=0)
    goals = models.IntegerField(default=0)
    assists = models.IntegerField(default=0)
    shots = models.IntegerField(default=0)
    shots_on_target = models.IntegerField(default=0)
    passes = models.IntegerField(default=0)
    key_passes = models.IntegerField(default=0)
    tackles = models.IntegerField(default=0)
    interceptions = models.IntegerField(default=0)
    yellow_cards = models.IntegerField(default=0)
    red_cards = models.IntegerField(default=0)
    rating = models.DecimalField(
        max_digits=4, decimal_places=2, null=True, blank=True
    )

    class Meta:
        unique_together = ("player", "fixture")

    def __str__(self) -> str:
        return f"{self.player.name} @ {self.fixture}"


class TeamStatistic(models.Model):
    """Estatísticas de uma equipe em uma partida específica."""

    team = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name="statistics"
    )
    fixture = models.ForeignKey(
        Fixture, on_delete=models.CASCADE, related_name="team_statistics"
    )

    possession = models.IntegerField(default=0)  # em porcentagem, ex: 54
    shots = models.IntegerField(default=0)
    shots_on_target = models.IntegerField(default=0)
    corners = models.IntegerField(default=0)
    fouls = models.IntegerField(default=0)
    offsides = models.IntegerField(default=0)
    yellow_cards = models.IntegerField(default=0)
    red_cards = models.IntegerField(default=0)

    class Meta:
        unique_together = ("team", "fixture")

    def __str__(self) -> str:
        return f"{self.team.name} @ {self.fixture}"
