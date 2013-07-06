from django.contrib import admin
from abq.models import AbqUser, Company, Hardware, OS, Software, \
    InstallScript, UninstallScript, Workspace, Project, LaunchedSoftware

admin.site.register(AbqUser)
admin.site.register(Company)
admin.site.register(Hardware)
admin.site.register(OS)
admin.site.register(Software)
admin.site.register(LaunchedSoftware)
admin.site.register(InstallScript)
admin.site.register(UninstallScript)
admin.site.register(Workspace)
admin.site.register(Project)
