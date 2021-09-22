from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    # REQUIRED_FIELDS = ['first_name', 'last_name']
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']
    pass
    # add additional fields in here
