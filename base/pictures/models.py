from django.db import models

from users.models import CustomUser


class Picture(models.Model):
    name = models.CharField(max_length=50, blank=False)
    description = models.TextField(max_length=3000, blank=True)
    src = models.ImageField(upload_to='photos/%Y/%m/%d/')
    owner = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='my_pictures')
    readers = models.ManyToManyField(CustomUser, through='UserPictureRelation', related_name='pictures')

    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.name} by {self.owner.first_name} {self.owner.last_name}'


class UserPictureRelation(models.Model):
    RATE_CHOICES = (
        (1, 'Ok'),
        (2, 'Fine'),
        (3, 'Good'),
        (4, 'Amazing'),
        (5, 'Incredible'),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    picture = models.ForeignKey(Picture, on_delete=models.CASCADE)
    like = models.BooleanField(default=False, null=True)
    in_favorites = models.BooleanField(default=False, null=True)
    rate = models.PositiveIntegerField(choices=RATE_CHOICES, null=True)

    def __str__(self):
        return f'{self.user.username}: {self.picture.name}, RATE: {self.rate}'

    # unique_together = (('user', 'picture'),)

    class Meta:
        unique_together = (('user', 'picture'),)
