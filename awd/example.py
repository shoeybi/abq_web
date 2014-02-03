from django.db import models
from django.contrib.auth.models import User
from abq.models import AbqUser, Company, Hardware, OS, Software
from abq.models import InstallScript, Workspace, Project, Region
import datetime
from django.utils import timezone


# ===================
# add users
# ===================

user = User(username='jo@jo.com', password="jo", first_name='Jo', last_name='Jo')
user.email = user.username
user.is_active = True
user.save()
abquser = AbqUser(user=user,abaqual_status='EX')
abquser.activation_key = 'abc'
abquser.key_expiration = timezone.now()
abquser.save();

user = User(username='dave@abaqual.com', password='123', first_name='Dave', last_name='Corson')
user.email = 'shoeybim@gmail.com'
user.is_active = True
user.save()
abquser = AbqUser(user=user,abaqual_status='EX')
abquser.activation_key = 'abc'
abquser.key_expiration = timezone.now()
abquser.save();

user = User(username='sanjeeb@abaqual.com', password='123', first_name='Sanjeeb', last_name='Bose')
user.email = 'shoeybim@gmail.com'
user.is_active = True
user.save()
abquser = AbqUser(user=user,abaqual_status='EX')
abquser.activation_key = 'abc'
abquser.key_expiration = timezone.now()
abquser.save();

user = User(username='raj@abaqual.com', password='123', first_name='Raj', last_name='Gupta')
user.email = 'shoeybim@gmail.com'
user.is_active = True
user.save()
abquser = AbqUser(user=user,abaqual_status='PR')
abquser.activation_key = 'abc'
abquser.key_expiration = timezone.now()
abquser.save();

user = User(username='vijay@abaqual.com', password='123', first_name='Vijay', last_name='Sellapon')
user.email = 'shoeybim@gmail.com'
user.is_active = True
user.save()
abquser = AbqUser(user=user,abaqual_status='PR')
abquser.activation_key = 'abc'
abquser.key_expiration = timezone.now()
abquser.save();

user = User(username='parviz@abaqual.com', password='123', first_name='Parviz', last_name='Moin')
user.email = 'shoeybim@gmail.com'
user.is_active = True
user.save()
abquser = AbqUser(user=user,abaqual_status='CU')
abquser.activation_key = 'abc'
abquser.key_expiration = timezone.now()
abquser.save();

user = User(username='frank@abaqual.com', password='123', first_name='Frank', last_name='Ham')
user.email = 'shoeybim@gmail.com'
user.is_active = True
user.save()
abquser = AbqUser(user=user,abaqual_status='CU')
abquser.activation_key = 'abc'
abquser.key_expiration = timezone.now()
abquser.save();



# ==============
# add hardware
# ==============

hardware1                = Hardware()
hardware1.name           = 'EC2 micro instance'
hardware1.key            = 't1.micro'
hardware1.price_per_hour = 0.02
hardware1.virtual_cpu    = 1
hardware1.memory_GiB     = 0.615
hardware1.storage_GiB    = 8.
hardware1.save()

hardware2                = Hardware()
hardware2.name           = 'EC2 small instance'
hardware2.key            = 'm1.small'
hardware2.price_per_hour = 0.06
hardware2.virtual_cpu    = 1
hardware2.memory_GiB     = 1.7
hardware2.storage_GiB    = 160.
hardware2.save()

hardware3                = Hardware()
hardware3.name           = 'EC2 medium instance'
hardware3.key            = 'm1.medium'
hardware3.price_per_hour = 0.12
hardware3.virtual_cpu    = 1
hardware3.memory_GiB     = 3.75
hardware3.storage_GiB    = 410.
hardware3.save()

hardware4                = Hardware()
hardware4.name           = 'EC2 large instance'
hardware4.key            = 'm1.large'
hardware4.price_per_hour = 0.24
hardware4.virtual_cpu    = 2
hardware4.memory_GiB     = 7.5
hardware4.storage_GiB    = 840.
hardware4.save()


# ===================
# operating system
# ===================

osU                = OS()
osU.name           = 'Ubuntu 12.04 LTS'
osU.key            = 'ubuntu12.04'
osU.price_per_hour = 0.0
osU.save()
osU.hardware.add(hardware1, hardware2, hardware3, hardware4)

osC                = OS()
osC.name           = 'CentOs 6.0'
osC.key            = 'centos6.0'
osC.price_per_hour = 0.0
osC.save()
osC.hardware.add(hardware3,hardware4)


# ===================
# software
# ===================

openFoam = Software()
openFoam.name = 'OpenFoam'
openFoam.version = '2.2.2'
openFoam.description = 'This is a general purpose CFD solver that works with unstructured meshes'
openFoam.software_url = 'http://www.openfoam.com/'
openFoam.comparable = 'Ansys fluent, StarCD, CFD++'
openFoam.category = 'CFD, solver, engineering'
openFoam.price_per_hour = 0.0
openFoam.save()
openFoam.supported_os.add(osU,osC)

octave = Software()
octave.name = 'QToctave'
octave.version = '3.8.0'
octave.description = 'Qtoctave is a mathematical, MATLAB like software'
octave.software_url = 'https://www.gnu.org/software/octave/'
octave.comparable = 'MATLAB'
octave.category = 'analysis, engineering'
octave.price_per_hour = 0.0
octave.save()
octave.supported_os.add(osU)

gimp = Software()
gimp.name = 'Gimp'
gimp.version = '2.8'
gimp.description = 'GIMP is the GNU Image Manipulation Program'
gimp.software_url = 'http://www.gimp.org/'
gimp.comparable = 'Adobe Photoshop'
gimp.category = 'photo retouching, image composition, and image authoring'
gimp.price_per_hour = 0.0
gimp.save()
gimp.supported_os.add(osU)


# =============================
# install and uninstall scripts
# =============================

insScr = InstallScript()
insScr.name = 'OpenFoam_2.2.2_Ubuntu'
insScr.os = osU
insScr.software = openFoam
insScr.save()

insScr = InstallScript()
insScr.name = 'OpenFoam_2.2.2_Centos'
insScr.os = osC
insScr.software = openFoam
insScr.save()

insScr = InstallScript()
insScr.name = 'Qtoctave_3.8.0_Ubuntu'
insScr.os = osU
insScr.software = octave
insScr.save()


insScr = InstallScript()
insScr.name = 'Gimp_2.8_Ubuntu'
insScr.os = osU
insScr.software = gimp
insScr.save()



# ==========
# regions
# ==========

region = Region()
region.name = 'us-west-1'
region.save()

region = Region()
region.name = 'us-west-2'
region.save()

region = Region()
region.name = 'us-east-1'
region.save()
'''
region = Region()
region.name = 'eu-west-1'
region.save()

region = Region()
region.name = 'ap-southeast-1'
region.save()

region = Region()
region.name = 'ap-southeast-2'
region.save()

region = Region()
region.name = 'ap-northeast-1'
region.save()

region = Region()
region.name = 'sa-east-1'
region.save()
'''
