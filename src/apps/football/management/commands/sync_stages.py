from django.core.management.base import BaseCommand
from apps.football.services.sync_stages import SyncStagesService


class Command(BaseCommand):
    help = "Cria ou sincroniza as fases da competição de forma automática"

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
            self.style.WARNING("Iniciando sincronização de fases...")
        )
        try:
            service = SyncStagesService()
            stages = service.execute(
                competition_id=competition_id, season=season
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Sincronização concluída com sucesso! {len(stages)} fases sincronizadas."
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Erro ao sincronizar fases: {str(e)}")
            )
