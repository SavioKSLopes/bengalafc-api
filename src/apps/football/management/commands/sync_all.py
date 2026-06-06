from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Executa a cadeia completa de sincronização do módulo football"

    def add_arguments(self, parser):
        parser.add_argument(
            "--competition-id",
            type=int,
            help="ID da competição na API externa (ex: 1 para Copa do Mundo)",
        )
        parser.add_argument(
            "--season", type=int, help="Ano da temporada (ex: 2022)"
        )

    def handle(self, *args, **options):
        comp_id = options.get("competition_id")
        season = options.get("season")

        self.stdout.write(
            self.style.MIGRATE_HEADING(
                "=== INICIANDO FLUXO COMPLETO DE SINCRONIZAÇÃO ==="
            )
        )

        # 1. Teams
        self.stdout.write(
            self.style.MIGRATE_LABEL("Passo 1/6: Sincronizando seleções...")
        )
        teams_kwargs = {}
        if comp_id:
            teams_kwargs["league"] = comp_id
        if season:
            teams_kwargs["season"] = season
        call_command("sync_teams", **teams_kwargs)

        # 2. Players
        self.stdout.write(
            self.style.MIGRATE_LABEL("Passo 2/6: Sincronizando jogadores...")
        )
        players_kwargs = {}
        if season:
            players_kwargs["season"] = season
        call_command("sync_players", **players_kwargs)

        # 3. Competitions
        self.stdout.write(
            self.style.MIGRATE_LABEL("Passo 3/6: Sincronizando competições...")
        )
        comp_kwargs = {}
        if comp_id:
            comp_kwargs["competition_id"] = comp_id
        if season:
            comp_kwargs["season"] = season
        call_command("sync_competitions", **comp_kwargs)

        # 4. Stages
        self.stdout.write(
            self.style.MIGRATE_LABEL("Passo 4/6: Sincronizando fases...")
        )
        stages_kwargs = {}
        if comp_id:
            stages_kwargs["competition_id"] = comp_id
        if season:
            stages_kwargs["season"] = season
        call_command("sync_stages", **stages_kwargs)

        # 5. Fixtures
        self.stdout.write(
            self.style.MIGRATE_LABEL("Passo 5/6: Sincronizando partidas...")
        )
        fixtures_kwargs = {}
        if comp_id:
            fixtures_kwargs["competition_id"] = comp_id
        if season:
            fixtures_kwargs["season"] = season
        call_command("sync_fixtures", **fixtures_kwargs)

        # 6. Statistics
        self.stdout.write(
            self.style.MIGRATE_LABEL("Passo 6/6: Sincronizando estatísticas...")
        )
        stats_kwargs = {}
        if comp_id:
            stats_kwargs["competition_id"] = comp_id
        call_command("sync_statistics", **stats_kwargs)

        self.stdout.write(
            self.style.SUCCESS(
                "=== FLUXO COMPLETO DE SINCRONIZAÇÃO FINALIZADO COM SUCESSO ==="
            )
        )
