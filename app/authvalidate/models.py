from django.db import models

from django.contrib.auth.models import User

# Create your models here.


class TokenEmail(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='token_email_user_set')
    token = models.CharField(max_length=32)
    date = models.DateTimeField(auto_now_add=True)
    typeToken = models.CharField(max_length=1, default='C')

    def __str__(self):
        return self.token

    class Meta:
        app_label = 'authvalidate'
