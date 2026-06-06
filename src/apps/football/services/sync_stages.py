import logging
from typing import Any, Dict, List, Optional
from django.db import transaction
from django.conf import settings
from apps.football.clients.football_api_client import FootballApiClient
from apps.football.models import Competition, Stage

logger = logging.getLogger(__name__)


class SyncStagesService:
    """Serviço responsável por sincronizar e criar fases de uma competição a partir das partidas."""

    def __init__(self, api_client: Optional[FootballApiClient] = None) -> None:
        self.api_client = api_client or FootballApiClient()

    def _determine_order(self, stage_name: str) -> int:
        """Determina a ordem lógica das fases para exibição baseando-se no nome."""
        name_lower = stage_name.lower()

        # Mapeamento heurístico de fases
        if "grupo a" in name_lower or "group a" in name_lower:
            return 1
        elif "grupo b" in name_lower or "group b" in name_lower:
            return 2
        elif "grupo c" in name_lower or "group c" in name_lower:
            return 3
        elif "grupo d" in name_lower or "group d" in name_lower:
            return 4
        elif "grupo e" in name_lower or "group e" in name_lower:
            return 5
        elif "grupo f" in name_lower or "group f" in name_lower:
            return 6
        elif "grupo g" in name_lower or "group g" in name_lower:
            return 7
        elif "grupo h" in name_lower or "group h" in name_lower:
            return 8
        elif "group" in name_lower or "grupo" in name_lower or "fase de grupos" in name_lower:
            return 10
        elif "oitavas" in name_lower or "round of 16" in name_lower or "1/8" in name_lower:
            return 20
        elif "quartas" in name_lower or "quarter-final" in name_lower or "1/4" in name_lower:
            return 30
        elif "semifinal" in name_lower or "semi-final" in name_lower or "1/2" in name_lower:
            return 40
        elif "terceiro" in name_lower or "3rd" in name_lower or "disputa de 3" in name_lower:
            return 45
        elif "final" in name_lower:
            return 50

        return 99

    def execute(
        self,
        competition_id: Optional[int] = None,
        season: Optional[int] = None,
    ) -> List[Stage]:
        """Importa as partidas da API, extrai as fases únicas e as salva no banco de dados."""
        comp_id = competition_id or getattr(
            settings, "FOOTBALL_API_DEFAULT_COMPETITION_ID", 1
        )
        season_year = season or getattr(
            settings, "FOOTBALL_API_DEFAULT_SEASON", 2022
        )

        logger.info(
            f"Iniciando sincronização de fases para competição ID: {comp_id}, season: {season_year}"
        )

        try:
            competition = Competition.objects.get(external_id=comp_id)
        except Competition.DoesNotExist:
            logger.error(
                f"Competição com external_id {comp_id} não encontrada. Por favor, sincronize as competições primeiro."
            )
            return []

        # Obtém partidas para extrair os rounds
        api_fixtures = self.api_client.get_fixtures(
            competition_id=comp_id, season=season_year
        )

        unique_rounds = set()
        for item in api_fixtures:
            league_info = item.get("league", {})
            round_name = league_info.get("round")
            if round_name:
                unique_rounds.add(round_name)

        if not unique_rounds:
            logger.warning(
                f"Nenhuma fase encontrada nos fixtures da API para a competição {competition.name}."
            )
            # Fases fallback se não houver fixtures da API
            unique_rounds = {
                "Grupo A",
                "Grupo B",
                "Grupo C",
                "Grupo D",
                "Oitavas de Final",
                "Quartas de Final",
                "Semifinal",
                "Decisão do 3º Lugar",
                "Final",
            }
            logger.info("Usando fases de fallback padrão.")

        synced_stages = []
        with transaction.atomic():
            for round_name in sorted(unique_rounds):
                order = self._determine_order(round_name)
                stage, created = Stage.objects.update_or_create(
                    competition=competition,
                    name=round_name,
                    defaults={"order": order},
                )
                synced_stages.append(stage)
                action = "Criada" if created else "Atualizada"
                logger.info(
                    f"{action} fase: '{stage.name}' (Ordem: {stage.order}) da competição '{competition.name}'"
                )

        return synced_stages
