from django.apps import AppConfig
from django.db.models.signals import m2m_changed


class InteractionsConfig(AppConfig):

    name = "interactions"

    def ready(self):

        from .models import MeetingInteraction, PhoneInteraction
        from .signals.handlers import set_attendees_string

        m2m_changed.connect(
            set_attendees_string, sender=PhoneInteraction.attendees.through)
        m2m_changed.connect(
            set_attendees_string, sender=MeetingInteraction.attendees.through)

        AppConfig.ready(self)
