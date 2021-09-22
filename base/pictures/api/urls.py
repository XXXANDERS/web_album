from django.urls import path
from rest_framework.routers import SimpleRouter

from pictures.views import PicturesViewSet, UserPictureRelationsViewSet, api_root
from users.views import UsersViewSet

router = SimpleRouter()
router.register(r'pictures', PicturesViewSet)
router.register(r'user-picture-relations', UserPictureRelationsViewSet)
router.register(r'users', UsersViewSet)
urlpatterns = [
    # path('')
    path('', api_root),
]
urlpatterns += router.urls
