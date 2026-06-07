from rest_framework.routers import DefaultRouter
from .views import FantasyLineupViewSet, FantasyTransferViewSet, PlayerViewSet, ScoreEventViewSet

router = DefaultRouter()
router.register(r'player', PlayerViewSet, basename='scores-player')
router.register(r'scores', ScoreEventViewSet, basename='scores')
router.register(r'lineups', FantasyLineupViewSet, basename='lineup')
router.register(r'transfers', FantasyTransferViewSet, basename='transfer')
