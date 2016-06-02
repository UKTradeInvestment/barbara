import os

from django.conf import settings
from django.test import TestCase

from ..mail import Message


class MessageTestCase(TestCase):

    def __init__(self, *args, **kwargs):

        TestCase.__init__(self, *args, **kwargs)

        sample = os.path.join(
            settings.BASE_DIR, "interactions", "tests", "sample.mail")

        with open(sample, "rb") as f:
            self.sample = f.read()

    def test_set_recipients(self):
        message = Message(self.sample)
        self.assertEqual(len(message.recipients), 3)
