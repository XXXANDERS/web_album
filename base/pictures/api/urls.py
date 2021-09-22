from django.urls import path
from rest_framework.routers import SimpleRouter

from pictures.views import PicturesViewSet, UserPictureRelationsViewSet, api_root

router = SimpleRouter()
router.register(r'pictures', PicturesViewSet)
router.register(r'user-picture-relations', UserPictureRelationsViewSet)
urlpatterns = [
    path('', api_root),
]
urlpatterns += router.urls
