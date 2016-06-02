from django.db import models

from polymorphic.models import PolymorphicModel

from users.models import User


class Contact(PolymorphicModel):
    pass


class UserContact(Contact):

    user = models.ForeignKey(User, blank=True, null=True)

    def __str__(self):
        return self.name

    @property
    def name(self):
        return self.user.name

    @property
    def email(self):
        return self.user.email


class ExternalContact(Contact):

    def __str__(self):
        return self.name

    name = models.EmailField()
    email = models.EmailField()
