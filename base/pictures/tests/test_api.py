# не забудьте создать папку img в каталоге tests и добавить файлы 1.jpg, 2.png

import os

from django.db.models import Count, Case, When
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from base import settings
from pictures.api.serializers import PictureSerializer, PictureRelationSerializer
from pictures.models import Picture, UserPictureRelation
from users.models import CustomUser


def set_absolute_urls(files: list):
    for file in files:
        if file.get('src'):
            file['src'] = 'http://testserver' + file.get('src')


def set_absolute_url(file: dict):
    if file.get('src'):
        old_file_src = file['src']
        file['src'] = 'http://testserver' + file.get('src')
        return old_file_src


def delete_file(path):
    path = path[1:]
    file_path = os.path.abspath(path)
    os.remove(file_path)


class PicturesApiTestCase(APITestCase):
    def setUp(self):
        self.user_1 = CustomUser.objects.create(username='user1')
        self.user_2 = CustomUser.objects.create(username='user2')
        self.picture_1 = Picture.objects.create(name='pic1', src='img1.png', owner=self.user_1)
        self.picture_2 = Picture.objects.create(name='pic2', src='img2.png', owner=self.user_2)
        # self.picture_3 = Picture.objects.create(name='pic3', src='img3.png', owner=self.user_1)

    def test_get_pictures(self):
        url = reverse('picture-list')
        response = self.client.get(url)
        pictures = Picture.objects.all().annotate(likes_count=Count(Case(When(userpicturerelation__like=True, then=1))))
        serializer_data = PictureSerializer(pictures, many=True).data
        set_absolute_urls(serializer_data)
        self.assertEqual(serializer_data, response.data)

    def test_create_picture(self):
        url = reverse('picture-list')
        count_before = Picture.objects.count()
        self.client.force_login(self.user_1)
        file_path = os.path.abspath('pictures/tests/img/1.jpg')
        file = open(file_path, 'rb')
        data = {
            'name': 'photo3',
            'src': file
        }
        response = self.client.post(url, data=data)
        picture = Picture.objects.last()
        serializer_data = PictureSerializer(picture).data
        old_path = set_absolute_url(serializer_data)
        count_after = Picture.objects.count()
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(serializer_data, response.data)
        self.assertEqual(count_before, count_after - 1)
        delete_file(old_path)

    def test_update_picture(self):
        url = reverse('picture-detail', kwargs={'pk': self.picture_1.pk})
        self.client.force_login(self.user_1)
        data = {
            'name': 'photo-1-new',
        }
        response = self.client.patch(url, data=data)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual('photo-1-new', response.data.get('name'))

        file_path = os.path.abspath('pictures/tests/img/2.png')
        file = open(file_path, 'rb')
        data = {
            'src': file
        }
        response = self.client.patch(url, data=data)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        import datetime
        now = datetime.datetime.now()
        path = f'/media/photos/{now.strftime("%Y/%m/%d")}/2.png'
        self.assertEqual(f'http://testserver{path}', response.data.get('src'))
        delete_file(path)

    def test_delete_picture(self):
        url = reverse('picture-detail', kwargs={'pk': self.picture_1.pk})
        count_before = Picture.objects.count()
        self.client.force_login(self.user_1)
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        count_after = Picture.objects.count()
        self.assertEqual(count_before, count_after + 1)

    def test_get_picture(self):
        url = reverse('picture-detail', kwargs={'pk': self.picture_1.pk})
        response = self.client.get(url)
        picture = Picture.objects.annotate(likes_count=Count(Case(When(userpicturerelation__like=True, then=1)))).get(
            pk=self.picture_1.pk)

        serializer_data = PictureSerializer(picture).data
        set_absolute_url(serializer_data)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_create_picture_not_authenticated(self):
        url = reverse('picture-list')
        file_path = os.path.abspath('pictures/tests/img/1.jpg')
        file = open(file_path, 'rb')
        data = {
            'name': 'photo2',
            'src': file
        }
        response = self.client.post(url, data=data)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_update_picture_not_authenticated(self):
        url = reverse('picture-detail', kwargs={'pk': self.picture_1.pk})
        data = {
            'name': 'photo-1-new',
        }
        response = self.client.patch(url, data=data)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_delete_picture_not_authenticated(self):
        url = reverse('picture-detail', kwargs={'pk': self.picture_1.pk})
        data = {
            'name': 'photo-1-new',
        }
        response = self.client.patch(url, data=data)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_update_picture_not_owner(self):
        self.client.force_login(self.user_2)
        url = reverse('picture-detail', kwargs={'pk': self.picture_1.pk})
        data = {
            'name': 'photo-1-new',
        }
        response = self.client.patch(url, data=data)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_delete_picture_not_owner(self):
        self.client.force_login(self.user_2)
        url = reverse('picture-detail', kwargs={'pk': self.picture_1.pk})
        data = {
            'name': 'photo-1-new',
        }
        response = self.client.delete(url, data=data)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)


class PictureRelationApiTestCase(APITestCase):
    def setUp(self):
        self.user_1 = CustomUser.objects.create(username='user1')
        self.user_2 = CustomUser.objects.create(username='user2')
        self.picture_1 = Picture.objects.create(name='pic1', src='img1.png', owner=self.user_1)
        self.picture_2 = Picture.objects.create(name='pic2', src='img2.png', owner=self.user_2)
        self.relation_1 = UserPictureRelation.objects.create(user=self.user_1, picture=self.picture_1, rate=1)
        self.relation_2 = UserPictureRelation.objects.create(user=self.user_2, picture=self.picture_1, rate=3)
        self.relation_3 = UserPictureRelation.objects.create(user=self.user_2, picture=self.picture_2, rate=3)

    def test_get_relations(self):
        url = reverse('userpicturerelation-list')
        response = self.client.get(url)
        relations = UserPictureRelation.objects.all()
        serializer_data = PictureRelationSerializer(relations, many=True).data
        self.assertEqual(serializer_data, response.data)

    def test_create_relation(self):
        url = reverse('userpicturerelation-list')
        count_before = UserPictureRelation.objects.count()
        self.client.force_login(self.user_1)
        data = {
            'picture': self.picture_2.id,
            'like': True,
        }
        response = self.client.post(url, data=data)
        relation = UserPictureRelation.objects.last()
        serializer_data = PictureRelationSerializer(relation).data
        count_after = UserPictureRelation.objects.count()
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(serializer_data, response.data)
        self.assertEqual(count_before, count_after - 1)

    def test_update_relation(self):
        url = reverse('userpicturerelation-detail', kwargs={'picture': self.picture_1.pk})
        self.client.force_login(self.user_1)
        data = {
            'like': True,
            'rate': 5,
        }
        self.client.force_login(self.user_1)
        response = self.client.put(url, data)
        relation = UserPictureRelation.objects.get(picture=self.picture_1, user=self.user_1)
        serializer_data = PictureRelationSerializer(relation).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(True, serializer_data.get('like'))
        self.assertEqual(5, serializer_data.get('rate'))

    def test_delete_relation(self):
        url = reverse('userpicturerelation-detail', kwargs={'picture': self.picture_1.pk})
        count_before = UserPictureRelation.objects.count()
        self.client.force_login(self.user_1)
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual({'detail': 'Объект успешно удалён'}, response.data)
        count_after = UserPictureRelation.objects.count()
        self.assertEqual(count_before, count_after + 1)

    def test_get_relation(self):
        url = reverse('userpicturerelation-detail', kwargs={'picture': self.picture_1.pk})
        self.client.force_login(self.user_1)
        response = self.client.get(url)
        relation = UserPictureRelation.objects.get(picture=self.picture_1, user=self.user_1)
        serializer_data = PictureRelationSerializer(relation).data
        # print(response.data)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_create_relation_not_authenticated(self):
        url = reverse('userpicturerelation-list')
        count_before = UserPictureRelation.objects.count()
        data = {
            'picture': self.picture_2.id,
            'like': True,
        }
        response = self.client.post(url, data=data)
        relation = UserPictureRelation.objects.last()
        count_after = UserPictureRelation.objects.count()
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual(count_before, count_after)

    def test_update_relation_not_authenticated(self):
        url = reverse('userpicturerelation-detail', kwargs={'picture': self.picture_1.pk})
        data = {
            'like': True,
            'rate': 5,
        }
        response = self.client.put(url, data)
        relation = UserPictureRelation.objects.get(picture=self.picture_1, user=self.user_1)
        serializer_data = PictureRelationSerializer(relation).data
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual(False, serializer_data.get('like'))
        self.assertEqual(1, serializer_data.get('rate'))

    def test_delete_relation_not_authenticated(self):
        url = reverse('userpicturerelation-detail', kwargs={'picture': self.picture_1.pk})
        count_before = UserPictureRelation.objects.count()
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        count_after = UserPictureRelation.objects.count()
        self.assertEqual(count_before, count_after)

    def test_get_relation_not_authenticated(self):
        url = reverse('userpicturerelation-detail', kwargs={'picture': self.picture_1.pk})
        response = self.client.get(url)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

    def test_update_relation_not_owner(self):
        url = reverse('userpicturerelation-detail', kwargs={'picture': self.picture_2.pk})
        data = {
            'like': True,
            'rate': 5,
        }
        self.client.force_login(self.user_1)
        response = self.client.put(url, data)
        relation = UserPictureRelation.objects.get(picture=self.picture_2.pk, user=self.user_1)
        relation2 = UserPictureRelation.objects.get(picture=self.picture_2.pk, user=self.user_2)
        serializer_data = PictureRelationSerializer(relation).data
        serializer_data2 = PictureRelationSerializer(relation2).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(True, serializer_data.get('like'))
        self.assertEqual(5, serializer_data.get('rate'))
        self.assertEqual(False, serializer_data2.get('like'))
        self.assertEqual(3, serializer_data2.get('rate'))

    def test_delete_relation_not_owner(self):
        url = reverse('userpicturerelation-detail', kwargs={'picture': self.picture_2.pk})
        count_before = UserPictureRelation.objects.count()
        self.client.force_login(self.user_1)
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        count_after = UserPictureRelation.objects.count()
        self.assertEqual(count_before, count_after)

    def test_get_relation_not_owner(self):
        url = reverse('userpicturerelation-detail', kwargs={'picture': self.picture_2.pk})
        self.client.force_login(self.user_1)
        response = self.client.get(url)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
