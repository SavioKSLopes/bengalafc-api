from django.core.management.base import BaseCommand
from apps.football.models import Team
from apps.football.services.sync_coaches import SyncCoachesService


class Command(BaseCommand):
    help = "Sincroniza técnicos com a API externa"

    def add_arguments(self, parser):
        parser.add_argument(
            "--team-id", type=int, help="ID externo do time na API (sincroniza só esse time)"
        )

    def handle(self, *args, **options):
        team_id = options.get("team_id")

        self.stdout.write(self.style.WARNING("Iniciando sincronização de técnicos..."))

        try:
            service = SyncCoachesService()

            if team_id:
                teams = Team.objects.filter(external_id=team_id)
            else:
                teams = Team.objects.filter(is_active=True)

            total = 0
            for team in teams:
                coaches = service.execute(team_id=team.external_id)
                total += len(coaches)

            self.stdout.write(
                self.style.SUCCESS(
                    f"Sincronização concluída com sucesso! {total} técnicos sincronizados."
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Erro ao sincronizar técnicos: {str(e)}")
            )