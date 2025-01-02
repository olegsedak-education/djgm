from django.test import TestCase
from ..forms import RegisterForm
from ..models import AppUser
from django.urls import reverse


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
        response = self.client.post(reverse('register'),
                                    {'username': self.username,
                                      'email':self.email,
                                      'password1': self.password,
                                      'password2': self.password
                                    }
                                    )
        self.assertEqual(response.status_code,302)
        self.assertRedirects(response, reverse('home'))


    def test_invalid_register(self):
        response = self.client.post(reverse('register'),
                                    {'username': self.username,
                                      'email':self.email,
                                      'password1': self.password,
                                      'password2': 'wrongpassword'
                                    }
                                    )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'The two password fields didn’t match.')
