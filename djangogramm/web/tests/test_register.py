from django.core import mail
from django.test import TestCase
from django.urls import reverse

from ..forms import RegisterForm
from ..models import AppUser


class RegisterTest(TestCase):
    username = 'newtestuser1'
    email = 'newtestuseremail@email.com'
    password = 'Alltestuserspassword'

    def test_register_form(self):
        form = RegisterForm(data={'username': self.username,
                                  'email': self.email,
                                  'password1': self.password,
                                  'password2': self.password})
        self.assertTrue(form.is_valid())

    def test_successful_register(self):
        response = self.client.post(reverse('web:auth:register'),
                                    {'username': self.username,
                                     'email': self.email,
                                     'password1': self.password,
                                     'password2': self.password
                                     }
                                    )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('web:auth:login'))

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Confirm your email')
        self.assertEqual(mail.outbox[0].to, [self.email])

        email_body = mail.outbox[0].body
        self.assertIn('Confirm your email', email_body)
        self.assertIn(self.username, email_body)

        activation_link = None
        for line in email_body.split('\n'):
            if 'http://' in line:
                activation_link = line.strip()
                break
        self.assertIsNotNone(activation_link, "Activation link not found in email body")

        parts = activation_link.split('/')
        uid = parts[-3]
        token = parts[-2]

        self.assertTrue(uid, "UID is empty")
        self.assertTrue(token, "Token is empty")

        response = self.client.get(
            reverse('web:auth:complete_registration',
                    kwargs={'uid64': uid, 'token': token})
        )
        self.assertEqual(response.status_code, 302)

        user = AppUser.objects.get(username=self.username)
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_email_confirmed)

    def test_invalid_register(self):
        response = self.client.post(reverse('web:auth:register'),
                                    {'username': self.username,
                                     'email': self.email,
                                     'password1': self.password,
                                     'password2': 'wrongpassword'
                                     }
                                    )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "errorlist")
        self.assertContains(response, "password2")

    def test_register_with_invalid_email(self):
        response = self.client.post(reverse('web:auth:register'),
                                    {'username': self.username,
                                     'email': 'invalid-email',
                                     'password1': self.password,
                                     'password2': self.password
                                     }
                                    )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Enter a valid email address.')

    def test_register_with_existing_username(self):
        AppUser.objects.create_user(
            username=self.username,
            email=self.email,
            password=self.password
        )

        response = self.client.post(reverse('web:auth:register'),
                                    {'username': self.username,
                                     'email': 'another@email.com',
                                     'password1': self.password,
                                     'password2': self.password
                                     }
                                    )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'A user with that username already exists.')
