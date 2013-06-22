from django.db import models
from django.contrib.auth.models import User
from abq.models import AbqUser



user = User(username='dave@abaqual.com', password='123', first_name='Dave', last_name='Corson')
user.email = user.username
user.save()
abquser = AbqUser(user=user,abaqual_status='EX')
abquser.save();


user = User(username='sanjeeb@abaqual.com', password='123', first_name='Sanjeeb', last_name='Bose')
user.email = user.username
user.save()
abquser = AbqUser(user=user,abaqual_status='EX')
abquser.save();

user = User(username='raj@abaqual.com', password='123', first_name='Raj', last_name='Gupta')
user.email = user.username
user.save()
abquser = AbqUser(user=user,abaqual_status='PR')
abquser.save();

user = User(username='vijay@abaqual.com', password='123', first_name='Vijay', last_name='Sellapon')
user.email = user.username
user.save()
abquser = AbqUser(user=user,abaqual_status='PR')
abquser.save();

user = User(username='parviz@abaqual.com', password='123', first_name='Parviz', last_name='Moin')
user.email = user.username
user.save()
abquser = AbqUser(user=user,abaqual_status='CU')
abquser.save();

user = User(username='frank@abaqual.com', password='123', first_name='Frank', last_name='Ham')
user.email = user.username
user.save()
abquser = AbqUser(user=user,abaqual_status='CU')
abquser.save();
