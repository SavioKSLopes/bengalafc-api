from django.core.management.base import BaseCommand
from apps.football.services.sync_statistics import SyncStatisticsService


class Command(BaseCommand):
    help = "Sincroniza estatísticas de partidas (equipes e jogadores) com a API externa"

    def add_arguments(self, parser):
        parser.add_argument(
            "--fixture-id",
            type=int,
            help="Sincroniza estatísticas apenas desta partida (external_id).",
        )
        parser.add_argument(
            "--competition-id",
            type=int,
            help="Sincroniza estatísticas para partidas desta competição.",
        )

    def handle(self, *args, **options):
        fixture_id = options.get("fixture-id")
        competition_id = options.get("competition-id")

        self.stdout.write(
            self.style.WARNING("Iniciando sincronização de estatísticas...")
        )
        try:
            service = SyncStatisticsService()
            totals = service.execute(
                fixture_id=fixture_id, competition_id=competition_id
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Sincronização concluída com sucesso!\n"
                    f"- Estatísticas de equipe: {totals['team_stats']}\n"
                    f"- Estatísticas de jogadores: {totals['player_stats']}"
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f"Erro ao sincronizar estatísticas: {str(e)}"
                )
            )
