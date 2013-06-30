from django.contrib import admin
from abq.models import AbqUser, Company, Workspace, Project

admin.site.register(AbqUser)
admin.site.register(Company)
admin.site.register(Workspace)
admin.site.register(Project)
