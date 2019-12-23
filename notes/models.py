from django.contrib.auth.models import User, AbstractUser
from django.db import models


class Media(models.Model):
    file = models.URLField(max_length=250)


class Data(models.Model):
    path = models.CharField(max_length=130)
    datetime = models.CharField(max_length=60)
    filename = models.CharField(max_length=60)


class Label(models.Model):
    name = models.CharField("name of label", max_length=254)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='label_user', default="admin")

    def __str__(self):
        return self.name

    def __repr__(self):
        return "Label({!r},{!r})".format(self.user, self.name)

    class Meta:
        verbose_name = 'label'
        verbose_name_plural = 'labels'


class Notes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    title = models.CharField(max_length=500, blank=True, )
    note = models.CharField(max_length=500, )
    image = models.ImageField(max_length=500, blank=True, null=True, upload_to="media")
    is_archive = models.BooleanField("is_archived", default=False)
    is_trashed = models.BooleanField("delete_note", default=False)
    label = models.ManyToManyField(Label, related_name="label", blank=True)
    collaborators = models.ManyToManyField(User, related_name='collaborators', blank=True)
    is_copied = models.BooleanField("make a copy", default=False)
    checkbox = models.BooleanField("check box", default=False)
    is_pined = models.BooleanField("is pinned", default=False)
    url = models.URLField("url", blank=True)
    reminder = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.note

    def __repr__(self):
        return "Note({!r},{!r},{!r})".format(self.user, self.title, self.note)

    class Meta:
        verbose_name = 'Note'
        verbose_name_plural = 'Notes'
