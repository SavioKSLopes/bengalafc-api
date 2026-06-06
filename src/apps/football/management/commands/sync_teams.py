from django.core.management.base import BaseCommand
from apps.football.services.sync_teams import SyncTeamsService


class Command(BaseCommand):
    help = "Sincroniza seleções/equipes com a API externa"

    def add_arguments(self, parser):
        parser.add_argument(
            "--league", type=int, help="ID da liga na API externa"
        )
        parser.add_argument(
            "--season", type=int, help="Ano da temporada (ex: 2022)"
        )

    def handle(self, *args, **options):
        league = options.get("league")
        season = options.get("season")

        self.stdout.write(
            self.style.WARNING("Iniciando sincronização de seleções...")
        )
        try:
            service = SyncTeamsService()
            teams = service.execute(league=league, season=season)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Sincronização concluída com sucesso! {len(teams)} seleções sincronizadas."
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f"Erro ao sincronizar seleções: {str(e)}"
                )
            )
