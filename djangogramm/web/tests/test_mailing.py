from django.core import mail
from django.test import TestCase


class EmailSendingTests(TestCase):
    def test_send_simple_email(self):
        self.assertEqual(len(mail.outbox), 0)

        mail.send_mail(
            subject='Test Subject',
            message='Test message body',
            from_email='from@example.com',
            recipient_list=['to@example.com'],
        )

        self.assertEqual(len(mail.outbox), 1)

        email = mail.outbox[0]

        self.assertEqual(email.subject, 'Test Subject')
        self.assertEqual(email.body, 'Test message body')
        self.assertEqual(email.from_email, 'from@example.com')
        self.assertEqual(email.to, ['to@example.com'])
