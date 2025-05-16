from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from PIL import Image as PILImage
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile

from ..models import (
    AppUser, UserProfile, Post, Image, Tag,
    PostReaction, ReactionType
)

AppUser = get_user_model()


class UserProfileViewTest(TestCase):

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

    def test_user_profile_view(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('web:users:detail', args=[self.user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "testuser1")


class FeedViewTest(TestCase):

    def setUp(self):
        self.username = 'testuser1'
        self.password = 'Alltestuserspassword'
        self.email = 'newtestuseremail@email.com'
        self.user = AppUser.objects.create_user(
            username=self.username,
            password=self.password,
            email=self.email
        )

    def test_feed_view(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('web:feed'))
        self.assertEqual(response.status_code, 200)


class PostsListViewTest(TestCase):

    def setUp(self):
        self.username = 'testuser1'
        self.password = 'Alltestuserspassword'
        self.email = 'newtestuseremail@email.com'
        self.user = AppUser.objects.create_user(
            username=self.username,
            password=self.password
        )
        self.post = Post.objects.create(
            author=self.user,
            title="Test post 1",
            text="This is a test post 1 text"
        )
        self.post = Post.objects.create(
            author=self.user,
            title="Test post 2",
            text="This is a test post 2 text"
        )

    def test_posts_list_view(self):
        response = self.client.get(reverse('web:posts:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test post 1")
        self.assertContains(response, "Test post 2")


class PostDetailViewTest(TestCase):

    def setUp(self):
        self.username = 'testuser1'
        self.password = 'Alltestuserspassword'
        self.email = 'newtestuseremail@email.com'
        self.user = AppUser.objects.create_user(
            username=self.username,
            password=self.password,
            email=self.email
        )
        self.post = Post.objects.create(
            author=self.user,
            title="Test post 1",
            text="This is a test post 1 text"
        )

    def test_post_detail_view(self):
        response = self.client.get(reverse('web:posts:detail', args=[self.post.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test post 1")
        self.assertContains(response, "This is a test post 1 text")


class CreatePostViewTest(TestCase):

    def setUp(self):
        self.username = 'testuser1'
        self.password = 'Alltestuserspassword'
        self.email = 'newtestuseremail@email.com'
        self.user = AppUser.objects.create_user(
            username=self.username,
            password=self.password,
            email=self.email
        )
        image = PILImage.new("RGB", (100, 100), color="red")
        image_content = BytesIO()
        image.save(image_content, format="JPEG")
        image_content.seek(0)
        self.image = SimpleUploadedFile(
            name="tests_image_1.jpg",
            content=image_content.read(),
            content_type="image/jpeg"
        )
        self.content = {
            'title': 'Test Post',
            'text': 'This is a test post',
            'image_urls': 'http://example.com/test.jpg'
        }

    def test_create_post_with_image(self):
        self.client.logout()
        self.client.login(username=self.username, password=self.password)
        response = self.client.post(reverse('web:posts:create'), self.content)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Post.objects.filter(title="Test Post").exists())
        self.assertTrue(Image.objects.exists())

    def test_create_post_get_request(self):
        self.client.logout()
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('web:posts:create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_post.html')


class UsersListViewTest(TestCase):

    def setUp(self):
        self.username = 'testuser1'
        self.password = 'Alltestuserspassword'
        self.email = 'newtestuseremail@email.com'
        self.admin_username = "admin"
        self.admin_password = "adminpassword"
        self.admin_email = "adminemail@mail.com"
        self.admin_user = AppUser.objects.create_user(
            username=self.admin_username,
            password=self.admin_password,
            email=self.admin_email
        )
        self.admin_user.is_staff = True
        self.admin_user.save()
        self.regular_user = AppUser.objects.create_user(
            username=self.username,
            password=self.password,
            email=self.email
        )

    def test_users_list_view_as_admin(self):
        self.client.logout()
        self.client.login(username=self.admin_username, password=self.admin_password)
        response = self.client.get(reverse('web:users:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users_list.html')

    def test_users_list_view_as_non_admin(self):
        self.client.logout()
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('web:users:list'))
        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "403 Forbidden: Access denied", status_code=403)


class EditPostViewTest(TestCase):

    def setUp(self):
        self.username = 'testuser1'
        self.password = 'Alltestuserspassword'
        self.email = 'newtestuseremail@email.com'
        self.user = AppUser.objects.create_user(
            username=self.username,
            password=self.password,
            email=self.email
        )
        self.post = Post.objects.create(
            author=self.user,
            title="Test post",
            text="This is a test post"
        )
        self.tag = Tag.objects.create(name="test")
        self.post.tags.add(self.tag)

    def test_edit_post_get_request(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(
            reverse('web:posts:edit', kwargs={'pk': self.post.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_post.html')
        self.assertContains(response, "Test post")
        self.assertContains(response, "This is a test post")
        self.assertContains(response, "test")

    def test_edit_post_with_tags(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.post(
            reverse('web:posts:edit', kwargs={'pk': self.post.pk}),
            {
                'title': 'Updated Post',
                'text': 'Updated Content',
                'tags': 'newtag1, newtag2'
            }
        )
        self.assertEqual(response.status_code, 302)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'Updated Post')
        self.assertEqual(self.post.text, 'Updated Content')
        self.assertEqual(self.post.tags.count(), 2)
        self.assertTrue(Tag.objects.filter(name='newtag1').exists())
        self.assertTrue(Tag.objects.filter(name='newtag2').exists())


class DeletePostViewTest(TestCase):

    def setUp(self):
        self.username = 'testuser1'
        self.password = 'Alltestuserspassword'
        self.email = 'newtestuseremail@email.com'
        self.user = AppUser.objects.create_user(
            username=self.username,
            password=self.password,
            email=self.email
        )
        self.post = Post.objects.create(
            author=self.user,
            title="Test post",
            text="This is a test post"
        )

    def test_delete_post(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.post(
            reverse('web:posts:delete', kwargs={'pk': self.post.pk})
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Post.objects.filter(pk=self.post.pk).exists())


class TagViewsTest(TestCase):

    def setUp(self):
        self.username = 'testuser1'
        self.password = 'Alltestuserspassword'
        self.email = 'newtestuseremail@email.com'
        self.user = AppUser.objects.create_user(
            username=self.username,
            password=self.password,
            email=self.email
        )
        self.post = Post.objects.create(
            author=self.user,
            title="Test post",
            text="This is a test post"
        )
        self.tag = Tag.objects.create(name="test")
        self.post.tags.add(self.tag)

    def test_tag_list_view(self):
        response = self.client.get(reverse('web:tags:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tag_list.html')
        self.assertContains(response, "test")

    def test_posts_by_tag_view(self):
        response = self.client.get(
            reverse('web:posts:by_tag', kwargs={'tag_name': 'test'})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'posts_list.html')
        self.assertContains(response, "Test post")


class PostReactionViewTest(TestCase):
    def setUp(self):
        self.username = 'testuser1'
        self.password = 'Alltestuserspassword'
        self.email = 'newtestuseremail@email.com'
        self.user = AppUser.objects.create_user(
            username=self.username,
            password=self.password,
            email=self.email
        )
        self.post = Post.objects.create(
            author=self.user,
            title="Test post",
            text="This is a test post"
        )

    def test_like_post(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.post(
            reverse('web:posts:like', kwargs={'pk': self.post.pk})
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            PostReaction.objects.filter(
                user=self.user,
                post=self.post,
                reaction=ReactionType.LIKE
            ).exists()
        )

    def test_unlike_post(self):
        PostReaction.objects.create(
            user=self.user,
            post=self.post,
            reaction=ReactionType.LIKE
        )

        self.client.login(username=self.username, password=self.password)
        response = self.client.post(
            reverse('web:posts:unlike', kwargs={'pk': self.post.pk})
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            PostReaction.objects.filter(
                user=self.user,
                post=self.post
            ).exists()
        )

    def test_dislike_post(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.post(
            reverse('web:posts:dislike', kwargs={'pk': self.post.pk})
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            PostReaction.objects.filter(
                user=self.user,
                post=self.post,
                reaction=ReactionType.DISLIKE
            ).exists()
        )

    def test_undislike_post(self):
        PostReaction.objects.create(
            user=self.user,
            post=self.post,
            reaction=ReactionType.DISLIKE
        )

        self.client.login(username=self.username, password=self.password)
        response = self.client.post(
            reverse('web:posts:undislike', kwargs={'pk': self.post.pk})
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            PostReaction.objects.filter(
                user=self.user,
                post=self.post
            ).exists()
        )

    def test_post_detail_with_reactions(self):
        PostReaction.objects.create(
            user=self.user,
            post=self.post,
            reaction=ReactionType.LIKE
        )

        self.client.login(username=self.username, password=self.password)
        response = self.client.get(
            reverse('web:posts:detail', kwargs={'pk': self.post.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "bi-heart-fill")
        self.assertContains(response, "1")
