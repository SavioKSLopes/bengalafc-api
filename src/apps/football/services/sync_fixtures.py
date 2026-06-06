import logging
from typing import Any, Dict, List, Optional
from django.db import transaction
from django.conf import settings
from django.utils.dateparse import parse_datetime
from apps.football.clients.football_api_client import FootballApiClient
from apps.football.models import Competition, Fixture, Stage, Team

logger = logging.getLogger(__name__)


class SyncFixturesService:
    """Serviço responsável por sincronizar partidas (fixtures) da API externa para o banco local."""

    def __init__(self, api_client: Optional[FootballApiClient] = None) -> None:
        self.api_client = api_client or FootballApiClient()

    def execute(
        self,
        competition_id: Optional[int] = None,
        season: Optional[int] = None,
    ) -> List[Fixture]:
        """Busca partidas da API externa e cria ou atualiza no banco local."""
        comp_id = competition_id or getattr(
            settings, "FOOTBALL_API_DEFAULT_COMPETITION_ID", 1
        )
        season_year = season or getattr(
            settings, "FOOTBALL_API_DEFAULT_SEASON", 2022
        )

        logger.info(
            f"Iniciando sincronização de partidas para competição ID: {comp_id}, season: {season_year}"
        )

        try:
            competition = Competition.objects.get(external_id=comp_id)
        except Competition.DoesNotExist:
            logger.error(
                f"Competição com external_id {comp_id} não encontrada. Sincronize as competições primeiro."
            )
            return []

        # Obtém partidas da API
        api_fixtures = self.api_client.get_fixtures(
            competition_id=comp_id, season=season_year
        )

        synced_fixtures = []

        with transaction.atomic():
            for item in api_fixtures:
                fixture_info = item.get("fixture", {})
                external_id = fixture_info.get("id")

                if not external_id:
                    continue

                # Parse do kickoff
                date_str = fixture_info.get("date")
                kickoff_at = parse_datetime(date_str) if date_str else None

                if not kickoff_at:
                    logger.warning(
                        f"Partida {external_id} sem data de kickoff válida: {date_str}"
                    )
                    continue

                # Resolução / Criação Dinâmica do Stage (Fase)
                league_info = item.get("league", {})
                round_name = league_info.get("round", "Desconhecido")
                stage, _ = Stage.objects.get_or_create(
                    competition=competition,
                    name=round_name,
                    defaults={"order": 99},
                )

                # Resolução / Criação Dinâmica das Equipes
                teams_info = item.get("teams", {})
                home_info = teams_info.get("home", {})
                away_info = teams_info.get("away", {})

                home_ext_id = home_info.get("id")
                away_ext_id = away_info.get("id")

                if not home_ext_id or not away_ext_id:
                    logger.warning(
                        f"Ignorando partida {external_id} devido a informações incompletas das equipes."
                    )
                    continue

                home_team, _ = Team.objects.get_or_create(
                    external_id=home_ext_id,
                    defaults={
                        "name": home_info.get("name"),
                        "logo": home_info.get("logo"),
                        "is_active": True,
                    },
                )

                away_team, _ = Team.objects.get_or_create(
                    external_id=away_ext_id,
                    defaults={
                        "name": away_info.get("name"),
                        "logo": away_info.get("logo"),
                        "is_active": True,
                    },
                )

                # Gols
                goals_info = item.get("goals", {})
                home_score = goals_info.get("home")
                away_score = goals_info.get("away")

                # Venue
                venue_info = fixture_info.get("venue", {})
                venue_name = venue_info.get("name") or ""
                if venue_info.get("city"):
                    venue_name += f" ({venue_info.get('city')})"

                defaults = {
                    "competition": competition,
                    "stage": stage,
                    "home_team": home_team,
                    "away_team": away_team,
                    "kickoff_at": kickoff_at,
                    "status": fixture_info.get("status", {}).get("short", "NS"),
                    "home_score": home_score,
                    "away_score": away_score,
                    "venue": venue_name[:255],
                }

                fixture, created = Fixture.objects.update_or_create(
                    external_id=external_id, defaults=defaults
                )
                synced_fixtures.append(fixture)

                action = "Criada" if created else "Atualizada"
                logger.info(
                    f"{action} partida: {fixture.home_team.name} {fixture.home_score or 0} x {fixture.away_score or 0} {fixture.away_team.name} (Status: {fixture.status})"
                )

        logger.info(
            f"Sincronização de partidas concluída. Total: {len(synced_fixtures)}"
        )
        return synced_fixtures
