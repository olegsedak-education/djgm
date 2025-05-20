from django.test import TestCase
from django.urls import reverse, resolve

from web import views


class URLTests(TestCase):

    def test_login_url_resolves(self):
        url = reverse('web:auth:login')
        match = resolve(url)
        self.assertEqual(match.func, views.sign_in)

    def test_profile_edit_url_resolves(self):
        test_pk = 1
        url = reverse('web:users:edit_profile', kwargs={'pk': test_pk})
        match = resolve(url)
        self.assertEqual(match.func, views.edit_profile)

    def test_404_handler(self):
        response = self.client.get('/nonexistent-page')
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'Not Found', response.content)

    def test_logout_redirects(self):
        url = reverse('web:auth:logout')
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')
