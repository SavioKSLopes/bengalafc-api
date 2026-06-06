import logging
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List, Optional
from django.db import transaction
from django.conf import settings
from apps.football.clients.football_api_client import FootballApiClient
from apps.football.models import Fixture, Player, PlayerStatistic, Team, TeamStatistic

logger = logging.getLogger(__name__)


class SyncStatisticsService:
    """Serviço responsável por sincronizar estatísticas de partidas (equipes e jogadores)."""

    def __init__(self, api_client: Optional[FootballApiClient] = None) -> None:
        self.api_client = api_client or FootballApiClient()

    def _parse_int(self, val: Any) -> int:
        """Auxiliar para converter valores da API para inteiros de forma segura."""
        if val is None:
            return 0
        if isinstance(val, str):
            val = val.replace("%", "").strip()
        try:
            return int(val)
        except ValueError:
            return 0

    def _parse_decimal(self, val: Any) -> Optional[Decimal]:
        """Auxiliar para converter avaliações da API para Decimal de forma segura."""
        if val is None or val == "N/A" or val == "":
            return None
        try:
            return Decimal(str(val))
        except (ValueError, InvalidOperation):
            return None

    def execute(
        self,
        fixture_id: Optional[int] = None,
        competition_id: Optional[int] = None,
    ) -> Dict[str, int]:
        """Importa estatísticas para uma partida específica ou para todas as partidas finalizadas.

        Retorna um dicionário com o total de registros sincronizados.
        """
        # Se um ID de partida foi informado, sincroniza apenas ela
        if fixture_id:
            fixtures = Fixture.objects.filter(external_id=fixture_id)
        else:
            # Caso contrário, pega todas as partidas da competição atual no banco
            comp_id = competition_id or getattr(
                settings, "FOOTBALL_API_DEFAULT_COMPETITION_ID", 1
            )
            # Sincroniza preferencialmente partidas que já começaram ou terminaram
            fixtures = Fixture.objects.filter(competition__external_id=comp_id)
            logger.info(
                f"Sincronizando estatísticas para as {fixtures.count()} partidas da competição {comp_id} salvas no banco."
            )

        totals = {"team_stats": 0, "player_stats": 0}

        for fixture in fixtures:
            logger.info(
                f"Sincronizando estatísticas da partida ID {fixture.external_id}: {fixture.home_team.name} vs {fixture.away_team.name}"
            )
            
            # 1. Sincronizar Estatísticas das Equipes (Team Statistics)
            try:
                self._sync_team_stats(fixture)
                totals["team_stats"] += 2  # Normalmente 2 equipes por partida
            except Exception as e:
                logger.error(
                    f"Erro ao sincronizar estatísticas de equipe para a partida {fixture.external_id}: {str(e)}"
                )

            # 2. Sincronizar Estatísticas dos Jogadores (Player Statistics)
            try:
                count = self._sync_player_stats(fixture)
                totals["player_stats"] += count
            except Exception as e:
                logger.error(
                    f"Erro ao sincronizar estatísticas de jogadores para a partida {fixture.external_id}: {str(e)}"
                )

        return totals

    def _sync_team_stats(self, fixture: Fixture) -> None:
        """Busca estatísticas das equipes e salva no banco de dados."""
        api_stats = self.api_client.get_fixture_statistics(fixture.external_id)
        if not api_stats:
            logger.info(f"Nenhuma estatística de equipe disponível para a partida {fixture.external_id}")
            return

        with transaction.atomic():
            for team_item in api_stats:
                team_info = team_item.get("team", {})
                team_ext_id = team_info.get("id")

                if not team_ext_id:
                    continue

                # Resolução / Criação Dinâmica do Time
                team, _ = Team.objects.get_or_create(
                    external_id=team_ext_id,
                    defaults={
                        "name": team_info.get("name"),
                        "logo": team_info.get("logo"),
                        "is_active": True,
                    },
                )

                # Mapeia a lista de estatísticas {"type": "...", "value": ...} para um dicionário
                stats_list = team_item.get("statistics", [])
                stats_dict = {
                    s.get("type"): s.get("value") for s in stats_list if s.get("type")
                }

                defaults = {
                    "possession": self._parse_int(stats_dict.get("Ball Possession", 0)),
                    "shots": self._parse_int(stats_dict.get("Total Shots", 0)),
                    "shots_on_target": self._parse_int(stats_dict.get("Shots on Goal", 0)),
                    "corners": self._parse_int(stats_dict.get("Corner Kicks", 0)),
                    "fouls": self._parse_int(stats_dict.get("Fouls", 0)),
                    "offsides": self._parse_int(stats_dict.get("Offsides", 0)),
                    "yellow_cards": self._parse_int(stats_dict.get("Yellow Cards", 0)),
                    "red_cards": self._parse_int(stats_dict.get("Red Cards", 0)),
                }

                TeamStatistic.objects.update_or_create(
                    team=team, fixture=fixture, defaults=defaults
                )

    def _sync_player_stats(self, fixture: Fixture) -> int:
        """Busca estatísticas dos jogadores e salva no banco de dados."""
        api_players_stats = self.api_client.get_player_statistics(fixture.external_id)
        if not api_players_stats:
            logger.info(f"Nenhuma estatística de jogador disponível para a partida {fixture.external_id}")
            return 0

        synced_count = 0

        with transaction.atomic():
            for team_item in api_players_stats:
                team_info = team_item.get("team", {})
                team_ext_id = team_info.get("id")

                if not team_ext_id:
                    continue

                team, _ = Team.objects.get_or_create(
                    external_id=team_ext_id,
                    defaults={
                        "name": team_info.get("name"),
                        "logo": team_info.get("logo"),
                    },
                )

                players_list = team_item.get("players", [])
                for player_item in players_list:
                    player_info = player_item.get("player", {})
                    player_ext_id = player_info.get("id")

                    if not player_ext_id:
                        continue

                    # Resolução / Criação Dinâmica do Jogador
                    player, _ = Player.objects.get_or_create(
                        external_id=player_ext_id,
                        defaults={
                            "name": player_info.get("name"),
                            "photo": player_info.get("photo"),
                            "team": team,
                        },
                    )

                    # Estatísticas detalhadas
                    stats_list = player_item.get("statistics", [])
                    if not stats_list:
                        continue

                    # Geralmente há apenas um objeto estatístico por partida
                    stats = stats_list[0]

                    games = stats.get("games", {})
                    goals = stats.get("goals", {})
                    shots = stats.get("shots", {})
                    passes = stats.get("passes", {})
                    tackles = stats.get("tackles", {})
                    cards = stats.get("cards", {})

                    defaults = {
                        "minutes": self._parse_int(games.get("minutes", 0)),
                        "goals": self._parse_int(goals.get("total", 0)),
                        "assists": self._parse_int(goals.get("assists", 0)),
                        "shots": self._parse_int(shots.get("total", 0)),
                        "shots_on_target": self._parse_int(shots.get("on", 0)),
                        "passes": self._parse_int(passes.get("total", 0)),
                        "key_passes": self._parse_int(passes.get("key", 0)),
                        "tackles": self._parse_int(tackles.get("total", 0)),
                        "interceptions": self._parse_int(tackles.get("interceptions", 0)),
                        "yellow_cards": self._parse_int(cards.get("yellow", 0)),
                        "red_cards": self._parse_int(cards.get("red", 0)),
                        "rating": self._parse_decimal(games.get("rating")),
                    }

                    PlayerStatistic.objects.update_or_create(
                        player=player, fixture=fixture, defaults=defaults
                    )
                    synced_count += 1

        return synced_count
