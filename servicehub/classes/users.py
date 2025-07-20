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

from . import api, auth, base, users

# Dashboard
def GetDashboardData(request):
    data = {}
    data['user'] = request.session.get('userdata', [])
    data['appurl'] = APP_URL
    data['date'] = base.GetDate()

    return data

def parse_ron(note_str):
    try:
        return int(note_str.replace(",", "").replace("RON", "").strip())
    except:
        return 0

def get_revenue_data(workshop_id, status):
    services = Services.objects.filter(workshop=workshop_id, status=4).all()
    monthly_data = {}

    for service in services:
        month = service.date.strftime('%Y-%m')
        revenue = parse_ron(service.note)

        if month not in monthly_data:
            monthly_data[month] = 0
        monthly_data[month] += revenue

    sorted_data = dict(sorted(monthly_data.items()))
    
    labels = list(sorted_data.keys())
    data = list(sorted_data.values())

    return {
        'labels': labels,
        'data': data,
    }

def DashboardHome(request):
    if auth.UserDidAuth(request) == False: return redirect('/auth')

    acc_type = request.session['userdata']['account_type']
    data = GetDashboardData(request)

    if acc_type == "admin":
        data['companies'] = [
            {
                **model_to_dict(m),
                'clients': Accounts.objects.filter(account_type="client", workshops__contains=f"|{m.id}|").all().count(),
                'vehicles': Vehicles.objects.filter(workshops__contains=f"|{m.id}|").all().count()
            }
            for m in Accounts.objects.filter(account_type="company").all()
        ]
        
        data['clients'] = Accounts.objects.filter(account_type="client").all()
        data['vehicles'] = Vehicles.objects.all()

        return render(request, 'dashboard/admin.html', context=data)
    elif acc_type == "company" or acc_type == "technician":
        data['company'] = GetCompany(request.session['userdata']['cui'])

        if request.method == "POST":
            if 'appointment' in request.POST:
                try:
                    if base.ValidateForm(request.POST, [
                        'serviceVehicle',
                        'serviceDate',
                        'serviceDate_hour',
                        'serviceTitle',
                        'serviceNote'
                    ]) == False:
                        raise Exception("Nu ai completat toate câmpurile")

                    service_datetime_str = f"{request.POST['serviceDate']} {request.POST['serviceDate_hour']}:00"
                    date = datetime.strptime(service_datetime_str, "%Y-%m-%d %H:%M:%S")

                    time_range_start = date - timedelta(minutes=30)
                    time_range_end = date + timedelta(minutes=30)

                    conflict_exists = Services.objects.filter(
                        date__range=(time_range_start, time_range_end)
                    ).exists()

                    if conflict_exists:
                        raise Exception(f"Există deja o programare selectată în acel interval.")

                    Services.objects.create(
                        veh = request.POST['serviceVehicle'],
                        title = request.POST['serviceTitle'],
                        note = f"{base.format(request.POST['serviceNote'])} RON",
                        notes = [],
                        status = 0,
                        date = date,
                        workshop = data['company'].id
                    )

                    messages.success(request, "Programarea a fost adăugată cu succes! 📅")
                
                    return redirect('/dashboard')
                except Exception as e:
                    messages.success(request, e)

        data['vehicles'] = []
        data['services'] = []
        data['opened_services'] = []

        data['revenue'] = get_revenue_data(data['company'].id, 4)

        now = datetime.now()
        start = make_aware(datetime.combine(now.date(), datetime.min.time()))
        end = start + timedelta(days=7)

        for i in Vehicles.objects.filter(workshops__contains=f"|{data['company'].id}|").all():
            try:
                account = Accounts.objects.get(id=i.owned_by)
                i.owned_friendly = account.name
                i.avatar = account.avatar
            except Accounts.DoesNotExist:
                i.owned_friendly = 'N/A'
                i.avatar = AVATAR_DEFAULT

            data['vehicles'].append(i)

            for j in Services.objects.filter(workshop=data['company'].id, veh=i.id, date__gte=start, date__lt=end, status__in=[0]).order_by('id').all()[:5]:
                j.owned_friendly = i.owned_friendly
                j.avatar = i.avatar

                j.name = i.name
                j.plate = i.plate
                j.f_status = SERVICE_MESSAGES_SHORT[int(j.status)]
                j.perc = int(j.status)*25

                data['services'].append(j)

            for j in Services.objects.filter(workshop=data['company'].id, veh=i.id, status__in=[1,2,3]).order_by('id').all()[:3]:
                j.owned_friendly = i.owned_friendly
                j.avatar = i.avatar

                j.name = i.name
                j.plate = i.plate
                j.f_status = SERVICE_MESSAGES_SHORT[int(j.status)]
                j.perc = int(j.status)*25

                data['opened_services'].append(j)

        data['empty_services'] = range(5-len(data['services']))
        data['empty_o_services'] = range(3-len(data['opened_services']))
        data['header'] = {}
        data['header']['vehicles'] = Vehicles.objects.filter(workshops__contains=f"|{data['company'].id}|").count()

        return render(request, 'dashboard/company.html', context=data)
    elif acc_type == "client":
        if request.method == "POST":
            if 'memento' in request.POST:
                try:
                    if base.ValidateForm(request.POST, [
                        'mementoReason',
                        'mementoVehicle',
                        'mementoDate'
                    ]) == False:
                        raise Exception("Nu ai completat toate câmpurile")
                    
                    try:
                        vehicle = Vehicles.objects.get(id=request.POST['mementoVehicle'])
                    except Vehicles.DoesNotExist:
                        return redirect('/dashboard')

                    date = datetime.strptime(request.POST['mementoDate'], "%Y-%m-%dT%H:%M")
                    reason = f"Vehiculul tău {vehicle.name} va trebui să efectueze '{Mementos[request.POST['mementoReason']]}' pe {date}. Asigură-te că ai contactat service-ul în vederea programării."
                
                    Memento.objects.create(
                        title = reason,
                        notify = 0,
                        user = request.session['userdata']['id'],
                        date = date
                    )

                    messages.success(request, "Memento a fost creat cu succes!")

                    return redirect('/dashboard/mementos')
                except Exception as e:
                    messages.success(request, e)
            elif 'vehedit' in request.POST:
                try:
                    if base.ValidateForm(request.POST, [
                        'serviceVehicle',
                        'serviceKM'
                    ]) == False:
                        raise Exception("Nu ai completat toate câmpurile")

                    km = int(request.POST['serviceKM'])
                    if km < 0 or km > 2000000:
                        raise Exception("Kilometrajul trebuie să aibă o valoare între 0 și 2,000,000.")

                    try:
                        vehicle = Vehicles.objects.get(id=request.POST['serviceVehicle'], owned_by=request.session['userdata']['id'])
                    except Vehicles.DoesNotExist:
                        raise Exception

                    vehicle.km = request.POST['serviceKM']
                    vehicle.save()

                    messages.success(request, "Detaliile vehiculului au fost actualizate!")
                except Exception as e:
                    messages.success(request, e)

        mementos = Memento.objects.filter(user=request.session['userdata']['id'], notify__lt=4).all()
        data['memento'] = [model_to_dict(memento) for memento in mementos]
        data['vehicles'] = []
        data['services'] = []
        for i in Vehicles.objects.filter(owned_by=request.session['userdata']['id']).all():
            try:
                account = Accounts.objects.get(id=i.owned_by)
                i.owned_friendly = account.name
                i.avatar = account.avatar
            except Accounts.DoesNotExist:
                i.owned_friendly = 'N/A'
                i.avatar = AVATAR_DEFAULT

            data['vehicles'].append(i)

            for j in Services.objects.filter(veh=i.id).order_by('-id').all():
                j.owned_friendly = i.owned_friendly
                j.avatar = i.avatar

                j.name = i.name
                j.plate = i.plate
                j.f_status = SERVICE_MESSAGES_SHORT[int(j.status)]
                j.perc = int(j.status)*25

                j.company = model_to_dict(GetCompanyFromID(j.workshop))

                data['services'].append(j)

        return render(request, 'dashboard/client.html', context=data)


def GetCompany(cui):
    a = Accounts.objects.filter(cui=cui).all().first()
    if a == None:
        a = Acounts.objects.all().first()

    return a

def GetCompanyFromID(id):
    a = Accounts.objects.filter(id=id).all().first()
    if a == None:
        a = Acounts.objects.all().first()

    return a

def Client_SeeMementos(request):
    acc_type = request.session['userdata']['account_type']
    if auth.UserDidAuth(request) == False or acc_type != 'client':
        return redirect('/auth')

    data = GetDashboardData(request)

    mementos = Memento.objects.filter(user=request.session['userdata']['id'], notify__lt=4).all()
    data['mementos'] = [
        {
            **model_to_dict(m),
            'start': m.date.strftime('%Y-%m-%dT%H:%M:%S'),
        }
        for m in mementos
    ]

    return render(request, "dashboard/mementos.html", context=data)

def Company_SeeTechs(request):
    acc_type = request.session['userdata']['account_type']
    if auth.UserDidAuth(request) == False or acc_type != 'company':
        return redirect('/auth')

    if request.method == 'POST':
        try:
            for i in ['companyName', 'companyEmail', 'companyPhone']:
                if request.POST.get(i) is None:
                    raise Exception("Nu ai completat toate câmpurile.")

            email = request.POST['companyEmail'].lower()
            if auth.CheckMail(email) == False:
                raise Exception("Poți introduce doar adrese de e-mail de tip gmail.com sau yahoo.com.")
            
            f2 = Accounts.objects.filter(email=request.POST['companyEmail'])
            if f2.exists():
                raise Exception("Deja există un cont cu acest e-mail.")
            else:
                a = RegisterAccount(
                    'technician', 
                    request.POST['companyName'], 
                    email, 
                    request.session['userdata']['cui'], 
                    auth.GeneratePassword(12), 
                    request.POST['companyPhone'], 
                    ''
                )
                
                messages.success(request, "Contul a fost adăugat cu succes. Am notificat tehnicianul despre crearea contului.")
        except Exception as e:
            messages.success(request, str(e))
            pass 

    data = GetDashboardData(request)
    data['technicians'] = []
    for i in Accounts.objects.filter(cui=request.session['userdata']['cui'], account_type='technician').all():
        if i.id != request.session['userdata']['id']:
            data['technicians'].append({
                'id': i.id,
                'email': i.email,
                'phone': i.phone,
                'name': i.name,
                'company': request.session['userdata']['name'],
            })

    return render(request, "dashboard/techs.html", context=data)

def Company_SeeClients(request):
    acc_type = request.session['userdata']['account_type']
    if auth.UserDidAuth(request) == False or acc_type == 'client':
        return redirect('/auth')

    if request.method == 'POST':
        if 'client' in request.POST:
            try:
                for i in ['clientName', 'clientEmail', 'clientPhone']:
                    if request.POST.get(i) is None or len(request.POST.get(i)) < 1:
                        raise Exception("Nu ai completat toate câmpurile.")

                email = request.POST['clientEmail'].lower()
                if auth.CheckMail(email) == False:
                    raise Exception("Poți introduce doar adrese de e-mail de tip gmail.com sau yahoo.com.")
                
                company = GetCompany(request.session['userdata']['cui']) 
                c = Accounts.objects.filter(email=request.POST['clientEmail']).first()
                if c:
                    if not f'|{company.id}|' in c.workshops:
                        c.workshops = c.workshops.rstrip('|')
                        c.workshops += f'|{company.id}|'
                        c.save()

                        raise Exception("Clientul are deja un cont pe ServiceHub, așadar l-am adăugat în baza ta de date. 💪")
                    else:
                        raise Exception("Acest client a fost adăugat deja în evidența companiei tale.")
                else:
                    a = RegisterAccount(
                        'client',
                        request.POST['clientName'],
                        email,
                        request.session['userdata']['cui'], #TBE CNP
                        auth.GeneratePassword(12),
                        request.POST['clientPhone'], 
                        f'|{company.id}|'
                    )

                    messages.success(request, "Contul a fost adăugat cu succes. Am notificat clientul despre crearea contului. ✅")
            except Exception as e:
                messages.success(request, str(e))
                pass 
        elif 'vehicle' in request.POST:
            try:
                for i in ['vehMake', 'vehModel', 'vehYear', 'vehClient', 'vehPlate']:
                    if request.POST.get(i) is None or len(request.POST.get(i)) < 1:
                        raise Exception("Nu ai completat toate câmpurile.")

                plate = request.POST['vehPlate'].replace(" ", "")
                v = Vehicles.objects.filter(plate=plate).first()
                company = Accounts.objects.filter(cui=request.session['userdata']['cui']).all().first()

                if v:
                    if not f'|{company.id}|' in v.workshops:
                        v.workshops = v.workshops.rstrip("|")
                        v.workshops += f'|{company.id}|'
                        v.save()

                        raise Exception("Această mașină există deja pe ServiceHub, așadar am adăugat-o în baza ta de date. 💪")
                    else:
                        raise Exception("Acest cont este deja în evidența companiei tale.")
                else:
                    Vehicles.objects.create(
                        name = f"{request.POST['vehMake']} {request.POST['vehModel']} {request.POST['vehYear']}",
                        plate = plate,
                        owned_by = request.POST['vehClient'],
                        workshops = f"|{company.id}|",
                        km = 0,
                        last_service = datetime.now().timestamp()
                    )

                    messages.success(request, "Vehiculul a fost adăugat cu succes.")
            except Exception as e:
                messages.success(request, str(e))
                pass 

    cID = GetCompany(request.session['userdata']['cui']).id

    data = GetDashboardData(request)
    data['clients'] = []
    for i in Accounts.objects.filter(workshops__contains=f"|{cID}|", account_type='client').all():
        if i.id != request.session['userdata']['id']:
            data['clients'].append({
                'id': i.id,
                'name': i.name,
                'email': i.email,
                'vehicles': Vehicles.objects.filter(owned_by=i.id).all().count(),
                'company': request.session['userdata']['name'],
            })

    data['vehicles'] = []
    for i in Vehicles.objects.filter(workshops__contains=f"|{cID}|").all():
        try:
            i.owned_friendly = Accounts.objects.get(id=i.owned_by).name
        except Accounts.DoesNotExist:
            i.owned_friendly = 'N/A'

        data['vehicles'].append(i)

    return render(request, "dashboard/clients.html", context=data)

from datetime import datetime, timedelta
from django.utils.dateformat import DateFormat
def Company_SeeAppointments(request):
    acc_type = request.session['userdata']['account_type']
    if auth.UserDidAuth(request) == False or acc_type == 'client':
        return redirect('/auth')

    data = GetDashboardData(request)
    data['company'] = GetCompany(request.session['userdata']['cui'])

    services = Services.objects.filter(workshop=data['company'].id).order_by('-id').all()
    data['services'] = [
        {
            **model_to_dict(service),
            'f_status': SERVICE_MESSAGES_SHORT[service.status]
        }
        for service in services
    ]

    now = datetime.now()
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if now.month == 12:
        end_of_month = now.replace(year=now.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
    else:
        end_of_month = now.replace(month=now.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)

    services_this_month = Services.objects.filter(date__gte=start_of_month, date__lte=end_of_month, status__in=[0]).order_by('date')

    data['services_this_month'] = [
        {
            **model_to_dict(service),
            'start': service.date.strftime('%Y-%m-%dT%H:%M:%S'),  # Convert to ISO 8601 format
        }
        for service in services_this_month
    ]


    return render(request, 'dashboard/programari.html', data)


Mementos = {
    "schimb_ulei": "Schimb ulei",
    "filtru_aer": "Schimb filtru de aer",
    "filtru_motorina": "Schimb filtru motorină",
    "filtru_habitaclu": "Schimb filtru habitaclu",
    "revizie_generala": "Revizie generală",
    "schimb_placute_fata": "Schimb plăcuțe frână față",
    "schimb_placute_spate": "Schimb plăcuțe frână spate",
    "schimb_discuri": "Schimb discuri frână",
    "ITP": "Inspecție tehnică periodică (ITP)",
    "asigurare_rca": "Reînnoire asigurare RCA",
    "schimb_anvelope": "Schimb anvelope (vară/iarnă)",
    "verificare_frigorifica": "Verificare sistem aer condiționat",
    "verificare_baterie": "Verificare/stare baterie",
    "verificare_directie": "Verificare sistem direcție",
    "verificare_suspensie": "Verificare suspensie",
    "schimb_distributie": "Schimb kit distribuție",
    "schimb_ulei_cutie": "Schimb ulei cutie de viteze",
    "schimb_fluide_frene": "Schimb lichid frână",
    "schimb_antigel": "Schimb lichid răcire (antigel)"
}

SERVICE_MESSAGES_SHORT = [
    "Programată",
    "Check-in",
    "Diagnoză",
    "Reparație",
    "Finalizată"
]

SERVICE_MESSAGES = [
    "Programată",
    "Am realizat Check-in-ul vehiculului tău și începem diagnoza în scurt timp.",
    "Am început diagnosticarea vehiculului tău și realizăm verificări complexe. 🛠️",
    "Am început reparația și ne asigurăm că vehiculul tău este reparat sau întreținut corespunzător.",
    "Servisarea a fost finalizată și te așteptăm în locația noastră să îți ridici vehiculul. 💕"
]

def SeeService(request, id):
    acc_type = request.session['userdata']['account_type']
    if auth.UserDidAuth(request) == False:
        return redirect('/auth')

    try:
        service = Services.objects.get(id=id)
    except Services.DoesNotExist:
        return redirect('/dashboard')

    try:
        vehicle = Vehicles.objects.get(id=service.veh)
    except Vehicles.DoesNotExist:
        return redirect('/dashboard')

    try:
        owner = Accounts.objects.get(id=vehicle.owned_by)
    except Accounts.DoesNotExist:
        return redirect('/dashboard')

    data = GetDashboardData(request)
    data['company'] = model_to_dict(GetCompanyFromID(service.workshop))

    if request.method == "POST":
        if 'status' in request.POST:
            try:
                if base.ValidateForm(request.POST, ['serviceStatus']) == False:
                    raise Exception("Nu ai completat toate câmpurile.")

                if datetime.now() < service.date.replace(tzinfo=None):
                    raise Exception("Nu poți modifica statusul acestei servisări deoarece nu a atins timpul programării.")

                new_status = int(request.POST['serviceStatus'])
                # if new_status < 0 or new_status > 4:
                #     raise Exception("Nu poți plasa statusul mai jos decât sau egal cu cel actual.")

                # if new_status <= service.status:
                #     raise Exception("Nu poți plasa statusul mai jos decât sau egal cu cel actual.")

                service.status = new_status
                service.notes.append({
                    "timestamp": datetime.now().isobase.format(),
                    "friendly_timestamp": base.GetFullDate(),
                    "avatar": request.session['userdata']['avatar'],
                    "user": request.session['userdata']['name'],
                    "message": SERVICE_MESSAGES[new_status]
                })

                service.save()

                messages.success(request, "Statusul a fost actualizat cu succes!")

                base.SendEmail(owner.email, 'serviciu', {
                    "vehicle": vehicle.name,
                    "company_name": data['company']['name'],
                    "id": service.id,
                    "title": service.title,
                    "perc": int(service.status)*25,
                    "status": SERVICE_MESSAGES_SHORT[int(service.status)],
                    "price": service.note,
                    "url": f"{APP_URL}/dashboard/service/{service.id}",
                    "msg": SERVICE_MESSAGES[new_status]
                })

                return redirect(f'/dashboard/service/{id}')
            except Exception as e:
                messages.success(request, e)
        elif 'servmsg' in request.POST:
            try:
                if base.ValidateForm(request.POST, ['serviceMessage']) == False:
                    raise Exception("Nu ai completat toate câmpurile.")

                service.notes.append({
                    "timestamp": datetime.now().isobase.format(),
                    "friendly_timestamp": base.GetFullDate(),
                    "avatar": request.session['userdata']['avatar'],
                    "user": request.session['userdata']['name'],
                    "message": request.POST['serviceMessage']
                })

                service.save()
            except Exception as e:
                messages.success(request, e)

    data['service'] = model_to_dict(service)
    data['percentage'] = service.status*25
    data['vehicle'] = model_to_dict(vehicle)
    data['notes'] = sorted(
        data['service']['notes'],
        key=lambda note: parse_datetime(note["timestamp"])
    )

    return render(request, "dashboard/service.html", context=data)