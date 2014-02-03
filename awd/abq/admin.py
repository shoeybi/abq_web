from django.contrib import admin
from abq.models import AbqUser, Company, Hardware, OS, Software, \
    InstallScript, Workspace, Project, SoftwareLaunch, \
    Employment, Region

admin.site.register(AbqUser)
admin.site.register(Company)
admin.site.register(Region)
admin.site.register(Employment)
admin.site.register(Hardware)
admin.site.register(OS)
admin.site.register(Software)
admin.site.register(SoftwareLaunch)
admin.site.register(InstallScript)
admin.site.register(Workspace)
admin.site.register(Project)
