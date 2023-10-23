import datetime
import random
from contextlib import closing

from django.conf import settings
from django.core.mail import send_mail
from django.db import connection
from django.shortcuts import render, redirect
from methodism import generate_key
from eskiz_sms import EskizSMS
from .models import User, OtpToken
from django.contrib.auth.decorators import login_required
from methodism import code_decoder
from django.contrib.auth import login as django_login, authenticate, logout

from core.models import Xodimlar
from core.service.forms import XodimlarForm


def login(request):
    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = User.objects.filter(username=username).first()
        if not user:
            return render(request, 'dashboard/login.html', {"error": 'User yoki password xato '})
        if not user.check_password(password):
            return render(request, 'dashboard/login.html', {"error": 'User yoki password xato '})

        code = random.randint(100_000, 999_999)

        email = "sukhrobisroilov@mail.ru"
        password = "Gq6OYTfRLfUBXB9kqJKK1O0DQrvqBmLtMy6dSH8k"
        eskiz = EskizSMS(email=email, password=password)
        eskiz.send_sms(mobile_phone='998992087910', message=f'{code}', from_whom='4546')
        # send_mail(subject='Kodi', message=f'Kodini Xechkimga bermang {code}', from_email=settings.EMAIL_HOST_USER,
        #           recipient_list=[user.email])
        token = generate_key(20) + '#' + str(code) + '#' + generate_key(20)

        shifr = "pbkdf2_sha256$600000$" + code_decoder(token, l=2)
        otp = OtpToken.objects.create(key=token, by=2, extra={'user_id': user.id})

        request.session['otp_token'] = otp.key
        request.session['user_id'] = user.id
        request.session['code'] = code

        return redirect('otp')
    ctx = {}

    return render(request, 'dashboard/login.html', ctx)


def register(request):
    if request.POST:
        email = request.POST.get('email')
        username = request.POST.get('username')
        fio = request.POST.get('fio')
        password = request.POST.get('password')
        re_password = request.POST.get('re_pass')
        user_sql = f"""
               SELECT id FROM core_user 
                WHERE email='{email}' or username ='{username}'
        
        """
        with closing(connection.cursor()) as cursor:
            cursor.execute(user_sql)
            user = cursor.fetchone()
        if user:
            return render(request, 'dashboard/register.htnl', {'error': 'User mavjud'})
        if re_password != password:
            return render(request, 'dashboard/register.htnl', {'error': 'Parollar mos emas'})
        code = random.randint(100_000, 999_999)

        email = "sukhrobisroilov@mail.ru"
        password = "Gq6OYTfRLfUBXB9kqJKK1O0DQrvqBmLtMy6dSH8k"
        eskiz = EskizSMS(email=email, password=password)
        eskiz.send_sms(mobile_phone='998992087910', message=f'{code}', from_whom='4546')
        # send_mail(subject='Kodi', message=f'Kodini Xechkimga bermang {code}', from_email=settings.EMAIL_HOST_USER,
        #           recipient_list=[user.email])
        token = generate_key(20) + '#' + str(code) + '#' + generate_key(20)

        shifr = "pbkdf2_sha256$600000$" + code_decoder(token, l=2)
        otp = OtpToken.objects.create(key=token, by=1,
                                      extra={'username': username, 'fio': fio, 'email': email, 'password': password})

        request.session['otp_token'] = otp.key

        request.session['code'] = code

        return redirect('otp')

    return render(request, 'dashboard/register.html')


def otp(request):
    token = request.session.get('otp_token')
    if not token:
        redirect('login')

    if request.POST:
        kod = request.POST.get('code')
        otp = OtpToken.objects.filter(key=token).first()
        if otp.is_verified or otp.is_expired:
            return render(request, 'dashboard/otp.html', {'error': 'Bu eskirgan token'})

        now = datetime.datetime.now()
        if (now - otp.created).total_seconds() >= 120:
            return render(request, 'dashboard/otp.html', {'error': 'Token Ajratilgan Vaqt tugadi'})
        code = token.split('#')[1]

        if str(code) != str(kod):
            otp.tries += 1
            otp.save()
            return render(request, 'dashboard/otp.html', {'error': 'Xato kode'})
        if otp.by == 2:
            if str(otp.extra['user_id']) != str(request.session.get('user_id')):
                return redirect('login')
            user = User.objects.filter(id=int(request.session.get('user_id'))).first()

            if not user:
                redirect('login')

            django_login(request, user)
            otp.is_expired = True,
            otp.is_verified = True
            try:
                del request.session['otp_token']
                del request.session['user_id']
                del request.session['code']
            except:
                pass
            return redirect('index')
        if otp.by == 1:
            user = User.objects.create_user(**otp.extra)
            django_login(request, user)
            authenticate(request)
            otp.is_expired = True
            otp.is_verified = True
            otp.extra = {}
            otp.save()
            try:
                del request.session['otp_token']

                del request.session['code']
            except:
                pass
            return redirect('index')

    return render(request, 'dashboard/otp.html')


def re_opt(request):
    old_token = request.session.get('otp_token')
    if not old_token:
        return redirect('login')

    old_otp = OtpToken.objects.filter(key=old_token).first()
    if not old_otp:
        return redirect('login')
    old_otp.is_expired = True
    old_otp.save()
    code = random.randint(100_000, 999_999)
    # send_mail(subject='Kodi', message=f'Kodini Xechkimga bermang {code}', from_email=settings.EMAIL_HOST_USER,
    #           recipient_list=[user.email])
    new_token = generate_key(20) + '#' + str(code) + '#' + generate_key(20)
    email = "sukhrobisroilov@mail.ru"
    password = "Gq6OYTfRLfUBXB9kqJKK1O0DQrvqBmLtMy6dSH8k"
    eskiz = EskizSMS(email=email, password=password)
    eskiz.send_sms(mobile_phone='998992087910', message=f'{code}', from_whom='4546')

    # shifr = "pbkdf2_sha256$600000$" + code_decoder(token, l=2)
    otp = OtpToken.objects.create(key=new_token, by=old_otp.by, extra=old_otp.extra)
    # print(otp.key)
    # print(shifr)
    request.session['otp_token'] = otp.key
    if otp.by == 2:
        request.session['user_id'] = old_otp.extra['user_id']
        old_otp.extra = {}
        old_otp.save()

    request.session['code'] = code
    return redirect('otp')


# DASHBOARD CRUD SISTEMA

def chiqish(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def ishchi_list(request):
    ctx = {
        'emp_all': Xodimlar.objects.all()
    }

    return render(request, 'dashboard/page/list.html', ctx)


@login_required(login_url='login')
def form_emp(request):
    if request.POST:

        form = XodimlarForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('ishchi_emp')
        else: print('error')
    form = XodimlarForm()
    ctx = {
        'form': form
    }

    return render(request, 'dashboard/page/form.html', ctx)


@login_required(login_url='login')
def info(request, pk):
    employes = Xodimlar.objects.get(pk=pk)
    print(employes)
    ctx = {
        'employes': employes
    }

    return render(request, 'dashboard/page/info.html', ctx)


@login_required(login_url='login')
def ishchi_edit(request):
    return render(request, 'dashboard/page/form.html')


@login_required(login_url='login')
def xodim_delete(request, pk, conf=False):
    if conf:
        try:
            Xodimlar.objects.get(pk=pk).delete()
        except:
            pass
    return redirect('ishchi_emp')
