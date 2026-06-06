from rest_framework.routers import DefaultRouter
from .views import RankingViewSet

router = DefaultRouter()
router.register(r'ranking', RankingViewSet, basename='ranking')