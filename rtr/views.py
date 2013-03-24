from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.utils import timezone, simplejson
from django.utils.safestring import mark_safe

from rtr.models import Session, Series, Stats, Question, Stat


def index(request):
    if request.session.get('type') is not None:
        if request.session.get('type') == 'creater':
            return HttpResponseRedirect('profDisplay')
    return render(request, 'rtr/index.html')


def end_session(request):
    if request.session.get('type') == 'creater':
        series = Session.objects.get(pk=int(request.session['session'])).series
        series.live = False
        series.save()
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
            labels.append((str(Stats.objects.get(pk=int(ids)).name)).lower())
        return render(request, 'rtr/audience_view.html', {'labels': labels, 'size': range(len(labels))})
    else:
        return redirect(request, 'rtr/index.html')


def ask_question(request):
    Question.objects.create(question=request.POST['question'],
                            session=Session.objects.get(pk=request.session.get('session')),
                            time_asked=timezone.now())
    return redirect(reverse('rtr:audience_display'))


def updateStats(request):
    statids = request.session.get('statids')
    if statids[-1] == ',':
        statids = statids[:len(statids) - 1]
    statids = statids.split(',')
    for i, stats in enumerate(statids):
        Stat.objects.create(change=int(request.POST['value' + str(i)]), timestamp=timezone.now(),
                            stats=Stats.objects.get(pk=stats))
    return redirect(reverse('rtr:audience_display'))


def calculate_stats(stats_per_user):
    result = 0
    if stats_per_user:
        for user_stat in stats_per_user:
            changes_by_user = Stat.objects.filter(stats=user_stat)
            total_user_change = 0
            for single_stat in changes_by_user:
                total_user_change += single_stat.change
            result += total_user_change
        result /= len(stats_per_user)
    return result


@login_required()
def get_stats(request):
    if request.session.get('type') == 'creater':
        #Why are we getting stat object
        session = Session.objects.get(pk=request.session.get('session'))
        stats = session.stats_on.split(",")
        percentages = []
        for stat_on in stats:
            stats_per_user = Stats.objects.filter(session=request.session.get('session'), name=stat_on)
            percentages.append(str(calculate_stats(stats_per_user)))
        data = [{'percentages': percentages}]
        return HttpResponse(simplejson.dumps(data), mimetype='application/json')
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
        return render(request, 'rtr/ProfData.html', context)
    else:
        return redirect(request, 'rtr/index.html')


@login_required()
def prof_start_display(request):
    session = Session.objects.get(pk=request.session.get('session'))
    try:
        _ = request.POST['understanding_toggle']
        if not session.stats_on.__contains__('Understanding'):
            session.stats_on += 'Understanding,'
    except Exception as _:
        pass
    try:
        _ = request.POST['interest_toggle']
        if not session.stats_on.__contains__('Interest'):
            session.stats_on += 'Interest,'
    except Exception as _:
        pass
    if not session.stats_on.__contains__('Understanding') and not session.stats_on.__contains__('Interest'):
        return redirect(reverse("rtr:prof_settings"), {"error_message": "Select at least one of the stats"})
    if session.stats_on[-1] == ",":
        session.series = session.stats_on[:len(session.stats_on) - 1]
    session.save()
    return HttpResponseRedirect('/rtr/profDisplay')


@login_required()
def prof_settings(request):
    if request.session.get('type') == 'creater':
        return render(request, 'rtr/prof_settings.html')
    else:
        return redirect(request, 'rtr/index.html')


def loginUser(request):
    username = request.POST['username']
    password = request.POST['password']
    session = request.POST['session']
    typeSession = request.POST['type_session']
    typeLogin = request.POST['optionLogin']
    if typeSession == "create":
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            try:
                series = Series.objects.get(series_id=session, live=False)
                series.live = True
                series.save()
                newSession = Session.objects.create(series=series, create_time=timezone.now(), stats_on="")
            except Series.DoesNotExist:
                try:
                    if session == 'a':
                        request.session.__setitem__('session', str(Session.objects.get(series_id=Series.objects.get(
                            series_id=session)).id))
                        request.session.__setitem__('type', 'creater')
                        return HttpResponseRedirect('/rtr/profDisplay')
                    else:
                        Series.objects.get(series_id=session)
                        return render(request, 'rtr/index.html', {"error_message": "Session already in progress"})
                except Series.DoesNotExist:
                    newSeries = Series.objects.create(series_id=session)
                    newSession = Session.objects.create(
                        series=newSeries, create_time=timezone.now(), stats_on="")
            request.session.__setitem__('session', str(newSession.id))
            request.session.__setitem__('type', 'creater')
            return HttpResponseRedirect(reverse("rtr:prof_settings"))
        else:
            return render(request, 'rtr/index.html', {"error_message": "Incorrect Username and/or Password"})
    elif typeSession == "join":
        try:
            series = Series.objects.get(series_id=session, live=True)
            session = Session.objects.filter(series_id=series).latest('create_time')
            stats = session.stats_on.split(",")
            stat_ids = ""
            for stat in stats:
                newStats = Stats.objects.create(session=session, name=stat)
                stat_ids += str(newStats.id) + ","
            request.session.__setitem__('session', str(session.id))
            request.session.__setitem__('type', 'joiner')
            request.session.__setitem__('statids', stat_ids)
            return redirect(reverse('rtr:audience_display'))
        except Series.DoesNotExist:
            return render(request, 'rtr/index.html', {"error_message": "Incorrect session, not currently running"})
    elif typeSession == 'view':
        try:
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                try:
                    series = Series.objects.get(series_id=session)
                except Series.DoesNotExist:
                    return render(request, 'rtr/index.html', {"error_message": "No Such Session"})
                return HttpResponseRedirect('/rtr/viewSeries/' + str(series.id))
            else:
                return render(request, 'rtr/index.html', {"error_message": "Incorrect Username and/or Password"})
        except Series.DoesNotExist:
            return render(request, 'rtr/index.html', {"error_message": "Incorrect session, not currently running"})
    else:
        return render(request, 'rtr/index.html', {"error_message": "Something Very Wrong Happened"})


@login_required()
def view_series(request, series_id):
    try:
        sessions = Session.objects.filter(series_id=Series.objects.get(pk=series_id))
        return render(request, 'rtr/view_series.html', {"Sessions": sessions})
    except Series.DoesNotExist:
        return redirect(reverse('rtr:index'))


@login_required()
def view_session(request, session_id):
    try:
        session = Session.objects.get(pk=session_id)
        stats = Stats.objects.filter(session=session)
        context = {}
        changes = []
        # groups_of_stats = {}
        # for stat in stats:
        #     groups_of_stats.get(stat.name, []).append(stat)

        for stat in stats:
            total_change = all_changes(stat)
            if total_change:
                changes.append(total_change)
        context['changes'] = changes
        return render(request, 'rtr/view_session.html', context)
    except Session.DoesNotExist:
        return redirect(reverse('rtr:index'))





def all_changes(stat):
    individual_changes = Stat.objects.filter(stats=stat).order_by('timestamp')
    if individual_changes:
        end_time = individual_changes.reverse()[0].timestamp
        delta = (end_time - individual_changes[0].timestamp).total_seconds() * 6
        x = []
        y = []
        last_time = None
        net_change_over_interval = 0
        for change in individual_changes:
            if last_time and (last_time + timedelta(minutes=delta)) < change.timestamp:
                net_change_over_interval += change.change
            else:
                if last_time:
                    x.append(str(last_time.hour) + ":" + str(last_time.minute))
                else:
                    x.append(str(change.timestamp.hour) + ":" + str(change.timestamp.minute))
                y.append(net_change_over_interval + change.change)
                net_change_over_interval = 0
                last_time = change.timestamp

        return tuple((mark_safe(x), y, stat.name, stat.id))
    else:
        return None