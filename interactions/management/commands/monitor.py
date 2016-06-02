import logging
import sys
import time

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q

from contacts.models import Contact
from interactions.models import EmailInteraction
from interactions.mail import MailFetcher, Message


class Command(BaseCommand):

    help = ("Monitors an email account through polling, capturing relevant "
            "data into our database.")
    
    def __init__(self, *args, **kwargs):

        self.logger = logging.getLogger(__name__)

        BaseCommand.__init__(self, *args, **kwargs)

        self.username = settings.MAIL_POLLING["username"]
        self.password = settings.MAIL_POLLING["password"]
        self.host = settings.MAIL_POLLING["host"]

    def add_arguments(self, parser):
        parser.add_argument("role", type=str, choices=("poll", "stdin"))

    def handle(self, *args, **options):
        getattr(self, "_handle_{}".format(options["role"]))()

    def _handle_poll(self):

        if not self.host or not self.username or not self.password:
            raise CommandError("Mail server settings are not defined")

        self.logger.debug("Starting polling")

        fetcher = MailFetcher(self.host, self.username, self.password)

        while True:

            # Collect the messages
            messages = list(fetcher.get_messages())

            # Strip out those we already have
            already_consumed = list(EmailInteraction.objects.filter(
                hash__in=[m.hash for m in messages]
            ).values_list("hash", flat=True))
            messages = [m for m in messages if m.hash not in already_consumed]

            for message in messages:
                self._process_message(message)

            time.sleep(10)

    def _handle_stdin(self):
        self.logger.debug("Starting standard-in handling")
        self._process_message(Message(bytes(sys.stdin.read(), "utf-8")))

    @staticmethod
    def _process_message(message):

        for recipient in message.recipients:

            if not EmailInteraction.is_relevant(message.sender, recipient):
                continue

            EmailInteraction.objects.create(
                hash=message.hash,
                sender=Contact.objects.get(
                    Q(externalcontact__email=message.sender) |
                    Q(usercontact__user__email=message.sender)
                ),
                recipient=Contact.objects.get(
                    Q(externalcontact__email=recipient) |
                    Q(usercontact__user__email=recipient)
                ),
                subject=message.subject,
                body=message.body,
                raw=str(message.raw, "utf-8")
            )
