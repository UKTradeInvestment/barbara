from django.db import models
from django.db.models import Q

from polymorphic.models import PolymorphicModel

from contacts.models import Contact


class Interaction(PolymorphicModel):

    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return str(self.created)


class EmailInteraction(Interaction):

    hash = models.CharField(max_length=128, unique=True)

    sender = models.ForeignKey(Contact, related_name="emails_sent")
    recipient = models.ForeignKey(Contact, related_name="emails_received")

    subject = models.CharField(max_length=256)
    body = models.TextField()
    raw = models.TextField()

    def __str__(self):
        return "Email from {} to {}, {}".format(
            self.sender,
            self.recipient,
            self.created
        )

    @staticmethod
    def is_relevant(*addresses):
        """
        Return True if both the sender and recipient have records as Contacts.
        """
        return len(set(Contact.objects.filter(
            Q(externalcontact__email__in=addresses) |
            Q(usercontact__user__email__in=addresses)
        ).values_list(
            "externalcontact__email",
            "usercontact__user__email"
        ))) == 2
