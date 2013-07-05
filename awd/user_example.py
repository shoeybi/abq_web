from django.db import models
from django.contrib.auth.models import User
from abq.models import AbqUser, Hardware, OperatingSystem
import datetime
from django.utils import timezone

user = User(username='dave@abaqual.com', password='123', first_name='Dave', last_name='Corson')
User.email = user.username
user.is_active = True
user.save()
abquser = AbqUser(user=user,abaqual_status='EX')
abquser.activation_key = 'abc'
abquser.key_expiration = timezone.now()
abquser.save();

user = User(username='sanjeeb@abaqual.com', password='123', first_name='Sanjeeb', last_name='Bose')
user.email = user.username
user.is_active = True
user.save()
abquser = AbqUser(user=user,abaqual_status='EX')
abquser.activation_key = 'abc'
abquser.key_expiration = timezone.now()
abquser.save();

user = User(username='raj@abaqual.com', password='123', first_name='Raj', last_name='Gupta')
user.email = user.username
user.is_active = True
user.save()
abquser = AbqUser(user=user,abaqual_status='PR')
abquser.activation_key = 'abc'
abquser.key_expiration = timezone.now()
abquser.save();

user = User(username='vijay@abaqual.com', password='123', first_name='Vijay', last_name='Sellapon')
user.email = user.username
user.is_active = True
user.save()
abquser = AbqUser(user=user,abaqual_status='PR')
abquser.activation_key = 'abc'
abquser.key_expiration = timezone.now()
abquser.save();

user = User(username='parviz@abaqual.com', password='123', first_name='Parviz', last_name='Moin')
user.email = user.username
user.is_active = True
user.save()
abquser = AbqUser(user=user,abaqual_status='CU')
abquser.activation_key = 'abc'
abquser.key_expiration = timezone.now()
abquser.save();

user = User(username='frank@abaqual.com', password='123', first_name='Frank', last_name='Ham')
user.email = user.username
user.is_active = True
user.save()
abquser = AbqUser(user=user,abaqual_status='CU')
abquser.activation_key = 'abc'
abquser.key_expiration = timezone.now()
abquser.save();


hardware                = Hardware()
hardware.name           = 'EC2 micro instance'
hardware.type           = 't1.micro'
hardware.price_per_hour = 0.02
hardware.virtual_cpu    = 1
hardware.memory_GiB     = 0.615
hardware.storage_GiB    = 8.
hardware.save()

hardware                = Hardware()
hardware.name           = 'EC2 small instance'
hardware.type           = 'm1.small'
hardware.price_per_hour = 0.06
hardware.virtual_cpu    = 1
hardware.memory_GiB     = 1.7
hardware.storage_GiB    = 160.
hardware.save()

hardware                = Hardware()
hardware.name           = 'EC2 medium instance'
hardware.type           = 'm1.medium'
hardware.price_per_hour = 0.12
hardware.virtual_cpu    = 1
hardware.memory_GiB     = 3.75
hardware.storage_GiB    = 410.
hardware.save()

hardware                = Hardware()
hardware.name           = 'EC2 large instance'
hardware.type           = 'm1.large'
hardware.price_per_hour = 0.24
hardware.virtual_cpu    = 2
hardware.memory_GiB     = 7.5
hardware.storage_GiB    = 840.
hardware.save()


os                = OperatingSystem()
os.name           = 'Ubuntu 12.04 LTS'
os.type           = 'ami-d0f89fb9'
os.price_per_hour = 0.0
os.save()

os                = OperatingSystem()
os.name           = 'CentOs 6.0'
os.type           = 'ami-03559b6a'
os.price_per_hour = 0.0
os.save()
