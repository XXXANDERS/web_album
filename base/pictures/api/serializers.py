from rest_framework import serializers
from rest_framework.fields import NullBooleanField
from rest_framework.validators import UniqueTogetherValidator

from pictures.models import Picture, UserPictureRelation
from users.models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id',)


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


class UniqueTV(UniqueTogetherValidator):

    def __init__(self, queryset, fields=None, message=None):
        user = UserSerializer(default=CustomUser.objects.first(), required=False)
        self.queryset = queryset
        self.fields = [user, 'pictures']
        self.message = message or self.message


class PictureRelationSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance is not None:
            # self.fields.pop('picture', None)
            self.fields.get('picture').read_only = True

    # def update(self, instance, validated_data):
    #     print(validated_data['like'], type(validated_data['like']))
    #     print(validated_data['in_favorites'], type(validated_data['in_favorites']))
    #     # instance.email = validated_data.get('email', instance.email)
    #     # instance.content = validated_data.get('content', instance.content)
    #     # instance.created = validated_data.get('created', instance.created)
    #     return instance

    def update(self, instance, validated_data):
        # print(validated_data)
        return super(PictureRelationSerializer, self).update(instance, validated_data)

    #
    # like = NullBooleanField()
    # in_favorites = NullBooleanField()

    class Meta:
        model = UserPictureRelation
        # user = serializers.HiddenField(default=CustomUser.objects.first())
        # user = serializers.HiddenField(default=serializers.CurrentUserDefault())
        # user = serializers.CurrentUserDefault()
        # user = UserSerializer(default=CustomUser.objects.first(), required=False)
        # user = UserSerializer(read_only=True, default=serializers.CurrentUserDefault())
        fields = ('id', 'user', 'picture', 'like', 'in_favorites', 'rate')
        read_only_fields = ('user',)
        extra_kwargs = {
            # 'user': {'required': False},
            'like': {'required': False},
            # 'in_favorites': {'required': False},
            # 'rate': {'required': False},
        }
        # validators = [
        #     UniqueTogetherValidator(
        #         queryset=UserPictureRelation.objects.all(),
        #         fields=['user', 'picture'],
        #         message='Данное отношение уже было добавлено. Вы можете только редактировать или удалить его',
        #     )
        # ]
