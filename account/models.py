from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class User(AbstractUser):
    username = models.TextField(unique=True)
    openSecret = models.TextField()
    superUserId = models.BigIntegerField()
    cqUrl = models.TextField(default='')
    pornSwitch = models.BooleanField(default=False)

    class Meta:
        db_table = "users_table"


class Command(models.Model):
    patternString = models.TextField()
    outputCommand = models.TextField()
    maxLength = models.IntegerField()
    openRe = models.BooleanField(default=False)
    nickname = models.TextField()
    belong = models.ForeignKey(User, related_name='command', on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = "command_table"


class Group(models.Model):
    groupId = models.BigIntegerField()
    belong = models.ForeignKey(Command, related_name='group', on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = "group_table"


class Person(models.Model):
    userId = models.BigIntegerField()
    nickname = models.TextField()
    inGroup = models.BooleanField(default=True)
    count = models.BigIntegerField(default=0)
    belong = models.ForeignKey(Group, related_name='person', on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = "person_table"
        ordering = ['-count']

