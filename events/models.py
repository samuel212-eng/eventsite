# =============================================
#  Models — these become our database tables
#  Each class = one table, each field = one column
# =============================================

from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    """A category like: Music, Tech, Sports, Art"""
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class Event(models.Model):
    """One event listing on the site"""

    # Basic info
    title       = models.CharField(max_length=200)
    description = models.TextField()
    category    = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)

    # Date and place
    date     = models.DateTimeField()
    location = models.CharField(max_length=300)

    # Optional banner image
    image = models.ImageField(upload_to='events/', blank=True, null=True)

    # Tickets
    price    = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    capacity = models.PositiveIntegerField(default=100)

    # Who created this event and when
    organizer  = models.ForeignKey(User, on_delete=models.CASCADE, related_name='my_events')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Is it published for everyone to see?
    is_published = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    def spots_left(self):
        """How many tickets are still available?"""
        booked = self.registrations.count()
        return self.capacity - booked

    def is_full(self):
        return self.spots_left() <= 0

    class Meta:
        ordering = ['date']   # Newest dates first


class Registration(models.Model):
    """A user signing up for an event"""

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    user  = models.ForeignKey(User, on_delete=models.CASCADE, related_name='my_registrations')

    registered_at = models.DateTimeField(auto_now_add=True)

    # Extra info collected at registration
    phone   = models.CharField(max_length=20, blank=True)
    message = models.TextField(blank=True, help_text="Any special requests?")

    def __str__(self):
        return f"{self.user.username} → {self.event.title}"

    class Meta:
        # A person can only register once per event
        unique_together = ('event', 'user')
