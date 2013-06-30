from django.db import models
from django.contrib.auth.models import User




class AbqUser(models.Model):

    ABAQUAL_STATUS = (
        ('EX', 'Expert'),
        ('PR', 'Professional'),
        ('CU', 'Customer'),
        )
    user           = models.OneToOneField(User)
    abaqual_status = models.CharField(max_length=2, choices=ABAQUAL_STATUS)
    activation_key = models.CharField(max_length=40)
    key_expires_on = models.DateTimeField()
    
    def __unicode__(self):
        return self.user.username

    class Meta:
        verbose_name = 'Abaqual User'




class Company(models.Model):
    
    owner    = models.ForeignKey(AbqUser,related_name='company_owner')
    exployee = models.ManyToManyField(AbqUser,related_name='company_employee', blank=True)
    name     = models.CharField(max_length=200)
    
    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'Company'




class Workspace(models.Model):
    
    company = models.ForeignKey(Company,related_name='workspace_owner')  
    name    = models.CharField(max_length=200)
    
    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'Workspace'




class Project(models.Model):
    
    company  = models.ForeignKey(Company,related_name='project_owner', null=True, blank=True)  
    customer = models.ForeignKey(AbqUser,related_name='project_customer',null=True, blank=True)  
    name     = models.CharField(max_length=200)
    email    = models.EmailField()

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'Project'
