from django.core.management.base import BaseCommand
from apps.football.services.sync_players import SyncPlayersService


class Command(BaseCommand):
    help = "Sincroniza jogadores com a API externa"

    def add_arguments(self, parser):
        parser.add_argument(
            "--team-id",
            type=int,
            help="ID da seleção na API externa. Se omitido, sincroniza todas do banco.",
        )
        parser.add_argument(
            "--season", type=int, help="Ano da temporada (ex: 2022)"
        )

    def handle(self, *args, **options):
        team_id = options.get("team-id")
        season = options.get("season")

        self.stdout.write(
            self.style.WARNING("Iniciando sincronização de jogadores...")
        )
        try:
            service = SyncPlayersService()
            players = service.execute(team_id=team_id, season=season)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Sincronização concluída com sucesso! {len(players)} jogadores sincronizados."
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f"Erro ao sincronizar jogadores: {str(e)}"
                )
            )
