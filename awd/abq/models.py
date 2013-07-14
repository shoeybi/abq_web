from django.db                     import models
from django.contrib.auth.models    import User



class AbqUser(models.Model):
    """ Abaqual users class 

    Abaqual user is a user with a status and a key for activation. 
    Status can be Expert, Professional, or Customer.
    
    """

    ABAQUAL_STATUS = (
        ('EX', 'Expert'),
        ('PR', 'Professional'),
        ('CU', 'Customer'),
        )
    user           = models.OneToOneField(User)
    abaqual_status = models.CharField(max_length=2,
                                      choices=ABAQUAL_STATUS)
    activation_key = models.CharField(max_length=40)
    key_expiration = models.DateTimeField()

    def __unicode__(self):
        return self.user.username

    class Meta:
        verbose_name = 'Abaqual user'



class Company(models.Model):
    """ Abaqual companies class
    
    A company has a unique name, an owner, and a launch date. It can also 
    have multiple employees 

    """
    
    name        = models.CharField(max_length=100)
    owner       = models.ForeignKey(AbqUser,related_name='company_owner')
    employee    = models.ManyToManyField(AbqUser,
                                         related_name='company_employee',
                                         through='Employment', blank=True)
    launch_date = models.DateTimeField()
        
    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'Company'




class Employment(models.Model):

    employee       = models.ForeignKey(AbqUser)
    company        = models.ForeignKey(Company)
    start_date     = models.DateTimeField(blank=True, null=True)
    end_date       = models.DateTimeField(blank=True, null=True)
    activation_key = models.CharField(max_length=40)
    key_expiration = models.DateTimeField()

    def __unicode__(self):
        return self.employee.user.email+' at '+self.company.name

    class Meta:
        verbose_name = 'Employment'




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



        
class OS(models.Model):

    name           = models.CharField(max_length=100)
    type           = models.CharField(max_length=100)
    price_per_hour = models.FloatField()
    hardware       = models.ManyToManyField(Hardware,related_name='os_hardware') 


    def __unicode__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Operating system'





class Software(models.Model):

    name           = models.CharField(max_length=100)
    supported_os   = models.ManyToManyField(OS,related_name='software_supported_os')
    price_per_hour = models.FloatField()
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Available software'




class InstallScript(models.Model):

    name     = models.CharField(max_length=100)
    os       = models.ForeignKey(OS,related_name='install_script_os')    
    software = models.ForeignKey(Software,related_name='install_script_software')    

    def __unicode__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Install script'




class UninstallScript(models.Model):

    name     = models.CharField(max_length=100)
    os       = models.ForeignKey(OS,related_name='uninstall_script_os')    
    software = models.ForeignKey(Software,related_name='uninstall_script_software')    

    def __unicode__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Uninstall script'




class Workspace(models.Model):
    
    name         = models.CharField(max_length=100)
    company      = models.ForeignKey(Company,related_name='workspace_owner')
    hardware     = models.ForeignKey(Hardware,related_name='workspace_hardware')    
    os           = models.ForeignKey(OS,related_name='workspace_os')
    region       = models.CharField(max_length=100)
    instance_id  = models.CharField(max_length=100)
    launch_date  = models.DateTimeField() 
    
    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'Workspace'




class LaunchedSoftware(models.Model):

    software      = models.ForeignKey(Software,related_name='launched_software')
    workspace     = models.ForeignKey(Workspace,related_name='launched_software_workspace')
    launched_date = models.DateTimeField()

    def __unicode__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Launched software'




class Storage(models.Model):

    name             = models.CharField(max_length=100)
    type             = models.CharField(max_length=100)
    price_per_hour   = models.FloatField()
    max_capacity_GiB = models.FloatField()  
    
    def __unicode__(self):
        return self.type
    
    class Meta:
        verbose_name = 'Storage'




class LaunchdStorage(models.Model):

    storage      = models.ForeignKey(Storage,related_name='launched_storage')
    workspace    = models.ForeignKey(Workspace,related_name='storage_workspace')
    capacity_GiB = models.FloatField()  
    launch_date  = models.DateTimeField() 

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
