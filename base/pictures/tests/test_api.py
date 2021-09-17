# не забудьте создать папку img в каталоге tests и добавить файлы 1.jpg, 2.png

import os

from django.db.models import Count, Case, When
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from base import settings
from pictures.api.serializers import PictureSerializer
from pictures.models import Picture
from users.models import CustomUser


def set_absolute_urls(files: list):
    for file in files:
        if file.get('src') != -1:
            file['src'] = 'http://testserver' + file.get('src')


def set_absolute_url(file: dict):
    if file.get('src') != -1:
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
        response = self.client.put(url, data=data)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual('photo-1-new', response.data.get('name'))

        file_path = os.path.abspath('pictures/tests/img/2.png')
        file = open(file_path, 'rb')
        data = {
            'src': file
        }
        response = self.client.put(url, data=data)
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

    def test_create_not_authenticated(self):
        url = reverse('picture-list')
        file_path = os.path.abspath('pictures/tests/img/1.jpg')
        file = open(file_path, 'rb')
        data = {
            'name': 'photo2',
            'src': file
        }
        response = self.client.post(url, data=data)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_update_not_authenticated(self):
        url = reverse('picture-detail', kwargs={'pk': self.picture_1.pk})
        data = {
            'name': 'photo-1-new',
        }
        response = self.client.put(url, data=data)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_delete_not_authenticated(self):
        url = reverse('picture-detail', kwargs={'pk': self.picture_1.pk})
        data = {
            'name': 'photo-1-new',
        }
        response = self.client.put(url, data=data)
        print(response.data)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_update_not_owner(self):
        self.client.force_login(self.user_2)
        url = reverse('picture-detail', kwargs={'pk': self.picture_1.pk})
        data = {
            'name': 'photo-1-new',
        }
        response = self.client.put(url, data=data)
        print(response.data)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_delete_not_owner(self):
        self.client.force_login(self.user_2)
        url = reverse('picture-detail', kwargs={'pk': self.picture_1.pk})
        data = {
            'name': 'photo-1-new',
        }
        response = self.client.delete(url, data=data)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

