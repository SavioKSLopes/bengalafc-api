from rest_framework.routers import DefaultRouter
from .views import (
    CompetitionViewSet,
    FixtureViewSet,
    PlayerStatisticViewSet,
    PlayerViewSet,
    StageViewSet,
    TeamStatisticViewSet,
    TeamViewSet,
)

router = DefaultRouter()
router.register(r"teams", TeamViewSet, basename="team")
router.register(r"players", PlayerViewSet, basename="player")
router.register(r"competitions", CompetitionViewSet, basename="competition")
router.register(r"stages", StageViewSet, basename="stage")
router.register(r"fixtures", FixtureViewSet, basename="fixture")
router.register(
    r"player-statistics", PlayerStatisticViewSet, basename="player-statistic"
)
router.register(
    r"team-statistics", TeamStatisticViewSet, basename="team-statistic"
)
