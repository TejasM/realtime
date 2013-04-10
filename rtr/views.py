from __future__ import division
from collections import defaultdict
from datetime import timedelta, datetime
from functools import wraps
import json
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from django.utils.safestring import mark_safe

import pytz
from mysite import settings

from rtr.models import Session, Series, Stats, Question, Stat


def index(request):
    if request.session.get('type') is not None:
        if request.session.get('type') == 'creater':
            return HttpResponseRedirect('profDisplay')
        elif request.session.get('type') == 'joiner':
            return redirect(reverse('rtr:audience_display'))
    return render(request, 'rtr/index.html')


def error(request):
    request.session.clear()
    return redirect(reverse('rtr:index'))


def end_session(request):
    if request.session.get('type') == 'creater':
        series = Session.objects.get(pk=int(request.session['session'])).series
        series.live = False
        series.save()
    elif request.session.get('type') == 'joiner':
        session = Session.objects.get(pk=int(request.session['session']))
        session.cur_num -= 1
        session.save()
        statids = request.session.get('statids')
        if statids[-1] == ',':
            statids = statids[:len(statids) - 1]
        statids = statids.split(',')
        for stat_key in statids:
            stats = Stats.objects.get(pk=stat_key)
            stats.live = False
            stats.save()

    logout(request)
    request.session.clear()
    return redirect(reverse('rtr:index'))


def audience_display(request):
    if request.session.get('session') is not None:
        statids = request.session.get('statids')
        if statids[-1] == ',':
            statids = statids[:len(statids) - 1]
        statids = statids.split(',')
        labels = []
        for ids in statids:
            labels.append((str(Stats.objects.get(pk=int(ids)).name)))
        return render(request, 'rtr/audience_view.html',
                      dict(labels=labels, async_url=settings.ASYNC_BACKEND_URL))
    else:
        return redirect(request, 'rtr/index.html')


def check_session(f):
    @wraps(f)
    def wrapper(request, *args, **kwds):
        session = Session.objects.get(pk=request.session.get('session'))
        if session.series.live:
            return f(request, *args, **kwds)
        else:
            messages.error(request, "Session has now ended")
            request.session.clear()
            raise Exception("Session has ended")

    return wrapper


@check_session
def ask_question(request):
    Question.objects.create(question=request.POST['question'],
                            session=Session.objects.get(pk=request.session.get('session')),
                            time_asked=timezone.now())
    return redirect(reverse('rtr:audience_display'))


@check_session
def updateStats(request):
    statids = request.session.get('statids')
    if statids[-1] == ',':
        statids = statids[:len(statids) - 1]
    statids = statids.split(',')
    for i, stats in enumerate(statids):
        Stat.objects.create(change=int(request.POST['value' + str(i)]),
                            old_value=int(request.POST['oldvalue' + str(i)]), stats=Stats.objects.get(pk=stats))
    return redirect(reverse('rtr:audience_display'))


def calculate_stats(stats_per_user, num_of_users):
    result = 0
    if stats_per_user:
        for user_stat in stats_per_user:
            if user_stat.live:
                changes_by_user = Stat.objects.filter(stats=user_stat).order_by("timestamp").reverse()
                total_user_change = 0
                changes_by_user = [change for change in changes_by_user]
                changes_by_user = changes_by_user[:3]
                alpha = 2 / (len(changes_by_user) + 1)
                for i, single_stat in enumerate(changes_by_user):
                    if single_stat.change != 0:
                        total_user_change += pow((1 - alpha), i) * single_stat.change
                result += (1 / num_of_users) * total_user_change * 25
    return result


@login_required()
def get_stats(request):
    if request.session.get('type') == 'creater':
        session = Session.objects.get(pk=request.session.get('session'))
        stats = session.stats_on.split(",")
        percentages = []
        for stat_on in stats:
            stats_per_user = Stats.objects.filter(session=request.session.get('session'), name=stat_on)
            percentages.append(str(calculate_stats(stats_per_user)))
        data = [{'percentages': percentages}]
        return HttpResponse(json.dumps(data), content_type='application/json')
    else:
        return redirect(request, 'rtr/index.html')


@login_required()
def get_all(request):
    if request.session.get('type') == 'creater':
        #Why are we getting stat object
        session = Session.objects.get(pk=request.session.get('session'))
        stats = session.stats_on.split(",")
        percentages = []
        for stat_on in stats:
            stats_per_user = Stats.objects.filter(session=request.session.get('session'), name=stat_on)
            percentages.append(str(max(0, min(round(50 + calculate_stats(stats_per_user, session.cur_num), 1), 100))))
        data = [{'percentages': percentages, 'count': session.cur_num}]
        return HttpResponse(json.dumps(data), content_type='application/json')
    else:
        return redirect(request, 'rtr/index.html')


@login_required()
def get_questions(request):
    if request.session.get('type') == 'creater':
        questions = Question.objects.filter(session=request.session.get('session'))
        data = serializers.serialize('json', questions)
        return HttpResponse(data, mimetype='application/json')
    else:
        return redirect(request, 'rtr/index.html')


@login_required()
def prof_display(request):
    if request.session.get('type') == 'creater':
        session = Session.objects.get(pk=request.session.get('session'))
        if session.stats_on is ("" or None):
            return redirect(reverse("rtr:prof_settings"))
        stats_on = session.stats_on
        if stats_on[-1] == ',':
            stats_on = stats_on[0:len(stats_on) - 1]
        stats_on = stats_on.split(",")
        context = {}
        labels = []
        for i, stat in enumerate(stats_on):
            labels.append(stat.title())
        context['labels'] = labels
        context['async_url'] = settings.ASYNC_BACKEND_URL
        context['session'] = request.session.get('session')
        return render(request, 'rtr/prof_data.html', context)
    else:
        return redirect(request, 'rtr/index.html')


@login_required()
def prof_start_display(request):
    session = Session.objects.get(pk=request.session.get('session'))
    try:
        _ = request.POST['understanding_toggle']
        if not 'Understanding' in session.stats_on:
            session.stats_on += 'Understanding,'
    except Exception as _:
        pass
    try:
        _ = request.POST['interest_toggle']
        if not 'Interest' in session.stats_on:
            session.stats_on += 'Interest,'
    except Exception as _:
        pass
    if not 'Understanding' in session.stats_on and not 'Interest' in session.stats_on:
        return redirect(reverse("rtr:prof_settings"), {"error_message": "Select at least one of the stats"})
    if session.stats_on[-1] == ",":
        session.stats_on = session.stats_on[:len(session.stats_on) - 1]
    session.save()
    return HttpResponseRedirect('/rtr/profDisplay')


@login_required()
def prof_settings(request):
    if request.session.get('type') == 'creater':
        return render(request, 'rtr/prof_settings.html')
    else:
        return redirect(request, 'rtr/index.html')


def loginUser(request):
    #Collect post data
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    session = request.POST.get('session', '')
    typeSession = request.POST.get('type_session', '')
    typeLogin = request.POST.get('optionLogin', '')

    #Validate Post Data
    if session == '':
        messages.error(request, "Need to specify session id")

    user = None
    if typeLogin == 'registered' or (typeSession == "create" or typeSession == "view"):
        if username == '' or password == '':
            messages.error(request, "Need both password and username for registered login")
            return redirect(reverse('rtr:index'))
        #Check user authentication if required:
        else:
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
            else:
                messages.error(request, "Incorrect Username and/or Password")
                return redirect(reverse('rtr:index'))

    #Redirect to where asked
    if typeSession == "create":
        try:
            series = Series.objects.get(series_id=session, live=False)
            series.live = True
            series.save()
            newSession = Session.objects.create(series=series, create_time=timezone.now(), stats_on="", user=user)
        except Series.DoesNotExist:
            try:
                Series.objects.get(series_id=session)
                messages.error(request, "Session already in progress")
                logout(request)
                return redirect(reverse('rtr:index'))
            except Series.DoesNotExist:
                newSeries = Series.objects.create(series_id=session, live=True)
                newSession = Session.objects.create(
                    series=newSeries, create_time=timezone.now(), stats_on="", user=user)
        request.session['session'] = str(newSession.id)
        request.session['session_name'] = session
        request.session['type'] = 'creater'
        return redirect(reverse("rtr:prof_settings"))

    elif typeSession == "join":
        try:
            series = Series.objects.get(series_id=session, live=True)
            session_name = session
            session = Session.objects.filter(series_id=series).latest('create_time')
            session.cur_num += 1
            if session.cur_num > session.max_num:
                session.max_num = session.cur_num
            session.save()
            stats = session.stats_on.split(",")
            stat_ids = ""
            for stat in stats:
                newStats = Stats.objects.create(session=session, name=stat)
                stat_ids += str(newStats.id) + ","
            request.session['session_name'] = session_name
            request.session['session'] = str(session.id)
            request.session['type'] = 'joiner'
            request.session['statids'] = stat_ids
            user = authenticate(username="tejas", password="tejas")
            if user is not None:
                login(request, user)
            return redirect(reverse('rtr:audience_display'))
        except Series.DoesNotExist:
            messages.error(request, "Incorrect session, not currently running")
            if user is not None:
                logout(request)
            return redirect(reverse('rtr:index'))

    elif typeSession == 'view':
        try:
            try:
                series = Series.objects.get(series_id=session)
            except Series.DoesNotExist:
                messages.error(request, "No Such Session")
                return redirect(reverse('rtr:index'))
            request.session['session'] = str(session)
            return HttpResponseRedirect('/rtr/viewSeries/' + str(series.id))
        except Series.DoesNotExist:
            messages.error(request, "Incorrect session, not currently running")
            logout(request)
            return redirect(reverse('rtr:index'))
    else:
        messages.error(request, "Something Very Wrong Happened")
        if user is not None:
            logout(request)
        return redirect(reverse('rtr:index'))


@login_required()
def view_series(request, series_id):
    try:
        sessions = Session.objects.filter(series_id=Series.objects.get(pk=series_id))
        return render(request, 'rtr/view_series.html', {"Sessions": sessions})
    except Series.DoesNotExist:
        return redirect(reverse('rtr:index'))


@login_required()
def view_session(request, session_id, location):
    try:
        session = Session.objects.get(pk=session_id)
        if not session.user == request.user:
            messages.error(request, "You did not create that session")
            return HttpResponseRedirect('/rtr/viewSeries/' + str(session.series.id))
        stats = Stats.objects.filter(session=session)
        context = {}
        changes = []
        groups_of_stats = defaultdict(list)
        for stat in stats:
            groups_of_stats[stat.name].append(stat)

        for key, value in groups_of_stats.iteritems():
            groups_of_stats[key] = group_stats(value)
        location = location.replace("1", "/")
        zone = pytz.timezone(str(location))
        for label, stat in groups_of_stats.iteritems():
            total_change = all_changes(stat, label, zone)
            if total_change:
                changes.append(total_change)
        context['changes'] = changes
        request.session['session'] = str(session.series.series_id + " : " +
                                         session.create_time.strftime("%A %d, %B %Y"))
        return render(request, 'rtr/view_session.html', context)
    except Session.DoesNotExist:
        return redirect(reverse('rtr:index'))


def group_stats(stats):
    individual_changes = []
    for per_user_stat in stats:
        per_user_individual_changes = Stat.objects.filter(stats=per_user_stat)
        for change in per_user_individual_changes:
            new_stat = Stat()
            new_stat.change = change.change
            new_stat.timestamp = change.timestamp
            individual_changes.append(new_stat)
    return sorted(individual_changes, key=lambda x: x.timestamp)


def all_changes(individual_changes, label, zone):
    if individual_changes:
        end_time = (individual_changes[::-1])[0].timestamp
        init_time = individual_changes[0].timestamp
        delta = (end_time - init_time).total_seconds() / 600
        x = []
        y = []
        net_change_over_interval = 0
        index = 1
        for change in individual_changes:
            if change.timestamp - init_time - (index * timedelta(minutes=delta)) < timedelta(minutes=0):
                net_change_over_interval += change.change
            else:
                time = (init_time + (index * timedelta(minutes=delta)))
                time = time.astimezone(zone)
                x.append(str(time.strftime("%I:%M %p")))
                y.append(net_change_over_interval)
                net_change_over_interval = change.change
                index += 1

        return tuple((mark_safe(x), y, label))
    else:
        return None