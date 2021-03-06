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
osU.hardware.add(hardware2, hardware3, hardware4)

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
openFoam.version = '2.2.1'
openFoam.description = 'OpenFOAM is a free, open source Computational Fluid Dynamics software package'
openFoam.software_url = 'http://www.openfoam.com/'
openFoam.comparable = 'Ansys Fluent, StarCD, CFD++'
openFoam.category = 'CFD, solver, engineering'
openFoam.price_per_hour = 0.0
openFoam.save()
openFoam.supported_os.add(osU)

octave = Software()
octave.name = 'Octave'
octave.version = '3.2.4'
octave.description = 'Octave is a high-level interpreted language, primarily intended for numerical computations'
octave.software_url = 'https://www.gnu.org/software/octave/'
octave.comparable = 'MATLAB'
octave.category = 'analysis, engineering'
octave.price_per_hour = 0.0
octave.save()
octave.supported_os.add(osU)

gimp = Software()
gimp.name = 'Gimp'
gimp.version = '2.6'
gimp.description = 'GIMP is a freely distributed piece of software for such tasks as photo retouching, image composition and image authoring'
gimp.software_url = 'http://www.gimp.org/'
gimp.comparable = 'Adobe Photoshop'
gimp.category = 'photo retouching, image composition, and image authoring'
gimp.price_per_hour = 0.0
gimp.save()
gimp.supported_os.add(osU)


paraview = Software()
paraview.name = 'Paraview'
paraview.version = '3.12.0'
paraview.description = 'ParaView is an open-source, multi-platform data analysis and visualization application'
paraview.software_url = 'http://www.paraview.org/'
paraview.comparable = 'Tecplot, Ensight, FieldView'
paraview.category = 'visualization'
paraview.price_per_hour = 0.0
paraview.save()
paraview.supported_os.add(osU)


# =============================
# install and uninstall scripts
# =============================

insScr = InstallScript()
insScr.name = 'openfoam_2.2.1_ubuntu12.04'
insScr.os = osU
insScr.software = openFoam
insScr.save()

insScr = InstallScript()
insScr.name = 'octave_3.2.4_ubuntu12.04'
insScr.os = osU
insScr.software = octave
insScr.save()

insScr = InstallScript()
insScr.name = 'gimp_2.6_ubuntu12.04'
insScr.os = osU
insScr.software = gimp
insScr.save()


insScr = InstallScript()
insScr.name = 'paraview_3.12.0_ubuntu12.04'
insScr.os = osU
insScr.software = paraview
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
