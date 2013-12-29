from django.db import models
from django.contrib.auth.models import User


class AbqUser(models.Model):
    """ Abaqual users class 

    Abaqual user is a Django User with an activation 
    key and its expiration date.
    """
    user           = models.OneToOneField(User)
    activation_key = models.CharField(max_length=40)
    key_expiration = models.DateTimeField()

    def __unicode__(self):
        return self.user.username

    class Meta:
        verbose_name = 'Abaqual user'
