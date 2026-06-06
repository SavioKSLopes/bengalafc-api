from django.core.management.base import BaseCommand
from apps.football.services.sync_competitions import SyncCompetitionsService


class Command(BaseCommand):
    help = "Sincroniza competições/torneios com a API externa"

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
            self.style.WARNING("Iniciando sincronização de competições...")
        )
        try:
            service = SyncCompetitionsService()
            competitions = service.execute(
                competition_id=competition_id, season=season
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Sincronização concluída com sucesso! {len(competitions)} competições sincronizadas."
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f"Erro ao sincronizar competições: {str(e)}"
                )
            )
