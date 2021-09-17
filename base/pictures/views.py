from django.db.models import Count, Case, When
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend, filters
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.viewsets import ModelViewSet

from pictures.api.serializers import PictureSerializer, PictureRelationSerializer, PictureUpdateSerializer
from pictures.models import Picture, UserPictureRelation
from pictures.permissions import IsOwnerOrReadOnly, RelationIsOwnerOrReadOnly


# class ProductFilter(filters.FilterSet):
#     min_price = filters.NumberFilter(field_name="price", lookup_expr='gte')
#     max_price = filters.NumberFilter(field_name="price", lookup_expr='lte')
#
#     class Meta:
#         model = UserPictureRelation
#         fields = ['category', 'in_stock']


class PicturesViewSet(ModelViewSet):
    parser_classes = [MultiPartParser, JSONParser, FormParser]
    queryset = Picture.objects.all().annotate(
        likes_count=Count(Case(When(userpicturerelation__like=True, then=1))))
    # serializer_class = PictureSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter, ]
    # filter_fields = ['likes_count']
    search_fields = ['name', 'description']
    ordering_fields = ['time_create', 'time_update']

    def perform_create(self, serializer):
        serializer.validated_data['owner'] = self.request.user
        serializer.save()

    def get_serializer_class(self):
        # print('ACTION = ', self.action)
        if self.request.method in ['PUT', 'PATCH']:
            return PictureUpdateSerializer
        else:
            return PictureSerializer


class UserPictureRelationsViewSet(ModelViewSet):
    parser_classes = [MultiPartParser, JSONParser, FormParser]
    queryset = UserPictureRelation.objects.all()
    serializer_class = PictureRelationSerializer
    permission_classes = [IsAuthenticated, RelationIsOwnerOrReadOnly]
    filter_backends = []
    lookup_field = 'picture'

    def perform_create(self, serializer):
        serializer.validated_data['user'] = self.request.user
        serializer.save()

    def get_object(self):
        obj, created = UserPictureRelation.objects.get_or_create(user=self.request.user,
                                                                 picture_id=self.kwargs['picture'])
        print('created', created)
        return obj

    # def perform_update(self, serializer):
    #     print(serializer.validated_data['like'], type(serializer.validated_data['like']))
    #     print(serializer.validated_data['in_favorites'], type(serializer.validated_data['in_favorites']))
    #     if serializer.validated_data['like'] is None:
    #         serializer.validated_data.pop('like')
    #     if serializer.validated_data['in_favorites'] is None:
    #         serializer.validated_data.pop('in_favorites')
    #     serializer.save()
