from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate
from rtr.models import Session, Series
from django.utils import timezone


def index(request):
    return render(request, 'rtr/index.html')


@login_required()
def get_stats(request):
    if request.session.get('type') == 'creater':
        #Todo: create context
        return render(request, 'rtr/ProfData.html')
    else:
        return redirect(request, 'rtr/index.html')


@login_required()
def get_questions(request):
    if request.session.get('type') == 'creater':
        #Todo: create context
        return render(request, 'rtr/ProfData.html')
    else:
        return redirect(request, 'rtr/index.html')


@login_required()
def prof_display(request):
    if request.session.get('type') == 'creater':
        return render(request, 'rtr/ProfData.html')
    else:
        return redirect(request, 'rtr/index.html')


@login_required()
def prof_start_display(request):
    understanding = request.POST['understanding_toggle']
    interest = request.POST['interest_toggle']
    print understanding
    print interest
    return redirect(reverse("rtr:prof_display"))


@login_required()
def prof_settings(request):
    if request.session.get('type') == 'creater':
        return render(request, 'rtr/prof_settings.html')
    else:
        return redirect(request, 'rtr/index.html')


def login(request):
    username = request.POST['username']
    password = request.POST['password']
    session = request.POST['session']
    typeSession = request.POST['type_session']
    typeLogin = request.POST['optionLogin']
    if typeSession == "create":
        user = authenticate(username=username, password=password)
        if user is not None:
            try:
                series = Series.objects.get(series_id=session, live=False)
                series.live = True
                series.save()
                newSession = Session.objects.create(series=series, create_time=timezone.now())
            except Series.DoesNotExist:
                Series.objects.create(series_id=session)
                newSession = Session.objects.create(
                    series=Series.objects.get(series_id=session), create_time=timezone.now())
            request.session.__setitem__('session', str(newSession.id))
            request.session.__setitem__('type', 'creater')
            return HttpResponseRedirect(reverse("rtr:prof_settings"))
        else:
            return render(request, 'rtr/index.html', {"error_message": "Incorrect Username and/or Password"})
    else:
        #Todo:
        user = authenticate(username="anon", password="anon")
        user.role = "joiner"
        return render(request, 'rtr/index.html', {"error_message": "Cannot join session yet"})