# Create your views here.
from functools import wraps
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
import sys


def index(request):
    return render(request, 'index/index.html')


def about(request):
    return render(request, 'index/about.html')


def blog_post(request):
    return render(request, 'index/blog-post.html')


def customers(request):
    return render(request, 'index/customers.html')


def contact(request):
    return render(request, 'index/contact.html')


def features(request):
    return render(request, 'index/features.html')


def pricing(request):
    return render(request, 'index/pricing.html')


def signup(request):
    return render(request, 'index/signup.html')


def team(request):
    return render(request, 'index/team.html')


def validateEmail(email):
    from django.core.validators import validate_email
    from django.core.exceptions import ValidationError
    try:
        validate_email( email )
        return True
    except ValidationError:
        return False


def check_input(f):
    @wraps(f)
    def wrapper(request, *args, **kwds):
        email_address = request.POST['email_address']
        username = request.POST['username']
        if not validateEmail(email_address):
            messages.error(request, "Invalid email address")
            return redirect(reverse("signup"))
        try:
            User.objects.get(username=username)
            messages.error(request, "Username already exists, try another name")
            return redirect(reverse("signup"))
        except User.DoesNotExist:
            return f(request, *args, **kwds)
    return wrapper


@check_input
def signup_post(request):
    username = request.POST['username']
    password = request.POST['password']
    email_address = request.POST['email_address']
    first_name = request.POST['first_name']
    last_name = request.POST['last_name']
    term = request.POST.get('term', '')

    if str(term) == '':
        messages.error(request, "You must accept the terms and agreement")
        return redirect(reverse("signup"))

    user = User.objects.create(username=username, email=email_address, first_name=first_name, last_name=last_name)
    user.set_password(password)
    user.save()
    return redirect(reverse("rtr:index"))