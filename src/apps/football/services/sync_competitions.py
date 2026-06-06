import logging
from typing import Any, Dict, List, Optional
from django.db import transaction
from django.conf import settings
from apps.football.clients.football_api_client import FootballApiClient
from apps.football.models import Competition

logger = logging.getLogger(__name__)


class SyncCompetitionsService:
    """Serviço responsável por sincronizar competições da API externa para o banco local."""

    def __init__(self, api_client: Optional[FootballApiClient] = None) -> None:
        self.api_client = api_client or FootballApiClient()

    def execute(
        self,
        competition_id: Optional[int] = None,
        season: Optional[int] = None,
    ) -> List[Competition]:
        """Busca competições da API externa e cria ou atualiza no banco local."""
        comp_id = competition_id or getattr(
            settings, "FOOTBALL_API_DEFAULT_COMPETITION_ID", 1
        )
        season_year = season or getattr(
            settings, "FOOTBALL_API_DEFAULT_SEASON", 2022
        )

        logger.info(
            f"Iniciando sincronização de competição ID: {comp_id}, season: {season_year}"
        )
        api_competitions = self.api_client.get_competitions(
            id=comp_id, season=season_year
        )

        synced_competitions = []

        with transaction.atomic():
            for item in api_competitions:
                league_data = item.get("league", {})
                external_id = league_data.get("id")

                if not external_id:
                    logger.warning(
                        f"Ignorando competição sem id: {league_data}"
                    )
                    continue

                defaults = {
                    "name": league_data.get("name"),
                    "type": league_data.get("type"),
                    "logo": league_data.get("logo"),
                    "season": season_year,
                }

                competition, created = Competition.objects.update_or_create(
                    external_id=external_id, defaults=defaults
                )
                synced_competitions.append(competition)

                action = "Criada" if created else "Atualizada"
                logger.info(
                    f"{action} competição: {competition.name} (ID Externo: {competition.external_id})"
                )

        # Caso a API retorne vazia (ex: chave trial não suporta busca genérica de ligas com filtros),
        # podemos criar/atualizar manualmente com os dados padrão informados como salvaguarda
        if not synced_competitions and comp_id:
            logger.warning(
                f"Nenhuma competição encontrada na API para ID {comp_id}. Criando registro fallback."
            )
            with transaction.atomic():
                defaults = {
                    "name": "World Cup" if comp_id == 1 else f"Competition {comp_id}",
                    "type": "Cup",
                    "logo": f"https://media.api-sports.io/football/leagues/{comp_id}.png",
                    "season": season_year,
                }
                competition, created = Competition.objects.update_or_create(
                    external_id=comp_id, defaults=defaults
                )
                synced_competitions.append(competition)
                action = "Criada (Fallback)" if created else "Atualizada (Fallback)"
                logger.info(f"{action} competição: {competition.name}")

        return synced_competitions
