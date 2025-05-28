from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from ..models import UserProfile

AppUser = get_user_model()


class EditProfileViewTest(TestCase):
    def setUp(self):
        self.username = 'testuser1'
        self.password = 'Alltestuserspassword'
        self.email = 'newtestuseremail@email.com'
        self.user = AppUser.objects.create_user(
            username=self.username,
            password=self.password,
            email=self.email
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            bio="Test Bio"
        )

    def test_edit_profile_view_get(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('web:users:edit_profile', args=[self.user.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_profile_edit.html')

    def test_edit_profile_view_post(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.post(
            reverse('web:users:edit_profile', args=[self.user.pk]),
            {
                'first_name': 'Test',
                'last_name': 'User',
                'bio': 'Updated Bio',
                'birth_date': '1990-01-01'
            }
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('web:users:detail', args=[self.user.pk]))

        self.user.refresh_from_db()
        self.profile.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Test')
        self.assertEqual(self.user.last_name, 'User')
        self.assertEqual(self.profile.bio, 'Updated Bio')

    def test_edit_profile_view_forbidden(self):
        other_user = AppUser.objects.create_user(
            username='otheruser',
            password='otherpassword',
            email='other@email.com'
        )
        UserProfile.objects.create(user=other_user)

        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('web:users:edit_profile', args=[other_user.pk]))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('web:users:detail', args=[self.user.pk]))

        messages = list(response.wsgi_request._messages)

        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "You can only edit your own profile.")
