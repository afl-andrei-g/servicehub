import os, json
import sys
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'servicehub.settings') 

import django
django.setup()

from servicehub.models import Memento, Accounts 
from servicehub.classes.base import SendEmail
from servicehub.settings import APP_URL

def Mementos_Announce():
    today = datetime.now()
    future_date = today + timedelta(days=30)

    mementos = Memento.objects.filter(date__date__gte=today, date__date__lte=future_date)

    for memento in mementos:
        due_date = memento.date.date()
        days_left = (due_date - today.date()).days

        status = 0
        message = ""

        if days_left == 14:
            status = 1
            message = "mementoul setat expiră în 14 zile"
        elif days_left == 7:
            status = 2
            message = "mementoul setat expiră în 7 zile"
        elif days_left == 2:
            status = 3
            message = "mementoul setat expiră în 2 zile"
        elif days_left == 0:
            status = 4
            message = "mementoul setat expiră astăzi"

        user = Accounts.objects.filter(id=memento.user).first()
        if user and user.email and status != memento.notify:
            SendEmail(user.email, 'notificare', {
                "title": "Mementoul setat expiră curând",
                "message": f"Îți scriem acest mesaj pentru că {message}. {memento.title}",
                "url": f"{APP_URL}/dashboard/mementos"
            })

            if memento.notify == 4:
                memento.delete()
            else:
                memento.notify = status
                memento.save()

if __name__ == "__main__":
    Mementos_Announce()
