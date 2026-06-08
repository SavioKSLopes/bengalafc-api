from datetime import datetime
from unittest.mock import MagicMock
from django.test import TestCase
from django.utils.timezone import make_aware
from apps.football.models import (
    Competition,
    Fixture,
    Player,
    PlayerStatistic,
    Stage,
    Team,
    TeamStatistic, Coach,
)
from apps.football.services.sync_coaches import SyncCoachesService
from apps.football.services.sync_competitions import SyncCompetitionsService
from apps.football.services.sync_fixtures import SyncFixturesService
from apps.football.services.sync_players import SyncPlayersService
from apps.football.services.sync_stages import SyncStagesService
from apps.football.services.sync_statistics import SyncStatisticsService
from apps.football.services.sync_teams import SyncTeamsService


class FootballServicesTestCase(TestCase):
    def setUp(self) -> None:
        self.mock_client = MagicMock()

    def test_sync_teams_service(self) -> None:
        # Arrange
        self.mock_client.get_teams.return_value = [
            {
                "team": {
                    "id": 26,
                    "name": "Argentina",
                    "code": "ARG",
                    "country": "Argentina",
                    "logo": "https://media.api-sports.io/football/teams/26.png",
                    "founded": 1893,
                }
            }
        ]
        service = SyncTeamsService(api_client=self.mock_client)

        # Act
        teams = service.execute(league=1, season=2022)

        # Assert
        self.assertEqual(len(teams), 1)
        team = teams[0]
        self.assertEqual(team.name, "Argentina")
        self.assertEqual(team.external_id, 26)
        self.assertEqual(team.code, "ARG")
        self.assertEqual(Team.objects.count(), 1)

        # Test idempotency (execute again, count stays 1)
        service.execute(league=1, season=2022)
        self.assertEqual(Team.objects.count(), 1)

    def test_sync_players_service(self) -> None:
        # Arrange
        team = Team.objects.create(external_id=26, name="Argentina")
        self.mock_client.get_team_players.return_value = [
            {
                "player": {
                    "id": 154,
                    "name": "Lionel Messi",
                    "firstname": "Lionel",
                    "lastname": "Messi",
                    "age": 35,
                    "nationality": "Argentina",
                    "height": "170 cm",
                    "weight": "72 kg",
                    "photo": "https://media.api-sports.io/football/players/154.png",
                },
                "statistics": [
                    {
                        "games": {"position": "Attacker", "number": 10},
                        "team": {"id": 26, "name": "Argentina"},
                    }
                ],
            }
        ]
        service = SyncPlayersService(api_client=self.mock_client)

        # Act
        players = service.execute(team_id=26, season=2022)

        # Assert
        self.assertEqual(len(players), 1)
        player = players[0]
        self.assertEqual(player.name, "Lionel Messi")
        self.assertEqual(player.position, "Attacker")
        self.assertEqual(player.number, 10)
        self.assertEqual(player.team, team)
        self.assertEqual(Player.objects.count(), 1)

    def test_sync_competitions_service(self) -> None:
        # Arrange
        self.mock_client.get_competitions.return_value = [
            {
                "league": {
                    "id": 1,
                    "name": "World Cup",
                    "type": "Cup",
                    "logo": "https://media.api-sports.io/football/leagues/1.png",
                }
            }
        ]
        service = SyncCompetitionsService(api_client=self.mock_client)

        # Act
        competitions = service.execute(competition_id=1, season=2022)

        # Assert
        self.assertEqual(len(competitions), 1)
        comp = competitions[0]
        self.assertEqual(comp.name, "World Cup")
        self.assertEqual(comp.external_id, 1)
        self.assertEqual(Competition.objects.count(), 1)

    def test_sync_stages_service(self) -> None:
        # Arrange
        comp = Competition.objects.create(
            external_id=1, name="World Cup", season=2022
        )
        self.mock_client.get_fixtures.return_value = [
            {"league": {"round": "Group Stage - 1"}},
            {"league": {"round": "Final"}},
        ]
        service = SyncStagesService(api_client=self.mock_client)

        # Act
        stages = service.execute(competition_id=1, season=2022)

        # Assert
        self.assertEqual(len(stages), 2)
        stage_names = [s.name for s in stages]
        self.assertIn("Group Stage - 1", stage_names)
        self.assertIn("Final", stage_names)
        self.assertEqual(Stage.objects.count(), 2)

    def test_sync_fixtures_service(self) -> None:
        # Arrange
        comp = Competition.objects.create(
            external_id=1, name="World Cup", season=2022
        )
        self.mock_client.get_fixtures.return_value = [
            {
                "fixture": {
                    "id": 855735,
                    "date": "2022-12-18T15:00:00+00:00",
                    "venue": {"name": "Lusail Iconic Stadium", "city": "Lusail"},
                    "status": {"short": "FT"},
                },
                "league": {"id": 1, "round": "Final"},
                "teams": {
                    "home": {
                        "id": 26,
                        "name": "Argentina",
                        "logo": "https://media.api-sports.io/football/teams/26.png",
                    },
                    "away": {
                        "id": 2,
                        "name": "France",
                        "logo": "https://media.api-sports.io/football/teams/2.png",
                    },
                },
                "goals": {"home": 3, "away": 3},
            }
        ]
        service = SyncFixturesService(api_client=self.mock_client)

        # Act
        fixtures = service.execute(competition_id=1, season=2022)

        # Assert
        self.assertEqual(len(fixtures), 1)
        fixture = fixtures[0]
        self.assertEqual(fixture.external_id, 855735)
        self.assertEqual(fixture.home_team.name, "Argentina")
        self.assertEqual(fixture.away_team.name, "France")
        self.assertEqual(fixture.home_score, 3)
        self.assertEqual(fixture.away_score, 3)
        self.assertEqual(fixture.status, "FT")
        self.assertEqual(Fixture.objects.count(), 1)

    def test_sync_statistics_service(self) -> None:
        # Arrange
        comp = Competition.objects.create(
            external_id=1, name="World Cup", season=2022
        )
        home = Team.objects.create(external_id=26, name="Argentina")
        away = Team.objects.create(external_id=2, name="France")
        stage = Stage.objects.create(competition=comp, name="Final")
        fixture = Fixture.objects.create(
            external_id=855735,
            competition=comp,
            stage=stage,
            home_team=home,
            away_team=away,
            kickoff_at=make_aware(datetime(2022, 12, 18, 15, 0)),
            status="FT",
        )

        # Mock Team statistics
        self.mock_client.get_fixture_statistics.return_value = [
            {
                "team": {"id": 26, "name": "Argentina"},
                "statistics": [
                    {"type": "Ball Possession", "value": "54%"},
                    {"type": "Total Shots", "value": 20},
                    {"type": "Shots on Goal", "value": 10},
                    {"type": "Corner Kicks", "value": 6},
                    {"type": "Fouls", "value": 26},
                    {"type": "Offsides", "value": 4},
                    {"type": "Yellow Cards", "value": 4},
                    {"type": "Red Cards", "value": 0},
                ],
            }
        ]

        # Mock Player statistics
        self.mock_client.get_player_statistics.return_value = [
            {
                "team": {"id": 26, "name": "Argentina"},
                "players": [
                    {
                        "player": {"id": 154, "name": "Lionel Messi"},
                        "statistics": [
                            {
                                "games": {"minutes": 120, "rating": "9.20"},
                                "goals": {"total": 2, "assists": 0},
                                "shots": {"total": 5, "on": 4},
                                "passes": {"total": 60, "key": 3},
                                "tackles": {"total": 1, "interceptions": 1},
                                "cards": {"yellow": 0, "red": 0},
                            }
                        ],
                    }
                ],
            }
        ]

        service = SyncStatisticsService(api_client=self.mock_client)

        # Act
        totals = service.execute(fixture_id=855735)

        # Assert
        self.assertEqual(TeamStatistic.objects.count(), 1)
        team_stat = TeamStatistic.objects.first()
        self.assertEqual(team_stat.team, home)
        self.assertEqual(team_stat.possession, 54)
        self.assertEqual(team_stat.shots, 20)

        self.assertEqual(PlayerStatistic.objects.count(), 1)
        player_stat = PlayerStatistic.objects.first()
        self.assertEqual(player_stat.player.name, "Lionel Messi")
        self.assertEqual(player_stat.goals, 2)
        self.assertEqual(float(player_stat.rating), 9.20)
        self.assertEqual(player_stat.fixture, fixture)

    def test_sync_coaches_service(self) -> None:
        # Arrange
        team = Team.objects.create(external_id=26, name="Argentina")
        self.mock_client.get_coaches.return_value = [
            {
                "id": 1,
                "name": "Lionel Scaloni",
                "nationality": "Argentina",
                "photo": "https://media.api-sports.io/football/coachs/1.png",
                "team": {"id": 26, "name": "Argentina"},
            }
        ]
        service = SyncCoachesService(api_client=self.mock_client)

        # Act
        coaches = service.execute(team_id=26)

        # Assert
        self.assertEqual(len(coaches), 1)
        coach = coaches[0]
        self.assertEqual(coach.name, "Lionel Scaloni")
        self.assertEqual(coach.external_id, 1)
        self.assertEqual(coach.team, team)
        self.assertEqual(coach.nationality, "Argentina")
        self.assertEqual(Coach.objects.count(), 1)

        # Idempotency
        service.execute(team_id=26)
        self.assertEqual(Coach.objects.count(), 1)