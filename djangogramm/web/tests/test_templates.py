from django.test import TestCase, Client
from django.urls import reverse
from ..models import AppUser, Post, Tag, PostReaction, ReactionType, Following


class TemplateTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = AppUser.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.post = Post.objects.create(
            author=self.user,
            title='Test Post',
            text='Test Content'
        )
        self.tag = Tag.objects.create(name='test')
        self.post.tags.add(self.tag)

    def test_base_template(self):
        response = self.client.get(reverse('web:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base.html')

    def test_post_detail_template(self):
        response = self.client.get(
            reverse('web:posts:detail', kwargs={'pk': self.post.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'post_detail.html')
        self.assertContains(response, 'Test Post')
        self.assertContains(response, 'Test Content')
        self.assertContains(response, 'test')

    def test_post_detail_with_reactions(self):
        PostReaction.objects.create(
            user=self.user,
            post=self.post,
            reaction=ReactionType.LIKE
        )
        
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(
            reverse('web:posts:detail', kwargs={'pk': self.post.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'bi-heart-fill')
        self.assertContains(response, '1')

    def test_tag_list_template(self):
        response = self.client.get(reverse('web:tags:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tag_list.html')
        self.assertContains(response, 'test')

    def test_posts_by_tag_template(self):
        response = self.client.get(
            reverse('web:posts:by_tag', kwargs={'tag_name': 'test'})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'posts_list.html')
        self.assertContains(response, 'Test Post')

    def test_user_profile_template(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(
            reverse('web:users:detail', kwargs={'pk': self.user.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_profile.html')
        self.assertContains(response, 'testuser')

    def test_feed_template(self):
        Following.objects.create(
            user=self.user,
            following_user=self.user
        )
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('web:feed'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'feed.html')
        self.assertContains(response, 'Test Post') 