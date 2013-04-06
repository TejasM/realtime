# Create your views here.
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect


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


def signup_post(request):
    username = request.POST['username']
    password = request.POST['password']
    email_address = request.POST['email_address']
    first_name = request.POST['first_name']
    last_name = request.POST['last_name']
    term = request.POST['term']

    if term is "off":
        return redirect(reverse("signup"))

    User.objects.create(username=username, password=password, email=email_address, first_name=first_name,
                        last_name=last_name)
    return redirect(reverse("signup"))