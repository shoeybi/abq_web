from django.conf import settings # for backend ...
from django.contrib.auth.models import User
from abq.models import Region, Company, Workspace
import re, glob



def clean_filename(filename):

    for c in r'[] /\;,><&*:%=+@!#^()|?^':
        filename = filename.replace(c,'_')
    return filename



def get_image_filename_for_workspace(company, workspace):

    # company name is unique but the workspace name inside 
    # a company is not, so we need to append numbers for
    # the ones that there is a conflict
    # first get the list if existing files
    prefix = 'workspaceImage__' + company.name + \
                '__' + workspace.name + '__'
    prefix = clean_filename(prefix)
    prefix = settings.MEDIA_ROOT + 'workspace_images/' + prefix
    file_list = glob.glob(prefix+'*.png')
    # now get the maximum index
    max_index = 0
    if len(file_list) > 0:
        indecies = []
        for name in file_list:
            name = name.replace(prefix,'')
            name = name.replace('.png','')
            indecies.append(int(name))
        max_index = max(indecies)
    # build the filename
    image_filename  = prefix + str(max_index+1) + '.png'
    return image_filename



def get_pretty_username(username):
    """ build a user friendly username based on first and last name """
    
    # first get the user 
    user = User.objects.get(username=username)
    if user == None:
        raise Exception("could not find the user")
    # get all the users that have the same last name 
    # as the passed user
    user_list = User.objects.filter(
        last_name=user.last_name, 
        first_name__startswith=user.first_name[0]
        ).order_by('date_joined')
    # make sure we at least have one user matching
    if len(user_list) <1:
        raise Exception('problem with query, could not find the user')
    # now if we have multiple pretty usernames, name them 
    # base on their order in the list. Note that we will not delete
    # users rather we will make them inactive, technically we should not 
    # have any issue if a person leaves Abaqual
    index = 0
    for i in range(len(user_list)):
        if user == user_list[i]:
            index = i+1
            break
    # we should have set index
    if index == 0:
        raise Exception('index is not set')
    elif index == 1:
        return (user.first_name[0]+user.last_name).lower()
    else:
        return (user.first_name[0]+user.last_name).lower() + str(index)



# the following code is adopted from Django code snippets, see
# http://djangosnippets.org/snippets/1547/
def login_user_no_credentials(request, user):
    """
    Log in a user without requiring credentials (using ``login`` from
    ``django.contrib.auth``, first finding a matching backend).
    
    """
    from django.contrib.auth import load_backend, login
    if not hasattr(user, 'backend'):
        for backend in settings.AUTHENTICATION_BACKENDS:
            if user == load_backend(backend).get_user(user.pk):
                user.backend = backend
                break
    if hasattr(user, 'backend'):
        return login(request, user)


    
def get_aws_available_regions():
    """ Get regions list 
    pass regions so company unique key is copied 
    in all the available regions
    """

    if settings.AWS:
        regions2 = Region.objects.all()
        regions = []
        for region in regions2:
            regions.append(region.name)
    else:
        regions = ['west']
    return regions



# select a region for the aws
def get_aws_region():
    # this needs to be changed
    supported_region_list = ['us-east-1', 
                             'us-west-1'] 

    # for now just west
    return supported_region_list[1]
