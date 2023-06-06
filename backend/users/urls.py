from django.urls import include, path
from rest_framework import routers

from users.views import CustomUserViewSet

app_name = 'users'

router = routers.DefaultRouter()
router.register(r'users', CustomUserViewSet, 'users')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/auth/', include('djoser.urls.authtoken')),
]
