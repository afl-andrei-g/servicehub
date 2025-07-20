# SERVICEHUB @ CORE PACKAGES
import django
from django.core.files.images import get_image_dimensions
from django.shortcuts import render, HttpResponse, redirect
from django.http import HttpResponse, JsonResponse
from django.core import serializers
from django.contrib import messages
import time, bcrypt, json, uuid, re, datetime, locale, os, asyncio
from pathlib import Path
import time as time2
# EMAILS
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.forms.models import model_to_dict
# 
import requests
from servicehub.models import *
from servicehub.settings import APP_URL, AVATAR_DEFAULT
locale.setlocale(locale.LC_TIME, 'ro_RO.UTF-8')
# Misc
from datetime import datetime, time, timedelta
from django.utils.timezone import make_aware
from django.utils.dateparse import parse_datetime
###########################

# Auth
def CheckMail(email):
    return email.lower().endswith('@gmail.com') or email.lower().endswith('@yahoo.com')

def UserDidAuth(request):
    if request.session.get('userdata') is not None:
        return True

    return False

import random, string
def GeneratePassword(length=12):
    chars = string.ascii_letters + string.digits
    password = ''.join(random.choice(chars) for _ in range(length))
    return password

def RegisterAccount(account_type, name, email, cui, pw, phone, workshop):
    a = Accounts.objects.create(
        email = email,
        name = name,
        password = bcrypt.hashpw(pw.encode('utf-8'), bcrypt.gensalt()).decode(),
        account_type = account_type,
        cui = cui,
        phone = phone,
        avatar = AVATAR_DEFAULT,
        workshops = workshop
    )

    return a.pk

def Auth(request):
    if UserDidAuth(request) == True: return redirect('/dashboard')

    # id, email, password, account_type
    if request.method == 'POST':
        if 'login' in request.POST:
            if request.POST.get('LoginEmail') is None or request.POST.get('LoginPw') is None:
                messages.success(request, "Nu ai completat toate câmpurile.")

            try:
                user = Accounts.objects.get(email=request.POST["LoginEmail"])
                pw = user.password.encode('utf-8')

                if bcrypt.hashpw(request.POST["LoginPw"].encode('utf-8'), pw) == pw:
                    request.session['userdata'] = {
                        'id': user.id,
                        'name': user.name,
                        'email': user.email,
                        'cui': user.cui,
                        'account_type': user.account_type,
                        'avatar': user.avatar
                    }

                    request.session.modified = True

                    return redirect('/dashboard')
                else:
                    messages.success(request, "Parola este greșită.")
            except Accounts.DoesNotExist:
                messages.success(request, "Acest cont nu există.")
        elif 'register' in request.POST:
            try:
                for i in ['RegisterEmail', 'RegisterPw', 'RegisterRepeatPw', 'RegisterCompany', 'RegisterCUI']:
                    if request.POST.get(i) is None:
                        messages.success(request, "Nu ai completat toate câmpurile.")
                        return render(request, 'auth/auth.html')

                if request.POST.get('RegisterTerms') is None or request.POST['RegisterTerms'] == "off":
                    messages.success(request, "Pentru a te putea înregistra, trebuie să fii de acord cu termenii și condițiile.")
                    return render(request, 'auth/auth.html')

                email = request.POST['RegisterEmail'].lower()
                if CheckMail(email) == False:
                    messages.success(request, "Te poți înregistra doar cu un e-mail de tip gmail.com sau yahoo.com.")
                    return render(request, 'auth/auth.html')

                if request.POST['RegisterPw'] != request.POST['RegisterRepeatPw']:
                    messages.success(request, "Parolele introduse nu coincid.")
                    return render(request, 'auth/auth.html')

                pw = request.POST['RegisterPw'].replace(" ", "")
                pw_length = len(pw)
                if pw_length < 8 or pw_length > 32:
                    messages.success(request, "Parola trebuie să fie compusă din minim 8 și maxim 32 caractere.")
                    return render(request, 'auth/auth.html')
            except Exception:
                pass

            # if grecaptcha_verify(request) == False:
            #     data["notification"] = "Nu ai completat reCaptcha."
            #     return render(request, "register.html", data)

            f2 = Accounts.objects.filter(email=request.POST['RegisterEmail'])
            if f2.exists():
                messages.success(request, "Deja există un cont cu acest e-mail.")
                return render(request, 'auth/auth.html')
            else:
                a = RegisterAccount(
                    'company',
                    request.POST['RegisterCompany'],
                    request.POST['RegisterEmail'],
                    request.POST['RegisterCUI'],
                    pw,
                    '07XXXXXXXX',
                    ''
                )

                request.session['userdata'] = {
                    'id': a,
                    'name': request.POST['RegisterCompany'],
                    'email': request.POST['RegisterEmail'],
                    'cui': request.POST['RegisterCUI'],
                    'account_type': 'company',
                    'avatar': AVATAR_DEFAULT
                }
                request.session.modified = True

                messages.success(request, "Contul tău a fost creat cu succes! Bine ai venit pe ServiceHub.")

                return redirect('/dashboard')

    return render(request, 'auth/auth.html')

def Logout(request):
    request.session['userdata'] = None
    request.session.modified = True

    return redirect('/auth')