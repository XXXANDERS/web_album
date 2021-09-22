from django.shortcuts import render
from rest_framework import status
from rest_framework.parsers import MultiPartParser, JSONParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from pictures.api.serializers import UserRegistrationSerializer
from users.models import CustomUser


class UsersViewSet(ModelViewSet):
    parser_classes = [MultiPartParser, JSONParser, FormParser]
    queryset = CustomUser.objects.all()
    serializer_class = UserRegistrationSerializer
    http_method_names = ['head', 'post', 'put', 'patch', 'delete']


# class Register(APIView):
#     http_method_names = ['post', 'put', 'patch']
#
#     def post(self, request):
#         user = CustomUser.objects.create(
#             username=request.data.get('email'),
#             email=request.data.get('email'),
#             first_name=request.data.get('firstName'),
#             last_name=request.data.get('lastName'))
#
#         user.set_password(str(request.data.get('password')))
#         user.save()
#         return Response({"status": "success", "response": "User Successfully Created"}, status=status.HTTP_201_CREATED)
