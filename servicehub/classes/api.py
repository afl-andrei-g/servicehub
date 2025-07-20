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

def GetAvailableHours(request):
    date_str = request.GET.get('date') 
    if not date_str:
        return JsonResponse({'error': 'A intervenit o eroare'}, status=400)

    try:
        selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return JsonResponse({'error': 'A intervenit o eroare'}, status=400)

    opening_time = time(8, 0)
    closing_time = time(20, 0)
    slot_duration = timedelta(minutes=60)

    slots = []
    current = make_aware(datetime.combine(selected_date, opening_time))
    end = make_aware(datetime.combine(selected_date, closing_time))

    while current + slot_duration <= end:
        slots.append(current)
        current += slot_duration

    start_of_day = make_aware(datetime.combine(selected_date, time.min))
    end_of_day = make_aware(datetime.combine(selected_date, time.max))

    occupied = Services.objects.filter(date__range=(start_of_day, end_of_day)).values_list('date', flat=True)

    available = [slot.strftime('%H:%M') for slot in slots if slot not in occupied]

    return JsonResponse({'available_slots': available})