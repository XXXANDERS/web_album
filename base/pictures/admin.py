from django.contrib import admin
from django.contrib.admin import ModelAdmin

from pictures.models import Picture, UserPictureRelation


@admin.register(Picture)
class PictureAdmin(ModelAdmin):
    pass


@admin.register(UserPictureRelation)
class PictureAdmin(ModelAdmin):
    pass
