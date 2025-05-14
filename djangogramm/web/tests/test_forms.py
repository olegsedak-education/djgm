from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image as PILImage
from io import BytesIO
from ..forms import RegisterForm, LoginForm, PostForm, UserProfileForm, TagForm
from ..models import AppUser, Post, Tag


class RegisterFormTest(TestCase):
    def test_register_form_valid_data(self):
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        form = RegisterForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_register_form_invalid_data(self):
        form_data = {
            'username': 'testuser',
            'email': 'invalid-email',
            'password1': 'testpass123',
            'password2': 'differentpass'
        }
        form = RegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertIn('password2', form.errors)


class LoginFormTest(TestCase):
    def test_login_form_valid_data(self):
        form_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        form = LoginForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_login_form_invalid_data(self):
        form_data = {
            'username': '',
            'password': ''
        }
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertIn('password', form.errors)


class PostFormTest(TestCase):
    def setUp(self):
        self.user = AppUser.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.tag = Tag.objects.create(name='test')

    def test_post_form_valid_data(self):
        form_data = {
            'title': 'Test Post',
            'text': 'This is a test post',
            'tags': 'test, newtag'
        }
        form = PostForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_post_form_invalid_data(self):
        form_data = {
            'title': '',  # Пустой заголовок
            'text': 'This is a test post',
            'tags': 'test'
        }
        form = PostForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)


class UserProfileFormTest(TestCase):
    def setUp(self):
        self.user = AppUser.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )

    def test_profile_form_valid_data(self):
        form_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'bio': 'Test bio'
        }
        form = UserProfileForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid())

    def test_profile_form_invalid_data(self):
        form_data = {
            'first_name': 'Test' * 50,  # Слишком длинное имя
            'last_name': 'User',
            'bio': 'Test bio'
        }
        form = UserProfileForm(data=form_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('first_name', form.errors)


class TagFormTest(TestCase):
    def test_tag_form_valid_data(self):
        form_data = {
            'name': 'newtag'
        }
        form = TagForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_tag_form_invalid_data(self):
        form_data = {
            'name': ''  # Пустое имя тега
        }
        form = TagForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_tag_form_duplicate_name(self):
        Tag.objects.create(name='existingtag')
        form_data = {
            'name': 'existingtag'  # Дублирующееся имя тега
        }
        form = TagForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors) 