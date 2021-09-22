from rest_framework import serializers
from rest_framework.fields import NullBooleanField, BooleanField
from rest_framework.validators import UniqueTogetherValidator

from pictures.models import Picture, UserPictureRelation
from users.models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username')


class PictureSerializer(serializers.ModelSerializer):
    likes_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Picture
        # fields = '__all__'
        fields = ('id', 'name', 'description', 'src', 'owner', 'time_create', 'time_update', 'likes_count')
        # read_only_fields = ('time_create', 'time_update')


class PictureUpdateSerializer(PictureSerializer):
    class Meta:
        model = Picture
        fields = ('id', 'name', 'description', 'src', 'owner', 'time_create', 'time_update', 'likes_count')
        extra_kwargs = {
            'src': {'required': False},
            'name': {'required': False}
        }


class PictureRelationSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance is not None:
            # self.fields.pop('picture', None)
            self.fields.get('picture').read_only = True

    # like = BooleanField(required=False, read_only=True)
    # in_favorites = BooleanField(required=False, read_only=True)
    user = UserSerializer(read_only=True, default=serializers.CurrentUserDefault())

    class Meta:
        model = UserPictureRelation

        fields = ('id', 'user', 'picture', 'like', 'in_favorites', 'rate')
        read_only_fields = ('user', 'like', 'in_favorites')
        extra_kwargs = {
            # 'user': {'required': False},
            # 'like': {'required': False},
            # 'in_favorites': {'required': False},
            # 'rate': {'required': False},
        }
        validators = [
            UniqueTogetherValidator(
                queryset=UserPictureRelation.objects.all(),
                fields=['user', 'picture'],
                message='Данное отношение уже было добавлено. Вы можете только редактировать или удалить его',
            )
        ]
