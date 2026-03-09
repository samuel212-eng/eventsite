# =============================================
#  URL patterns for the events app
#  Format:  URL  →  view function  →  name
# =============================================

from django.urls import path
from . import views

urlpatterns = [
    # Home
    path('',                            views.home,                name='home'),

    # Event pages
    path('events/',                     views.event_list,          name='event_list'),
    path('events/<int:pk>/',            views.event_detail,        name='event_detail'),
    path('events/create/',              views.event_create,        name='event_create'),
    path('events/<int:pk>/edit/',       views.event_edit,          name='event_edit'),
    path('events/<int:pk>/delete/',     views.event_delete,        name='event_delete'),

    # Registration
    path('events/<int:pk>/register/',   views.event_register,      name='event_register'),
    path('cancel/<int:pk>/',            views.cancel_registration,  name='cancel_registration'),

    # User dashboard
    path('my-tickets/',                 views.my_tickets,          name='my_tickets'),
    path('my-events/',                  views.my_events,           name='my_events'),

    # Sign up
    path('signup/',                     views.signup,              name='signup'),
]
