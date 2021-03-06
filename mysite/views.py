from django.contrib.auth import authenticate
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.sessions.models import Session
import json
import urllib
from django.conf import settings
from . import models, forms
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib import auth
from django.contrib.auth.decorators import login_required
# Create your views here.
# def index(request):
#     years = range(1960,2021)
#     try:
#         urid = request.GET['user_id']
#         urpass = request.GET['user_pass']
#         uryear = request.GET['byear']
#         urfcolor = request.GET.getlist('fcolor')
#     except:
#         urid = None

#     if urid != None and urpass == '12345':
#         verified = True
#     else:
#         verifeid = False
#     return render(request, 'index.html', locals())


def index(request, pid=None, del_pass=None):
    if request.user.is_authenticated:
        username = request.user.username
        useremail = request.user.email
        try:
            user = models.User.objects.get(username=username)
            diaries = models.Diary.objects.filter(user=user).order_by('-ddate')
        except:
            pass
    messages.get_messages(request)
    return render(request, 'index.html', locals())

def listing(request):
    posts = models.Post.objects.filter(enabled=True).order_by('-pub_time')[:150]
    moods = models.Mood.objects.all()
    return render(request, 'listing.html', locals())


@login_required(login_url='/login/')
def posting(request):
    if request.user.is_authenticated:
        username = request.user.username
        useremail = request.user.email
    messages.get_messages(request)

    if request.method == 'POST':
        user = User.objects.get(username=username)
        diary = models.Diary(user=user)
        post_form = forms.DiaryForm(request.POST, instance=diary)
        if post_form.is_valid():
            messages.add_message(request, messages.INFO, '???????????????')
            post_form.save()
            return HttpResponseRedirect('/')
        else:
            messages.add_message(request, messages.INFO, '??????????????????????????????????????????....')
    else:
        post_form = forms.DiaryForm()
        messages.add_message(request, messages.INFO, '??????????????????????????????????????????....')
    return render(request, 'posting.html', locals())


def contact(request):
    if request.method == 'POST':
        form = forms.ContactForm(request.POST)
        if form.is_valid():
            message = "?????????????????????"
            user_name = form.cleaned_data['user_name']
            user_city = form.cleaned_data['user_city']
            user_school = form.cleaned_data['user_school']
            user_email  = form.cleaned_data['user_email']
            user_message = form.cleaned_data['user_message']
            mail_body = u'''
???????????????{}
???????????????{}
???????????????{}
?????????????????????
{}'''.format(user_name, user_city, user_school, user_message)
            send_mail(
    '????????????',
    mail_body,
    'a6898208@gmail.com',
    [user_email],
    fail_silently=False,
)

        else:
            message = "??????????????????????????????????????????"
    else:
        form = forms.ContactForm()
    return render(request, 'contact.html', locals())



def post2db(request):
    if request.method == 'POST':
        post_form = forms.PostForm(request.POST)
        if post_form.is_valid():
            ''' Begin reCAPTCHA validation '''
            recaptcha_response = request.POST.get('g-recaptcha-response')
            url = 'https://www.google.com/recaptcha/api/siteverify'
            values = {
                'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
                'response': recaptcha_response
            }
            data = urllib.parse.urlencode(values).encode()
            req =  urllib.request.Request(url, data=data)
            response = urllib.request.urlopen(req)
            result = json.loads(response.read().decode())
            ''' End reCAPTCHA validation '''
            if result['success']:
                message = "??????????????????????????????????????????????????????????????????"
                post_form.save()
                return HttpResponseRedirect('/list/')
            else:
                message = "Invalid reCAPTCHA. Please try again."
        else:
            message = '????????????????????????????????????????????????...'
    else:
        post_form = forms.PostForm()
        message = '????????????????????????????????????????????????...'          

    return render(request, 'post2db.html', locals())


def login(request):
    if request.method == 'POST':
        login_form = forms.LoginForm(request.POST)
        if login_form.is_valid():
            login_name=request.POST['username'].strip()
            login_password=request.POST['password']
            user = authenticate(username=login_name, password=login_password)
            if user is not None:
                if user.is_active:
                    auth.login(request, user)
                    print("success")
                    messages.add_message(request, messages.SUCCESS, '???????????????')
                    return redirect('/')
                else:
                    messages.add_message(request, messages.WARNING, '??????????????????')
            else:
                messages.add_message(request, messages.WARNING, '????????????')
        else:
            messages.add_message(request, messages.INFO,'??????????????????????????????')
    else:
        login_form = forms.LoginForm()
    return render(request, 'login.html', locals())



def logout(request):
    auth.logout(request)
    messages.add_message(request, messages.INFO, '???????????????')
    return redirect('/')

@login_required(login_url='/login/')
def userinfo(request):
    if request.user.is_authenticated:
        username = request.user.username
    try:
        user = User.objects.get(username=username)
        userinfo = models.Profile.objects.get(user=user)
    except:
        pass
    return render(request, 'userinfo.html', locals())