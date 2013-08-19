from django.conf import settings # for backend ...


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



# select a region for the aws
def get_aws_region():
    # this needs to be changed
    supported_region_list = ['us-east-1', 
                             'us-west-1'] 

    # for now just west
    return supported_region_list[1]
