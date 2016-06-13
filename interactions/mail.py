import datetime
import hashlib
import imaplib
import logging
import re

from base64 import b64decode
from dateutil import parser
from email import policy
from email.parser import BytesParser
from email.utils import parseaddr


class MailFetcherError(Exception):
    pass


class InvalidMessageError(Exception):
    pass


class Loggable(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)


class Message(Loggable):
    """
    A crude, but simple email message class.  We assume that there's a subject
    and n attachments, and that we don't care about the message body.
    """

    def __init__(self, data):
        """
        Cribbed heavily from
        https://www.ianlewis.org/en/parsing-email-attachments-python
        """

        Loggable.__init__(self)

        self.raw = data
        self.attachments = []
        self.recipients = []

        message = BytesParser(policy=policy.default).parsebytes(self.raw)

        self.hash = hashlib.sha512(data).hexdigest()
        self.sender = parseaddr(str(message["From"]))[1].lower()
        self.subject = str(message["Subject"]).replace("\r\n", "")

        # Prefer plain text and strip everything south of the signature. Note
        # that I'm not sure what will happen here if you send an HTML-only
        # email.
        self.body = "\n\n".join(
            re.sub(r"\r?\n\r?\n-- \r?\n.*", "", str(
                message.get_body(
                    preferencelist=('plain', 'related', 'html')
                )
            ), flags=re.DOTALL).split("\n\n")[1:]
        )

        self._set_recipients(message)
        self._set_time(message)
        self._set_attachments(message)

        self.logger.info('Consuming email: "{}"'.format(self.subject))

    def __str__(self):
        return str(self.raw)

    def _set_recipients(self, message):
        """
        Each of To:, Cc:, and Bcc: can contain a list of addresses, separated
        by ",", so we first have to merge the lists as a string and then
        re-separate them on the "," to get a proper list.
        """

        recipients = [message.get("To"), message.get("Cc"), message.get("Bcc")]
        recipients = [r for r in recipients if r]
        recipients = ",".join(recipients).split(",")

        self.recipients = [parseaddr(r)[1].lower() for r in recipients]

    def _set_attachments(self, message):

        attachments = []
        for part in message.walk():

            content_disposition = part.get("Content-Disposition")
            if not content_disposition:
                continue

            dispositions = content_disposition.strip().split(";")
            if not dispositions[0].lower() == "attachment":
                if len(dispositions) == 1:
                    continue
                if "filename" not in dispositions[1].lower():
                    continue

            file_data = part.get_payload()

            attachments.append(Attachment(
                b64decode(file_data), content_type=part.get_content_type()))

        self.attachments = attachments

    def _set_time(self, message):
        self.time = datetime.datetime.now()
        message_time = message.get("Date")
        if message_time:
            try:
                self.time = parser.parse(message_time)
            except (ValueError, AttributeError):
                pass  # We assume that "now" is ok


class Attachment(object):

    def __init__(self, data, content_type):

        self.content_type = content_type
        self.data = data

    def read(self):
        return self.data


class MailFetcher(Loggable):

    def __init__(self, host, username, password, port=993, inbox="INBOX"):

        Loggable.__init__(self)

        self._connection = None
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._inbox = inbox

    def get_messages(self):

        r = []
        try:

            self._connect()
            self._login()

            for message in self._fetch():
                if message:
                    r.append(message)

            self._connection.expunge()
            self._connection.close()
            self._connection.logout()

        except Exception as e:
            self.logger.error(str(e))

        return r

    def _connect(self):
        self._connection = imaplib.IMAP4_SSL(self._host, self._port)

    def _login(self):

        login = self._connection.login(self._username, self._password)
        if not login[0] == "OK":
            raise MailFetcherError("Can't log into mail: {}".format(login[1]))

        inbox = self._connection.select("INBOX")
        if not inbox[0] == "OK":
            raise MailFetcherError("Can't find the inbox: {}".format(inbox[1]))

    def _fetch(self):
        """
        There's a (potentially annoying) problem here: as best I can tell,
        executing .fetch() on a message necessitates marking it as read.  It's
        probably worth looking into whether it's possible to preserve a
        message's unread state, but for now I'm not going to worry about it.
        """

        for num in self._connection.search(None, "ALL")[1][0].split():

            __, data = self._connection.fetch(num, "(RFC822)")

            message = None
            try:
                message = Message(data[0][1])
            except InvalidMessageError as e:
                self.logger.error(str(e))

            if message:
                yield message
