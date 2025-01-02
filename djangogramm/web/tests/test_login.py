from django.test import TestCase
from ..forms import LoginForm
from ..models import AppUser
from django.urls import reverse


class LogInTest(TestCase):

    def setUp(self):
        self.username = 'testuser1'
        self.password = 'Alltestuserspassword'
        self.user = AppUser.objects.create_user(username=self.username, password=self.password)


    def test_login_form(self):
        form = LoginForm(data={'username': self.username, 'password': self.password})
        self.assertTrue(form.is_valid())


    def test_successful_login(self):
        response = self.client.post(reverse('login'), {'username': self.username, 'password': self.password})
        self.assertEqual(response.status_code,302)
        self.assertRedirects(response, reverse('home'))


    def test_invalid_login(self):
        response = self.client.post(reverse('login'), {'username': self.username, 'password': 'wrongtestpassword'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid username or password')
