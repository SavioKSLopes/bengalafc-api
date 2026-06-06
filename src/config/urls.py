from django.contrib import admin
from django.urls import path, include
from .views import hello_world, pag2
from apps.users.api.router import router as users_router
from apps.ranking.api.router import router as ranking_router

urlpatterns = [
    path('admin/', admin.site.urls),
    path('hello/', hello_world, name='hello_world'),
    path('pag2/', pag2, name='pag2'),
    
    # API URLs
    path('api/', include(users_router.urls)),
    path('api/', include(ranking_router.urls)),
    
    # OAuth2 URLs
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
]