from rest_framework.routers import DefaultRouter
from .views import PlayerViewSet, ScoreEventViewSet

router = DefaultRouter()
router.register(r'player', PlayerViewSet, basename='scores-player')
router.register(r'scores', ScoreEventViewSet, basename='scores')