from django.db                     import models
from django.contrib.auth.models    import User
from django.core.files             import File
from PIL                           import Image

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


class Region(models.Model):

    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'Region'


class Employment(models.Model):

    employee       = models.ForeignKey(AbqUser)
    company        = models.ForeignKey(Company)
    start_date     = models.DateTimeField(blank=True, null=True)
    end_date       = models.DateTimeField(blank=True, null=True)
    activation_key = models.CharField(max_length=40)
    key_expiration = models.DateTimeField()

    def __unicode__(self):
        return self.employee.user.username+' at '+self.company.name

    class Meta:
        verbose_name = 'Employment'




class Hardware(models.Model):

    name           = models.CharField(max_length=100)
    key            = models.CharField(max_length=100)
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
    key            = models.CharField(max_length=100)
    price_per_hour = models.FloatField()
    hardware       = models.ManyToManyField(Hardware,related_name='os_hardware') 


    def __unicode__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Operating system'




class Software(models.Model):

    name           = models.CharField(max_length=100)
    version        = models.CharField(max_length=50)
    description    = models.CharField(max_length=200)
    software_url   = models.URLField(max_length=200,default='#')
    comparable     = models.CharField(max_length=200)
    category       = models.CharField(max_length=100)
    price_per_hour = models.FloatField()
    supported_os   = models.ManyToManyField(OS,related_name='software_supported_os')
       
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



class Workspace(models.Model):
    
    WORKSPACE_STATUS = (
        ('NL', 'Not launched'),
        ('SU', 'Starting up'),
        ('RN', 'Running'),
        ('PA', 'Paused'),
        ('ST', 'Stopping'),
        ('TR', 'Terminated'),
        )
    status       = models.CharField(max_length=2,
                                    choices=WORKSPACE_STATUS,
                                    default='NL')
    name         = models.CharField(max_length=100)
    company      = models.ForeignKey(Company,related_name='workspace_owner')
    hardware     = models.ForeignKey(Hardware,related_name='workspace_hardware')    
    os           = models.ForeignKey(OS,related_name='workspace_os')
    region       = models.CharField(max_length=100)
    instance_id  = models.CharField(max_length=100)
    launch_date  = models.DateTimeField()
    image        = models.ImageField(upload_to='workspace_images')
    instance_url = models.URLField(max_length=200,default='#')
    software     = models.ManyToManyField(Software,
                                         related_name='workspace_software',
                                         through='SoftwareLaunch', blank=True)
    
    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'Workspace'

    def set_size_and_save_image(self,target_filename,original_filename):
        self.image.save(target_filename,File(open(original_filename, 'r')))
        image = Image.open(self.image)
        # hardcode the size
        size = ( 160, 90)
        image = image.resize(size, Image.ANTIALIAS)
        image.save(self.image.path)           

    def delete(self, *args, **kwargs):
        self.image.delete()
        super(Workspace, self).delete(*args, **kwargs)


class SoftwareLaunch(models.Model):

    software      = models.ForeignKey(Software)
    workspace     = models.ForeignKey(Workspace)
    launched_date = models.DateTimeField()
    installed     = models.BooleanField(default=False)

    def __unicode__(self):
        return self.software.name+' at '+self.workspace.name
    
    class Meta:
        verbose_name = 'Software launch'



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
    
    company  = models.ForeignKey(Company,
                                 related_name='project_owner', 
                                 null=True, blank=True)  
    customer = models.ForeignKey(AbqUser,
                                 related_name='project_customer',
                                 null=True, blank=True)  
    name     = models.CharField(max_length=100)
    email    = models.EmailField()

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'Project'
