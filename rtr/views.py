from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

content_type = ContentType.objects.get(app_label='rtr',model="Session")
permissionCreater = Permission.objects.create(codename='started_sesssion',
    name='Started Session',content_type=content_type)


def creater_check(user):
    return user.has_perm("started_session")

def index(request):
    return render(request, 'rtr/index.html')

@login_required()
@user_passes_test(creater_check)
def profsettings(request):
    return render(request, 'rtr/prof_settings.html')

def login(request):
    username = request.POST['username']
    password = request.POST['password']
    session = request.POST['session']
    typeSession = request.POST['type_session']
    typeLogin = request.POST['optionLogin']
    if typeSession=="create":
        user = authenticate(username=username, password=password)
        if user is not None:
            user.user_permissions.add(permissionCreater)
            return HttpResponseRedirect(reverse("rtr:profsettings"))
        else:
            return render(request, 'rtr/index.html', {"errorMessage": "Incorrect Username and/or Password"})
    else:
        #Todo:
        user = authenticate(username="anon", password="anon")
        user.role = "joiner"
        return render(request, 'rtr/index.html')
