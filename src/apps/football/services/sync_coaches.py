import logging
from typing import Any, List, Optional
from django.db import transaction
from apps.football.clients.football_api_client import FootballApiClient
from apps.football.models import Coach, Team

logger = logging.getLogger(__name__)


class SyncCoachesService:
    """Serviço responsável por sincronizar técnicos da API externa para o banco local."""

    def __init__(self, api_client: Optional[FootballApiClient] = None) -> None:
        self.api_client = api_client or FootballApiClient()

    def execute(self, team_id: int) -> List[Coach]:
        """Busca técnicos da API externa e cria ou atualiza no banco local."""
        logger.info(f"Iniciando sincronização de técnicos para o time ID: {team_id}")

        api_coaches = self.api_client.get_coaches(team=team_id)
        synced_coaches = []

        with transaction.atomic():
            for item in api_coaches:
                external_id = item.get("id")

                if not external_id:
                    logger.warning(f"Ignorando técnico sem id: {item}")
                    continue

                team_data = item.get("team", {})
                team_external_id = team_data.get("id")
                team = None
                if team_external_id:
                    team = Team.objects.filter(external_id=team_external_id).first()
                    if not team:
                        logger.warning(
                            f"Time com external_id {team_external_id} não encontrado para técnico {item.get('name')}"
                        )

                defaults = {
                    "name": item.get("name", ""),
                    "nationality": item.get("nationality"),
                    "photo": item.get("photo"),
                    "team": team,
                    "is_active": True,
                }

                coach, created = Coach.objects.update_or_create(
                    external_id=external_id, defaults=defaults
                )
                synced_coaches.append(coach)

                action = "Criado" if created else "Atualizado"
                logger.info(
                    f"{action} técnico: {coach.name} (ID Externo: {coach.external_id})"
                )

        return synced_coaches