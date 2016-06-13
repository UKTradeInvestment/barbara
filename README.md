# UKTI Barbara

Barbara is a passive archival system, collecting all the interaction data it
can find, storing it in a structured system for easy retrieval and statistics
generation.  Maybe one day it'll have fancy charts!


## Installation

It's your standard Django project, so:

1. `virtualenv --python python3 ${HOME}/.virtualenvs/barbara`
2. `. ${HOME}/.virtualenvs/barbara/bin/activate`
3. `cd /path/to/barbara`
4. `pip install --requirement requirements.txt`
5. `./manage.py migrate`

## Using It

There's two parts to Barbara: the web server, and the mail monitor.

### Dummy Data

In order to be able to see something, you'll probably want some dummy data in
the system to start.  The following code snippet will create you two users:
your test user and your personal account, and then backfill the interaction
history between you two with four different events:

```python
from datetime import datetime
from django.utils import timezone
from users.models import User
from contacts.models import UserContact, ExternalContact
from interactions.models import PhoneInteraction, MeetingInteraction

test = UserContact.objects.create(user=User.objects.create(
    name="Barbara Gordon", email="test-account@somewhere.ca"))
me = ExternalContact.objects.create(
    name="My Name", email="my.name@digital.bis.gov.uk")

p1 = PhoneInteraction.objects.create(
    subject="Let's talk about comic books!",
    notes="Barbara Gordon is pretty awesome."
)
p1.attendees.add(me, test)
p1.created = timezone.make_aware(datetime(2016, 6, 8, 14, 22))
p1.save()

p2 = PhoneInteraction.objects.create(
    subject="Conference call regarding CORE",
    notes="Headaches for everyone!"
)
p2.attendees.add(me, test)
p2.created = timezone.make_aware(datetime(2016, 6, 9, 14, 38))
p2.save()

m1 = MeetingInteraction.objects.create(
    subject="Lunch Break",
    notes="Talked about how green the grass was"
)
m1.attendees.add(me, test)
m1.created = timezone.make_aware(datetime(2016, 6, 8, 13, 46))
m1.save()

m2 = MeetingInteraction.objects.create(
    subject="Movie Night",
    notes="Marvel > DC"
)
m2.attendees.add(me, test)
m2.created = timezone.make_aware(datetime(2016, 6, 8, 18, 58))
m2.save()
```

### Web Server

It's your typical Django web server.  Start it with `./manage.py runserver` and
you're good to go.

### Mail Monitor

The monitor is run by way of a management command with two options: `poll` and
`stdin`.  The `poll` option tells Barbara to poll a mail account every minute
forever, looking for juicy new emails, while the `stdin` option tells her to
parse a single email as standard in.  The former is handy for monitoring a
single email account, while the latter is handy if you want to shunt a bunch
of emails to a process.  Just call `./manage.py monitor <poll|stdin>`.

Note however that the `stdin` option doesn't make a lot of sense at scale.
Rather, you should have a process that dumps mail into a queue server and then
modify Barbara to consume individual messages from the queue in an infinite
loop.  The code for the `stdin` method would server as a good starting point
for this.

One more note about the `poll` option.  Running it at first will likely
complain with:

> **CommandError: Mail server settings are not defined**

That's because Barbara assumes the following variables are in the environment
when it runs:

    POLLING_HOST="mail.somemailserver.ca"
    POLLING_USERNAME="some_login_name"
    POLLING_PASSWORD="some_password"

Set those to your test account and you're good to go.  Here's your
step-by-step:

1. Use the Django shell to create two users in your database: one for your test
   account, and another for your personal account (from which you'll be sending
   a message to the test account)
2. Start the web server
3. Start the monitor (with `poll`)
4. Open your browser and visit http://localhost:8000/
5. Send an email to your test account.
6. Watch it pop up in your web browser, freshly consumed by the monitor.

## Colophon

But why *"Barbara"*? What better name for an archival system that Monitors All
The Things than that of [Barbara Gordon](https://en.wikipedia.org/wiki/Barbara_Gordon),
aka *Oracle*?
