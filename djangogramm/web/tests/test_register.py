from django.test import TestCase
from django.core import mail
from django.urls import reverse
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
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
        self.assertRedirects(response, reverse('web:home'))
        
        # Проверяем, что письмо было отправлено
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Confirm your email')
        self.assertEqual(mail.outbox[0].to, [self.email])
        
        # Проверяем содержимое письма
        email_body = mail.outbox[0].body
        self.assertIn('Confirm your email', email_body)
        self.assertIn(self.username, email_body)
        
        # Получаем ссылку подтверждения из письма
        confirmation_link = email_body.split('https://')[1].split('\n')[0]
        uid = confirmation_link.split('/')[-2]
        token = confirmation_link.split('/')[-1]
        
        # Проверяем подтверждение регистрации
        response = self.client.get(
            reverse('web:auth:complete_registration', 
                   kwargs={'uid64': uid, 'token': token})
        )
        self.assertEqual(response.status_code, 302)
        
        # Проверяем, что пользователь активирован
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
        self.assertContains(response, 'The two password fields didn't match.')

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
        # Создаем пользователя
        AppUser.objects.create_user(
            username=self.username,
            email=self.email,
            password=self.password
        )
        
        # Пытаемся зарегистрировать пользователя с тем же именем
        response = self.client.post(reverse('web:auth:register'),
                                    {'username': self.username,
                                      'email': 'another@email.com',
                                      'password1': self.password,
                                      'password2': self.password
                                    }
                                    )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'A user with that username already exists.')
