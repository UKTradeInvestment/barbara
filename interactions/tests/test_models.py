from django.test import TestCase

from contacts.models import ExternalContact, UserContact
from users.models import User

from ..models import EmailInteraction


class EmailInteractionTestCase(TestCase):

    def test_is_relevant(self):
        UserContact.objects.create(user=User.objects.create(
            name="Test User 0",
            email="test0@example.ca"
        ))
        ExternalContact.objects.create(
            name="Test User 1",
            email="test1@example.ca"
        )
        self.assertTrue(EmailInteraction.is_relevant(
            "test0@example.ca", "test1@example.ca"))
        self.assertTrue(EmailInteraction.is_relevant(
            "test1@example.ca", "test0@example.ca"))
        self.assertFalse(EmailInteraction.is_relevant(
            "test2@example.ca", "test3@example.ca"))
        self.assertFalse(EmailInteraction.is_relevant(
            "test0@example.ca", "test0@example.ca"))
        self.assertFalse(EmailInteraction.is_relevant(
            "test1@example.ca", "test1@example.ca"))
