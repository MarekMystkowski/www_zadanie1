from wybory.user.forms import UserForm
from django.contrib.auth.models import User
from django.shortcuts import HttpResponseRedirect, render
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone


def index(request):
    try:
        next_page = request.POST['next']
    except:
        next_page = "/"
    if request.user.is_authenticated():
        return HttpResponseRedirect(next_page)
    error = ""
    if request.method == 'POST':
        if request.POST.get('submit_login', False):
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect(next_page)
                else:
                    error = "To konto jest zablokowane."
            else:
                error = "Błędne dane logowania."


        if request.POST.get('submit_register'):
            user_form = UserForm(data=request.POST)

            if user_form.is_valid():
                user = user_form.save()
                user.set_password(user.password)
                user.save()
                login(request, authenticate(username=request.POST['username'], password=request.POST['password']))
                return HttpResponseRedirect(next_page)

            else:
                error = user_form.errors

    return render(request, 'login.html', {
        'user_form': UserForm(),
        'error': error,
        'next': request.GET['next'] if request.GET and 'next' in request.GET else next_page
    })

def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/')
