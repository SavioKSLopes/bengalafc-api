from django.core.management.base import BaseCommand
from apps.football.services.sync_fixtures import SyncFixturesService


class Command(BaseCommand):
    help = "Sincroniza as partidas (fixtures) com a API externa"

    def add_arguments(self, parser):
        parser.add_argument(
            "--competition-id", type=int, help="ID da competição na API externa"
        )
        parser.add_argument(
            "--season", type=int, help="Ano da temporada (ex: 2022)"
        )

    def handle(self, *args, **options):
        competition_id = options.get("competition-id")
        season = options.get("season")

        self.stdout.write(
            self.style.WARNING("Iniciando sincronização de partidas...")
        )
        try:
            service = SyncFixturesService()
            fixtures = service.execute(
                competition_id=competition_id, season=season
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Sincronização concluída com sucesso! {len(fixtures)} partidas sincronizadas."
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f"Erro ao sincronizar partidas: {str(e)}"
                )
            )
