from django.test import TestCase

from contacts.models import ExternalContact, UserContact
from users.models import User

from ..models import PhoneInteraction, MeetingInteraction, EmailInteraction


class ModelsTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            name="Test User 0", email="test0@example.ca")
        self.user_contact = UserContact.objects.create(user=self.user)
        self.external_contact = ExternalContact.objects.create(
            name="Test User 1", email="test1@example.ca")

    def test_is_relevant(self):
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

    def test_phone_inheritance(self):
        self._test_voice_inheritance(PhoneInteraction)

    def test_meeting_inheritance(self):
        self._test_voice_inheritance(MeetingInteraction)

    def _test_voice_inheritance(self, klass):

        interaction = klass.objects.create(
            subject="Test Subject", notes="These are notes")

        self.assertTrue(hasattr(interaction, "attendees"))
        self.assertTrue(hasattr(interaction, "attendees_string"))
        self.assertTrue(hasattr(interaction, "subject"))
        self.assertTrue(hasattr(interaction, "notes"))

    def test_phone_attendee_string_generation(self):
        self._test_attendee_string_generation(PhoneInteraction)

    def test_meeting_attendee_string_generation(self):
        self._test_attendee_string_generation(MeetingInteraction)

    def _test_attendee_string_generation(self, klass):

        interaction = klass.objects.create(
            subject="Test Subject", notes="These are notes")

        interaction.attendees.add(self.user_contact)
        interaction.attendees.add(self.external_contact)

        self.assertEqual(interaction.attendees.all().count(), 2)
        self.assertEqual(
            interaction.attendees_string, "Test User 0, Test User 1")
