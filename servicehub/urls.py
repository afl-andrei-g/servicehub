from django.urls import path
from . import views
from .classes import api, auth, users

urlpatterns = [
    # Landing Page
    path('', views.LandingPage, name='LandingPage'),

    # Autentificare
    path('auth', auth.Auth, name='Auth'),
    path('auth/logout', auth.Logout, name='Logout'),

    # Dashboard
    path('dashboard', users.DashboardHome, name='DashboardHome'),

    # Client
    path('dashboard/mementos', users.Client_SeeMementos, name='Client_SeeMementos'),

    # Company
    path('dashboard/clients', users.Company_SeeClients, name='Company_SeeClients'),
    path('dashboard/techs', users.Company_SeeTechs, name='Company_SeeTechs'),
    path('dashboard/appointments', users.Company_SeeAppointments, name='Company_SeeAppointments'),

    # Pot accesa: clienți, tehnicieni, companii
    path('dashboard/service/<int:id>', users.SeeService, name='SeeService'),

    # API
    path('api/ore', api.GetAvailableHours, name='ore'),
]
