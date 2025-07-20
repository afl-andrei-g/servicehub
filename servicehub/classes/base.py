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

# Mailing
def SendEmail(to, template, data):
    emailData = data

    html_content = render_to_string(f"emails/{template}.html", emailData)
    text_content = strip_tags(html_content)

    email = EmailMultiAlternatives(
        f"{emailData['title']}",
        text_content,
        "servicehub@hypenet.ro",
        [to]
    )

    email.attach_alternative(html_content, "text/html")
    email.send()

# Forms
def ValidateForm(post, array):
    for i in array:
        if post.get(i) is None or len(post.get(i)) < 1:
            return False

    return True

# Dates
def GetFullDate():
    romanian_weekdays = [
        "Luni", "Marți", "Miercuri", "Joi", "Vineri", "Sâmbătă", "Duminică"
    ]
    
    romanian_months = [
        "Ianuarie", "Februarie", "Martie", "Aprilie", "Mai", "Iunie",
        "Iulie", "August", "Septembrie", "Octombrie", "Noiembrie", "Decembrie"
    ]
    
    today = datetime.today()
    hour_minute = today.strftime("%H:%M")
    weekday = romanian_weekdays[today.weekday()]
    day = today.day
    month = romanian_months[today.month - 1]
    year = today.year
    
    return f"{hour_minute}, {weekday}, {day} {month}, {year}"

def GetDate():
    romanian_weekdays = [
        "Luni", "Marți", "Miercuri", "Joi", "Vineri", "Sâmbătă", "Duminică"
    ]
    
    romanian_months = [
        "Ianuarie", "Februarie", "Martie", "Aprilie", "Mai", "Iunie",
        "Iulie", "August", "Septembrie", "Octombrie", "Noiembrie", "Decembrie"
    ]
    
    today = datetime.today()
    weekday = romanian_weekdays[today.weekday()]
    day = today.day
    month = romanian_months[today.month - 1]
    year = today.year
    
    return f"{weekday}, {day} {month}, {year}"

# Formatting
def format(value):
    try:
        number = float(value) if '.' in str(value) else int(value)
        return f"{number:,}"
    except (ValueError, TypeError):
        return str(value) 

# Google ReCaptcha
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def grecaptcha_verify(request):
    if request.method == 'POST':
        response = {}
        data = request.POST
        captcha_rs = data.get('g-recaptcha-response')
        url = "https://www.google.com/recaptcha/api/siteverify"
        params = {
            'secret': '6LfqMpwpAAAAAJJgJCcbWuYBCf9W3up92HjtXF7-',
            'response': captcha_rs,
            'remoteip': get_client_ip(request)
        }
        verify_rs = requests.get(url, params=params, verify=True)
        verify_rs = verify_rs.json()
        response["status"] = verify_rs.get("success", False)
        response['message'] = verify_rs.get('error-codes', None) or "Unspecified error."
        return response["status"]