from django.db import models

# Create your models here.


class LogModel(models.Model):
    msg_type = models.TextField()
    msg_text = models.TextField()
    msg_date = models.DateTimeField().auto_now_add
    msg_time = models.TimeField().auto_now_add
