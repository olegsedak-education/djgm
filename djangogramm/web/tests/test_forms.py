from unittest.mock import patch

from django.test import TestCase

from ..forms import RegisterForm, LoginForm, PostForm, UserProfileForm, TagForm
from ..models import AppUser, Tag


class RegisterFormTest(TestCase):

    def setUp(self):
        self.form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }

    def test_register_form_valid_data(self):
        form = RegisterForm(data=self.form_data)
        self.assertTrue(form.is_valid())

    def test_register_form_invalid_data(self):
        invalid_form_data = {
            'username': '_',
            'email': 'invalid-email',
            'password1': '123',
            'password2': 'differentpass'
        }
        form = RegisterForm(data=invalid_form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertIn('password2', form.errors)


class LoginFormTest(TestCase):

    def setUp(self):
        self.username = 'testuser1'
        self.password = 'Alltestuserspassword'
        self.user = AppUser.objects.create_user(username=self.username, password=self.password)

    def test_login_form_valid_data(self):
        form = LoginForm(data={'username': self.username, 'password': self.password})
        self.assertTrue(form.is_valid())

    def test_login_form_invalid_data(self):
        invalid_form_data = {
            'username': '',
            'password': ''
        }
        form = LoginForm(data=invalid_form_data)
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
        self.tag = Tag.objects.create(name='test_tag')

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
            'title': '',
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

    @patch('cloudinary.models.CloudinaryField.to_python')
    def test_profile_form_valid_data(self, mock_to_python):
        mock_to_python.return_value = 'test_avatar.jpg'
        form_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'bio': 'Test bio',
            'birth_date': '1990-01-01'
        }
        form = UserProfileForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid())

    @patch('cloudinary.models.CloudinaryField.to_python')
    def test_profile_form_invalid_data(self, mock_to_python):
        mock_to_python.return_value = 'test_avatar.jpg'
        form_data = {
            'first_name': 'Test' * 50,
            'last_name': 'User',
            'bio': 'Test bio'
        }
        form = UserProfileForm(data=form_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('first_name', form.errors)

    @patch('cloudinary.models.CloudinaryField.to_python')
    def test_profile_form_with_avatar(self, mock_to_python):
        mock_to_python.return_value = 'test_avatar.jpg'
        from django.core.files.uploadedfile import SimpleUploadedFile
        from PIL import Image
        import io

        file = io.BytesIO()
        image = Image.new('RGB', (100, 100), 'white')
        image.save(file, 'png')
        file.name = 'test.png'
        file.seek(0)

        form_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'bio': 'Test bio',
            'birth_date': '1990-01-01',
            'avatar': SimpleUploadedFile(
                name='test.png',
                content=file.read(),
                content_type='image/png'
            )
        }
        form = UserProfileForm(
            data=form_data,
            files={'avatar': form_data['avatar']},
            user=self.user
        )
        self.assertTrue(form.is_valid())


class TagFormTest(TestCase):
    def setUp(self):
        self.user = AppUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_tag_form_valid_data(self):
        form_data = {
            'name': 'newtag'
        }
        form = TagForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_tag_form_invalid_data(self):
        form_data = {
            'name': ''
        }
        form = TagForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_tag_form_duplicate_name(self):
        Tag.objects.create(name='existingtag')
        form_data = {
            'name': 'existingtag'
        }
        form = TagForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_post_form_with_tags(self):
        form_data = {
            'title': 'Test Post',
            'text': 'Test Content',
            'tags': 'tag1, tag2, tag3'
        }
        form = PostForm(data=form_data)
        self.assertTrue(form.is_valid())
        post = form.save(commit=False)
        post.author = self.user
        post.save()
        form.save()

        self.assertEqual(post.tags.count(), 3)
        self.assertTrue(Tag.objects.filter(name='tag1').exists())
        self.assertTrue(Tag.objects.filter(name='tag2').exists())
        self.assertTrue(Tag.objects.filter(name='tag3').exists())

    def test_post_form_empty_tags(self):
        form_data = {
            'title': 'Test Post',
            'text': 'Test Content',
            'tags': ''
        }
        form = PostForm(data=form_data)
        self.assertTrue(form.is_valid())
        post = form.save(commit=False)
        post.author = self.user
        post.save()
        form.save()

        self.assertEqual(post.tags.count(), 0)
