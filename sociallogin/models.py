from django.contrib.auth.models import User
from django.db import models


# Create your models here.
# class Create_Label(models.Model):
#
#     name = models.CharField("label", max_length=254)
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='label_user', default="admin1")
#
#
# class Create_Notes(models.Model):
#     objects = None
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
#     title = models.CharField(max_length=500, blank=True, )
#     note = models.TextField()
#
#     def __str__(self):
#         return self.title