from django.db import models
from django.contrib.auth.models import User

class Expert(models.Model):
    user = models.OneToOneField(User)
    
    def __unicode__(self):
        return self.user.username
    
