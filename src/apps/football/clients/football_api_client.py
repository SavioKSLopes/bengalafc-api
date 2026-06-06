import logging
import time
from typing import Any, Dict, List, Optional
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class FootballApiClientError(Exception):
    """Exceção base para erros do cliente da API de Futebol."""

    pass


class FootballApiClient:
    """Cliente HTTP para comunicação com a API-Football."""

    def __init__(self) -> None:
        self.base_url = settings.FOOTBALL_API_URL.rstrip("/")
        self.api_key = settings.FOOTBALL_API_KEY
        self.api_header = settings.FOOTBALL_API_HEADER
        self.session = requests.Session()

        # Configura os cabeçalhos padrão para autenticação
        self.session.headers.update(
            {
                "Accept": "application/json",
                self.api_header: self.api_key,
            }
        )

    def _request(
        self,
        endpoint: str,
        method: str = "GET",
        params: Optional[Dict[str, Any]] = None,
        retries: int = 3,
        backoff_factor: float = 2.0,
    ) -> Dict[str, Any]:
        """Executa a requisição HTTP com retry automático, rate limit handling e tratamento de erros."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        delay = 1.0

        for attempt in range(1, retries + 1):
            try:
                logger.info(
                    f"Enviando requisição para {url} - Tentativa {attempt}/{retries}. Params: {params}"
                )
                response = self.session.request(
                    method=method, url=url, params=params, timeout=15
                )

                # Tratamento de rate limit (HTTP 429)
                if response.status_code == 429:
                    logger.warning(
                        f"Rate limit atingido (HTTP 429). Aguardando {delay} segundos..."
                    )
                    time.sleep(delay)
                    delay *= backoff_factor
                    continue

                # Erros HTTP genéricos
                response.raise_for_status()

                data = response.json()

                # A API-Football às vezes retorna HTTP 200 contendo erros no corpo JSON
                if "errors" in data and data["errors"]:
                    errors = data["errors"]
                    # Pode ser uma lista vazia, ou um dicionário com erros
                    if isinstance(errors, dict) and errors:
                        # Verifica se é rate limit na resposta da API-Football
                        # Exemplo: {'rateLimit': 'Requests limit reached'}
                        error_msg = "; ".join(
                            [f"{k}: {v}" for k, v in errors.items()]
                        )
                        logger.warning(
                            f"Erro retornado na resposta da API: {error_msg}. Tentativa {attempt}/{retries}"
                        )

                        if "limit" in error_msg.lower() or "rate" in error_msg.lower():
                            time.sleep(delay)
                            delay *= backoff_factor
                            continue
                        raise FootballApiClientError(
                            f"Erro na resposta da API: {error_msg}"
                        )

                return data

            except requests.RequestException as e:
                logger.error(
                    f"Erro de conexão na tentativa {attempt}/{retries} para {url}: {str(e)}"
                )
                if attempt == retries:
                    raise FootballApiClientError(
                        f"Erro ao conectar com a API de futebol: {str(e)}"
                    ) from e
                time.sleep(delay)
                delay *= backoff_factor

        raise FootballApiClientError(
            f"Falha ao executar requisição para {url} após {retries} tentativas."
        )

    def get_teams(
        self, league: Optional[int] = None, season: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Busca seleções de uma liga e temporada específicas."""
        params = {}
        if league:
            params["league"] = league
        if season:
            params["season"] = season

        # Caso nenhum parâmetro seja fornecido, tenta buscar usando padrões de settings
        if not params:
            params["league"] = getattr(
                settings, "FOOTBALL_API_DEFAULT_COMPETITION_ID", 1
            )
            params["season"] = getattr(
                settings, "FOOTBALL_API_DEFAULT_SEASON", 2022
            )

        data = self._request("teams", params=params)
        return data.get("response", [])

    def get_team_players(
        self, team_id: int, season: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Busca jogadores de uma seleção específica, tratando a paginação da API-Football."""
        players = []
        page = 1
        total_pages = 1

        if not season:
            season = getattr(settings, "FOOTBALL_API_DEFAULT_SEASON", 2022)

        while page <= total_pages:
            params = {"team": team_id, "season": season, "page": page}
            data = self._request("players", params=params)

            # Extrai os dados da página
            response_list = data.get("response", [])
            players.extend(response_list)

            # Verifica paginação
            paging = data.get("paging", {})
            total_pages = paging.get("total", 1)
            page += 1

        return players

    def get_competitions(
        self,
        id: Optional[int] = None,
        name: Optional[str] = None,
        season: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Busca competições disponíveis."""
        params = {}
        if id:
            params["id"] = id
        if name:
            params["name"] = name
        if season:
            params["season"] = season

        data = self._request("leagues", params=params)
        return data.get("response", [])

    def get_fixtures(
        self, competition_id: int, season: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Busca partidas de uma competição/temporada."""
        if not season:
            season = getattr(settings, "FOOTBALL_API_DEFAULT_SEASON", 2022)

        params = {"league": competition_id, "season": season}
        data = self._request("fixtures", params=params)
        return data.get("response", [])

    def get_fixture_statistics(self, fixture_id: int) -> List[Dict[str, Any]]:
        """Busca estatísticas das equipes para uma partida."""
        params = {"fixture": fixture_id}
        data = self._request("fixtures/statistics", params=params)
        return data.get("response", [])

    def get_player_statistics(self, fixture_id: int) -> List[Dict[str, Any]]:
        """Busca estatísticas dos jogadores para uma partida."""
        params = {"fixture": fixture_id}
        data = self._request("fixtures/players", params=params)
        return data.get("response", [])
