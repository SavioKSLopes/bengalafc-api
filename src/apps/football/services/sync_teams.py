import logging
from typing import Any, Dict, List, Optional
from django.db import transaction
from apps.football.clients.football_api_client import FootballApiClient
from apps.football.models import Team

logger = logging.getLogger(__name__)


class SyncTeamsService:
    """Serviço responsável por sincronizar equipes da API externa para o banco local."""

    def __init__(self, api_client: Optional[FootballApiClient] = None) -> None:
        self.api_client = api_client or FootballApiClient()

    def execute(
        self, league: Optional[int] = None, season: Optional[int] = None
    ) -> List[Team]:
        """Busca seleções da API externa e cria ou atualiza no banco local."""
        logger.info(
            f"Iniciando sincronização de seleções para league={league}, season={season}"
        )
        api_teams = self.api_client.get_teams(league=league, season=season)

        synced_teams = []

        with transaction.atomic():
            for item in api_teams:
                team_data = item.get("team", {})
                external_id = team_data.get("id")

                if not external_id:
                    logger.warning(
                        f"Ignorando equipe sem external_id: {team_data}"
                    )
                    continue

                defaults = {
                    "name": team_data.get("name"),
                    "code": team_data.get("code"),
                    "country": team_data.get("country"),
                    "logo": team_data.get("logo"),
                    "founded": team_data.get("founded"),
                    "is_active": True,
                }

                team, created = Team.objects.update_or_create(
                    external_id=external_id, defaults=defaults
                )
                synced_teams.append(team)

                action = "Criada" if created else "Atualizada"
                logger.info(
                    f"{action} seleção: {team.name} (ID Externo: {team.external_id})"
                )

        logger.info(
            f"Sincronização de seleções concluída. Total: {len(synced_teams)}"
        )
        return synced_teams
