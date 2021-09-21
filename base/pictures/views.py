from django.db.models import Count, Case, When
from django.http import JsonResponse
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend, filters, FilterSet
from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from pictures.api.serializers import PictureSerializer, PictureRelationSerializer, PictureUpdateSerializer
from pictures.models import Picture, UserPictureRelation
from pictures.permissions import IsOwnerOrReadOnly


class PictureFilter(FilterSet):
    min_likes = filters.NumberFilter(field_name="likes_count", lookup_expr='gte')
    max_likes = filters.NumberFilter(field_name="likes_count", lookup_expr='lte')


class PicturesViewSet(ModelViewSet):
    parser_classes = [MultiPartParser, JSONParser, FormParser]
    queryset = Picture.objects.all().annotate(
        likes_count=Count(Case(When(userpicturerelation__like=True, then=1))))

    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filter_class = PictureFilter
    # filter_fields = []
    search_fields = ['name', 'description']
    ordering_fields = ['time_create', 'time_update']

    def perform_create(self, serializer):
        serializer.validated_data['owner'] = self.request.user
        serializer.save()

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return PictureUpdateSerializer
        else:
            return PictureSerializer


def bool_validator(value, serializer, field: str):
    if value in ['True', 'False', True, False]:
        serializer.validated_data[field] = value
        return True
    return not value
    # return Response({'detail': 'значение поля like должно быть типа bool'}, status=status.HTTP_400_BAD_REQUEST)


class UserPictureRelationsViewSet(ModelViewSet):
    parser_classes = [MultiPartParser, JSONParser, FormParser]

    queryset = UserPictureRelation.objects.all().select_related('user')
    serializer_class = PictureRelationSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = []
    lookup_field = 'picture'
    # http_method_names = ['get', 'head', 'put', 'patch']

    def perform_update(self, serializer):
        bool_validator(self.request.data.get('like'), serializer, 'like')
        bool_validator(self.request.data.get('in_favorites'), serializer, 'in_favorites')
        serializer.save()

    def perform_create(self, serializer):
        serializer.validated_data['user'] = self.request.user
        serializer.save()

    def get_object(self):
        if self.request.method not in ['DELETE', 'GET']:
            obj, created = UserPictureRelation.objects.get_or_create(user=self.request.user,
                                                                     picture_id=self.kwargs['picture'])
        elif self.request.method in ['GET'] and not bool(self.request.user and self.request.user.is_authenticated):
            obj = []
        else:
            obj = UserPictureRelation.objects.filter(user=self.request.user, picture_id=self.kwargs['picture']).first()
        return obj

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance:
            return Response({'detail': 'Объект не найден'}, status=status.HTTP_204_NO_CONTENT)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance:
            return Response({'detail': 'Объект не найден'}, status=status.HTTP_204_NO_CONTENT)
        self.perform_destroy(instance)
        return Response({'detail': 'Объект успешно удалён'}, status=status.HTTP_204_NO_CONTENT)
