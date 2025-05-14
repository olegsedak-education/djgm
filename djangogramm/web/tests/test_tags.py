from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.db import models
from ..models import Post, Tag
from ..forms import PostForm

User = get_user_model()


class TagModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.post = Post.objects.create(
            author=self.user,
            title='Test Post',
            text='Test Content'
        )
        self.tag = Tag.objects.create(name='test')

    def test_tag_creation(self):
        """Тест создания тега"""
        self.assertEqual(self.tag.name, 'test')
        self.assertTrue(isinstance(self.tag, Tag))
        self.assertEqual(str(self.tag), 'test')

    def test_tag_unique_name(self):
        """Тест уникальности имени тега"""
        with self.assertRaises(Exception):
            Tag.objects.create(name='test')

    def test_tag_post_relationship(self):
        """Тест связи тега с постом"""
        self.post.tags.add(self.tag)
        self.assertEqual(self.post.tags.count(), 1)
        self.assertEqual(self.tag.posts.count(), 1)
        self.assertEqual(self.tag.posts.first(), self.post)


class TagFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_post_form_with_tags(self):
        """Тест формы поста с тегами"""
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
        form.save()  # Сохраняем теги

        self.assertEqual(post.tags.count(), 3)
        self.assertTrue(Tag.objects.filter(name='tag1').exists())
        self.assertTrue(Tag.objects.filter(name='tag2').exists())
        self.assertTrue(Tag.objects.filter(name='tag3').exists())

    def test_post_form_empty_tags(self):
        """Тест формы поста с пустыми тегами"""
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


class TagViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        self.post = Post.objects.create(
            author=self.user,
            title='Test Post',
            text='Test Content'
        )
        self.tag = Tag.objects.create(name='test')
        self.post.tags.add(self.tag)

    def test_tag_list_view(self):
        """Тест представления списка тегов"""
        response = self.client.get(reverse('web:tags:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tag_list.html')
        self.assertContains(response, 'test')

    def test_posts_by_tag_view(self):
        """Тест представления постов по тегу"""
        response = self.client.get(
            reverse('web:posts:by_tag', kwargs={'tag_name': 'test'})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'posts_list.html')
        self.assertContains(response, 'Test Post')

    def test_create_post_with_tags(self):
        """Тест создания поста с тегами"""
        response = self.client.post(
            reverse('web:posts:create'),
            {
                'title': 'New Post',
                'text': 'New Content',
                'tags': 'newtag1, newtag2'
            }
        )
        self.assertEqual(
            response.status_code, 302
        )  # Редирект после успешного создания
        post = Post.objects.get(title='New Post')
        self.assertEqual(post.tags.count(), 2)
        self.assertTrue(Tag.objects.filter(name='newtag1').exists())
        self.assertTrue(Tag.objects.filter(name='newtag2').exists())

    def test_edit_post_tags(self):
        """Тест редактирования тегов поста"""
        response = self.client.post(
            reverse('web:posts:edit', kwargs={'pk': self.post.pk}),
            {
                'title': 'Updated Post',
                'text': 'Updated Content',
                'tags': 'updatedtag1, updatedtag2'
            }
        )
        self.assertEqual(
            response.status_code, 302
        )  # Редирект после успешного обновления
        self.post.refresh_from_db()
        self.assertEqual(self.post.tags.count(), 2)
        self.assertTrue(Tag.objects.filter(name='updatedtag1').exists())
        self.assertTrue(Tag.objects.filter(name='updatedtag2').exists()) 