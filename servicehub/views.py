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
from .models import *
from .settings import APP_URL, AVATAR_DEFAULT
locale.setlocale(locale.LC_TIME, 'ro_RO.UTF-8')
# Misc
from datetime import datetime, time, timedelta
from django.utils.timezone import make_aware
from django.utils.dateparse import parse_datetime
###########################

from .classes import users

def LandingPage(request):
    data = users.GetDashboardData(request)
    return render(request, 'landing.html')

