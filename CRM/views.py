from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic.base import View

from CRM.forms import LoginForm

class Home(LoginRequiredMixin , View):

    login_url = '/login/'
    redirect_field_name = 'next'

    def get(self, request, *args, **kwargs):
        context = dict()
        return render(request, 'CRM/index.html', context)

class Login(View):

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('crm:home')
        context = dict()
        context['login_form'] = LoginForm()
        return render(request, 'CRM/login.html', context)

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST or None)
        if form.is_valid():
            user = authenticate(request, username=form.cleaned_data['email'], password=form.cleaned_data['password'])
            if user is not None:
                login(request, user)
                redirect_url = request.POST.get('next', reverse('crm:home'))
                return redirect(redirect_url)
            else:
                messages.error(request, 'Email ou mot de passe invalide!')
                return redirect('crm:login')

        messages.error(request, 'Veuillez verifier les champs puis ressayer')
        return redirect('crm:login')

class Me(LoginRequiredMixin, View):

    login_url = '/login/'
    redirect_field_name = 'next'

    def get(self, request, *args, **kwargs):
        return HttpResponse("HI")