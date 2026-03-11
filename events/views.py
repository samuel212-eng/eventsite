#  Views — one function per page
#  Each view gets a request and returns a page

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Event, Category, Registration
from .forms import SignUpForm, EventForm, RegistrationForm

# HOME PAGE
def home(request):
    """The landing page with featured events"""
    upcoming_events = Event.objects.filter(is_published=True).order_by('date')[:6]
    categories      = Category.objects.all()
    total_events    = Event.objects.filter(is_published=True).count()
    return render(request, 'events/home.html', {
        'upcoming_events': upcoming_events,
        'categories':      categories,
        'total_events':    total_events,
    })

# EVENT LIST
def event_list(request):
    """All events, with search and category filter"""
    events     = Event.objects.filter(is_published=True)
    categories = Category.objects.all()

    # Search box
    search = request.GET.get('search', '')
    if search:
        events = events.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search) |
            Q(location__icontains=search)
        )

    # Category filter
    cat_id = request.GET.get('category', '')
    if cat_id:
        events = events.filter(category__id=cat_id)

    return render(request, 'events/event_list.html', {
        'events':            events,
        'categories':        categories,
        'search':            search,
        'selected_category': cat_id,
    })

# EVENT DETAIL
def event_detail(request, pk):
    """One event's full page"""
    event = get_object_or_404(Event, pk=pk, is_published=True)

    # Is the current user already registered?
    already_registered = False
    if request.user.is_authenticated:
        already_registered = Registration.objects.filter(
            event=event, user=request.user
        ).exists()

    return render(request, 'events/event_detail.html', {
        'event':              event,
        'already_registered': already_registered,
    })


# CREATE EVENT  (must be logged in)
@login_required
def event_create(request):
    """Page to create a new event"""
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event           = form.save(commit=False)  # Don't save yet
            event.organizer = request.user             # Attach the logged-in user
            event.save()
            messages.success(request, f'🎉 "{event.title}" has been created!')
            return redirect('event_detail', pk=event.pk)
    else:
        form = EventForm()
    return render(request, 'events/event_form.html', {'form': form, 'action': 'Create'})


# EDIT EVENT  (must be logged in + must be organizer)
@login_required
def event_edit(request, pk):
    """Page to edit an existing event"""
    event = get_object_or_404(Event, pk=pk)

    # Only the organizer can edit
    if event.organizer != request.user:
        messages.error(request, "You can only edit your own events.")
        return redirect('event_detail', pk=pk)

    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, f'✅ "{event.title}" has been updated!')
            return redirect('event_detail', pk=event.pk)
    else:
        form = EventForm(instance=event)

    return render(request, 'events/event_form.html', {'form': form, 'action': 'Edit', 'event': event})


# DELETE EVENT  (must be logged in + must be organizer)
@login_required
def event_delete(request, pk):
    """Confirm and delete an event"""
    event = get_object_or_404(Event, pk=pk)

    if event.organizer != request.user:
        messages.error(request, "You can only delete your own events.")
        return redirect('event_detail', pk=pk)

    if request.method == 'POST':
        title = event.title
        event.delete()
        messages.success(request, f'🗑️ "{title}" has been deleted.')
        return redirect('event_list')

    return render(request, 'events/event_confirm_delete.html', {'event': event})


# REGISTER FOR EVENT
@login_required
def event_register(request, pk):
    """Sign up for an event"""
    event = get_object_or_404(Event, pk=pk, is_published=True)

    # Stop double-registration
    if Registration.objects.filter(event=event, user=request.user).exists():
        messages.warning(request, "You're already registered for this event!")
        return redirect('event_detail', pk=pk)

    # Stop if event is full
    if event.is_full():
        messages.error(request, "Sorry, this event is fully booked.")
        return redirect('event_detail', pk=pk)

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            reg       = form.save(commit=False)
            reg.event = event
            reg.user  = request.user
            reg.save()
            messages.success(request, f"🎟️ You're registered for {event.title}!")
            return redirect('my_tickets')
    else:
        form = RegistrationForm()

    return render(request, 'events/event_register.html', {'form': form, 'event': event})


# MY TICKETS
@login_required
def my_tickets(request):
    """All events the logged-in user has registered for"""
    registrations = Registration.objects.filter(user=request.user).order_by('-registered_at')
    return render(request, 'events/my_tickets.html', {'registrations': registrations})

# MY EVENTS (events I organised)
@login_required
def my_events(request):
    """Events created by the logged-in user"""
    events = Event.objects.filter(organizer=request.user).order_by('-created_at')
    return render(request, 'events/my_events.html', {'events': events})

# CANCEL REGISTRATION
@login_required
def cancel_registration(request, pk):
    """Cancel a registration"""
    reg = get_object_or_404(Registration, pk=pk, user=request.user)
    if request.method == 'POST':
        event_title = reg.event.title
        reg.delete()
        messages.success(request, f"Registration for '{event_title}' has been cancelled.")
        return redirect('my_tickets')
    return render(request, 'events/cancel_confirm.html', {'registration': reg})

# SIGN UP
def signup(request):
    """New user registration page"""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)   # Log them in automatically
            messages.success(request, f"Welcome, {user.username}! 👋")
            return redirect('home')
    else:
        form = SignUpForm()

    return render(request, 'registration/signup.html', {'form': form})

