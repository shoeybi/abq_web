from django.conf import settings # for backend ...
from django.contrib.auth.models import User
from abq.models import Region, Company, Workspace
import re


def get_image_filename_for_workspace(company, workspace):

    # company name is unique but the workspace name inside 
    # a company is not, so we need to append numbers for
    # the ones that there is a conflict
    # first get a list of all the worksapces in the company 
    # with the same name
    ws_set = Workspace.objects.filter(
        company=company, 
        name=workspace.name)
    # NOTE: the new workspace is not saved into database
    # so uniqueness means that the list is empty
    index = len(ws_set)
    # unique name
    image_filename  = 'workspaceImage__' + company.name + \
                '__' + workspace.name + '__' + str(index) + '.png'
    # make the filenames safe
    for c in r'[] /\;,><&*:%=+@!#^()|?^':
        image_filename = image_filename.replace(c,'_')
    # return the filename
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
