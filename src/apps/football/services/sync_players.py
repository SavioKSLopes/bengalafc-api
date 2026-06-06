import logging
from typing import Any, Dict, List, Optional
from django.db import transaction
from apps.football.clients.football_api_client import FootballApiClient
from apps.football.models import Player, Team

logger = logging.getLogger(__name__)


class SyncPlayersService:
    """Serviço responsável por sincronizar jogadores da API externa para o banco local."""

    def __init__(self, api_client: Optional[FootballApiClient] = None) -> None:
        self.api_client = api_client or FootballApiClient()

    def execute(
        self, team_id: Optional[int] = None, season: Optional[int] = None
    ) -> List[Player]:
        """Busca jogadores da API externa e cria ou atualiza no banco local.

        Se team_id for fornecido, sincroniza apenas os jogadores daquela seleção.
        Caso contrário, sincroniza os jogadores de todas as seleções salvas no banco.
        """
        if team_id:
            teams = Team.objects.filter(external_id=team_id)
            if not teams.exists():
                logger.error(
                    f"Equipe com external_id {team_id} não encontrada no banco local."
                )
                return []
        else:
            teams = Team.objects.filter(is_active=True)
            logger.info(
                f"Nenhum team_id especificado. Sincronizando jogadores para todas as {teams.count()} seleções ativas."
            )

        synced_players = []

        for team in teams:
            logger.info(
                f"Sincronizando jogadores da seleção: {team.name} (ID: {team.external_id})"
            )
            try:
                api_players = self.api_client.get_team_players(
                    team_id=team.external_id, season=season
                )
            except Exception as e:
                logger.error(
                    f"Erro ao buscar jogadores da seleção {team.name} (ID: {team.external_id}): {str(e)}"
                )
                continue

            with transaction.atomic():
                for item in api_players:
                    player_data = item.get("player", {})
                    external_id = player_data.get("id")

                    if not external_id:
                        continue

                    # Extrai informações extras do nó de estatísticas
                    statistics = item.get("statistics", [])
                    position = None
                    number = None

                    if statistics:
                        # Pega informações do primeiro nó de estatísticas correspondente
                        # que contém os detalhes do jogo (posição e número da camisa)
                        games_info = statistics[0].get("games", {})
                        position = games_info.get("position")
                        number = games_info.get("number")

                    defaults = {
                        "team": team,
                        "name": player_data.get("name"),
                        "firstname": player_data.get("firstname"),
                        "lastname": player_data.get("lastname"),
                        "age": player_data.get("age"),
                        "nationality": player_data.get("nationality"),
                        "height": player_data.get("height"),
                        "weight": player_data.get("weight"),
                        "photo": player_data.get("photo"),
                        "position": position,
                        "number": number,
                        "is_active": True,
                    }

                    player, created = Player.objects.update_or_create(
                        external_id=external_id, defaults=defaults
                    )
                    synced_players.append(player)

                    action = "Criado" if created else "Atualizado"
                    logger.debug(
                        f"{action} jogador: {player.name} (ID Externo: {player.external_id})"
                    )

            logger.info(
                f"Finalizada sincronização para a seleção {team.name}. Jogadores sincronizados: {len(api_players)}"
            )

        return synced_players
