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
    key_expiration = models.DateTimeField()
    
    def __unicode__(self):
        return self.user.username

    class Meta:
        verbose_name = 'Abaqual user'




class Company(models.Model):
    
    name     = models.CharField(max_length=100)
    owner    = models.ForeignKey(AbqUser,related_name='company_owner')
    employee = models.ManyToManyField(AbqUser,related_name='company_employee', blank=True)
        
    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'Company'




class Hardware(models.Model):

    name           = models.CharField(max_length=100)
    type           = models.CharField(max_length=100)
    price_per_hour = models.FloatField()
    virtual_cpu    = models.IntegerField()
    memory_GiB     = models.FloatField()
    storage_GiB    = models.FloatField()

    def __unicode__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Hardware'




class OperatingSystem(models.Model):

    name           = models.CharField(max_length=100)
    type           = models.CharField(max_length=100)
    price_per_hour = models.FloatField()

    def __unicode__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Operating system'




class Software(models.Model):

    name           = models.CharField(max_length=100)
    supported_os   = models.ManyToManyField(OperatingSystem,related_name='software_supported_os')
    price_per_hour = models.FloatField()
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Available software'




class LaunchedSoftware(models.Model):

    software      = models.ForeignKey(Software,related_name='launched_software')
    launched_date = models.DateTimeField()

    def __unicode__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Launched software'




class InstallScript(models.Model):

    name             = models.CharField(max_length=100)
    operating_system = models.ForeignKey(OperatingSystem,related_name='install_script_os')    
    software         = models.ForeignKey(Software,related_name='install_script_software')    

    def __unicode__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Install script'




class UninstallScript(models.Model):

    name             = models.CharField(max_length=100)
    operating_system = models.ForeignKey(OperatingSystem,related_name='uninstall_script_os')    
    software         = models.ForeignKey(Software,related_name='uninstall_script_software')    

    def __unicode__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Uninstall script'




class Workspace(models.Model):
    
    name             = models.CharField(max_length=100)
    company          = models.ForeignKey(Company,related_name='workspace_owner')
    hardware         = models.ForeignKey(Hardware,related_name='workspace_hardware')    
    operating_system = models.ForeignKey(OperatingSystem,related_name='workspace_os')
    software         = models.ManyToManyField(LaunchedSoftware,
                                              related_name='workspace_software',blank=True)    
    region           = models.CharField(max_length=100)
    instance_id      = models.CharField(max_length=100)
    launch_date      = models.DateTimeField() 
    
    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'Workspace'




class Storage(models.Model):

    workspace      = models.ForeignKey(Workspace,related_name='storage_workspace')
    type           = models.CharField(max_length=100)
    price_per_hour = models.FloatField()
    capacity_GiB   = models.FloatField()  
    launch_date    = models.DateTimeField() 

    def __unicode__(self):
        return self.type
    
    class Meta:
        verbose_name = 'Storage'




class Project(models.Model):
    
    company  = models.ForeignKey(Company,related_name='project_owner', null=True, blank=True)  
    customer = models.ForeignKey(AbqUser,related_name='project_customer',null=True, blank=True)  
    name     = models.CharField(max_length=100)
    email    = models.EmailField()

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'Project'
