from datetime import datetime

from django.db import models

from .base import Party, PartyRepresentative

COMMUNICATION_MEDIA = (
    ("Phone", "Phone"),
    ("Email", "Email"),
    ("SMS", "SMS"),
    ("Visit", "Visit"),
)

COMMUNICATION_STATUSES = (
    ("Preparing", "Preparing"),
    ("Could not Connect", "Could not Connect"),
    ("No Response", "No Response"),
    ("Could not talk to authority", "Could not talk to authority"),
    ("Waiting for Reply", "Waiting for Reply"),
    ("Follow Up", "Follow Up"),
    ("Fail", "Fail"),
    ("Success", "Success"),
)


class CommunicationLog(models.Model):
    party = models.ForeignKey(Party, related_name="communication_logs", on_delete=models.PROTECT)
    representative = models.ForeignKey(PartyRepresentative, related_name="communication_logs", on_delete=models.PROTECT, blank=True, null=True)
    date_time = models.DateTimeField(default=datetime.now)
    medium = models.CharField(choices=COMMUNICATION_MEDIA, default=COMMUNICATION_MEDIA[0][0], max_length=255)
    outbound = models.BooleanField(default=True)
    follow_up = models.DateTimeField(blank=True, null=True)
    followed_up = models.BooleanField(default=False)
    status = models.CharField(choices=COMMUNICATION_STATUSES, max_length=255)
    transcript = models.TextField(blank=True, null=True)
