from django.urls import path
from rest_framework.routers import SimpleRouter

from pictures.views import PicturesViewSet, UserPictureRelationsViewSet

router = SimpleRouter()
router.register(r'pictures', PicturesViewSet)
router.register(r'user-picture-relation', UserPictureRelationsViewSet)

urlpatterns = [
    # path('')
]
urlpatterns += router.urls
