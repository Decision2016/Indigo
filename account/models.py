from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class User(AbstractUser):
    username = models.TextField(unique=True)
    open_secret = models.TextField()
    super_user_id = models.BigIntegerField()
    cq_url = models.TextField(default='')
    porn_switch = models.BooleanField(default=False)

    class Meta:
        db_table = "users_table"


class Command(models.Model):
    pattern_string = models.TextField()
    output_command = models.TextField()
    max_length = models.IntegerField()
    open_re = models.BooleanField(default=False)
    nickname = models.TextField()
    belong = models.ForeignKey(User, related_name='command', on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = "command_table"


class Group(models.Model):
    group_id = models.BigIntegerField()
    belong = models.ForeignKey(Command, related_name='group', on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = "group_table"


class Person(models.Model):
    user_id = models.BigIntegerField()
    nickname = models.TextField()
    in_group = models.BooleanField(default=True)
    count = models.BigIntegerField(default=0)
    group = models.ForeignKey(Group, related_name='person', on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = "person_table"
        ordering = ['-count']

