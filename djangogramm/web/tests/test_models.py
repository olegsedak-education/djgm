from django.test import TestCase
from datetime import date, timedelta
from django.utils import timezone


from ..models import *

NUMBER_OF_USERS = 5


class AppUserModelTest(TestCase):


    def setUp(self):
        self.users = []
        for number in range(1, NUMBER_OF_USERS+1):
            username = f"test_user{number}"
            password = f"{number}testuserspassword"
            email = f"{number}testusermail@mail.com"
            user = AppUser.objects.create_user(
                username=username,
                password=password,
                email=email
            )
            self.users.append(user)

    def test_users_creation(self):
        for number, user in enumerate(self.users, 1):
            self.assertEqual(user.username, f"test_user{number}")
            self.assertEqual(user.email, f"{number}testusermail@mail.com")
            self.assertTrue(user.check_password(f"{number}testuserspassword"))


    def test_user_str_method(self):
        for number, user in enumerate(self.users, 1):
            self.assertEqual(str(user), f"test_user{number}")


class UserProfileModelTest(TestCase):

    def setUp(self):
        self.users = []
        self.profiles = []
        for number in range(1, NUMBER_OF_USERS+1):
            username = f"test_user{number}"
            password = f"{number}testuserspassword"
            email = f"{number}testusermail@mail.com"
            user = AppUser.objects.create_user(
                username=username,
                password=password,
                email=email
            )
            self.users.append(user)
            profile = UserProfile.objects.create(
                user=user,
                birth_date=date(1990+number, number, number),
                bio=f"Bio for {user.username}"
            )
            self.profiles.append(profile)


    def test_user_profile_creation(self):
        for number, profile in enumerate(self.profiles, 1):
            self.assertEqual(profile.user.username, f"test_user{number}")
            self.assertEqual(profile.birth_date, date(1990+number, number, number)),
            self.assertEqual(profile.bio, f"Bio for test_user{number}")


    def test_user_profile_str_method(self):
        for number, profile in enumerate(self.profiles, 1):
            self.assertEqual(str(profile), f"test_user{number} profile")


class PostModelTest(TestCase):

    def setUp(self):
        self.user = AppUser.objects.create_user(
            username="test_user",
            password="test_password",
            email="testusermail@mail.com"
        )
        self.post = Post.objects.create(
            author=self.user,
            title="Test post",
            text="This is a test post",
            published=True
        )

    def test_post_create(self):
        self.assertEqual(self.post.author.username, "test_user")
        self.assertEqual(self.post.title, "Test post")
        self.assertEqual(self.post.text, "This is a test post")
        self.assertTrue(self.post.published)


class ImageModelTest(TestCase):

    def setUp(self):
        self.image = Image.objects.create(image="djangogramm/images_for_test/imgfortest.jpg")


    def test_image_creation(self):
        self.assertEqual(self.image.image.name, "djangogramm/images_for_test/imgfortest.jpg")


    def test_uploadede_at_auto_now_add(self):
        self.assertIsNotNone(self.image.uploadede_at)
        self.assertAlmostEqual(self.image.uploadede_at, timezone.now(), delta=timedelta(seconds=1))


    def test_image_str_method(self ):
        self.assertEqual(str(self.image), "/media/djangogramm/images_for_test/imgfortest.jpg")


class CommentModelTest(TestCase):

    def setUp(self):
        self.user = AppUser.objects.create_user(
            username="test_user",
            password="test_password",
            email="testusermail@mail.com"
        )
        self.post = Post.objects.create(
            author=self.user,
            title="Test post",
            text="This is a test post",
            published=True
        )
        self.comment = Comment.objects.create(
            author=self.user,
            post=self.post,
            text="This is a test comment"
        )

    def test_comment_creation(self):
        self.assertEqual(self.comment.author.username, "test_user")
        self.assertEqual(self.comment.post.text, "This is a test post")
        self.assertEqual(self.comment.text, "This is a test comment")


    def test_comment_str_method(self):
        self.assertEqual(str(self.comment), "This is a test comment, test_user, Test post")


class PostRectionModelTest(TestCase):

    def setUp(self):
        self.user = AppUser.objects.create_user(
            username="test_user",
            password="test_password",
            email="testusermail@mail.com"
        )
        self.post = Post.objects.create(
            author=self.user,
            title="Test post",
            text="This is a test post",
            published=True
        )
        self.post_reaction = PostReaction.objects.create(
            user=self.user,
            post=self.post,
            reaction=ReactionType.LIKE
        )

    def test_post_reaction_creation(self):
        self.assertEqual(self.post_reaction.user.username, "test_user")
        self.assertEqual(self.post_reaction.post.title, "Test post")
        self.assertEqual(self.post_reaction.reaction, ReactionType.LIKE)


    def test_get_reaction_type(self):
        self.assertEqual(self.post_reaction.get_reaction_type(), "Like")


    def test_post_reaction_str_method(self):
        self.assertEqual(str(self.post_reaction), "PostReaction: Like by test_user on Test post")


class CommentRectionModelTest(TestCase):

    def setUp(self):
        self.user = AppUser.objects.create_user(
            username="test_user",
            password="test_password",
            email="testusermail@mail.com"
        )
        self.post = Post.objects.create(
            author=self.user,
            title="Test post",
            text="This is a test post",
            published=True
        )
        self.comment = Comment.objects.create(
            author=self.user,
            post=self.post,
            text="This is a test comment"
        )
        self.comment_reaction = CommentReaction.objects.create(
            user=self.user,
            comment=self.comment,
            reaction=ReactionType.LIKE
        )

    def test_comment_reaction_creation(self):
        self.assertEqual(self.comment_reaction.user.username, "test_user")
        self.assertEqual(self.comment_reaction.comment.text, "This is a test comment")
        self.assertEqual(self.comment_reaction.reaction, ReactionType.LIKE)


    def test_get_reaction_type(self):
        self.assertEqual(self.comment_reaction.get_reaction_type(), "Like")


    def test_post_reaction_str_method(self):
        self.assertEqual(str(self.comment_reaction),
                         "CommentReaction: Like by test_user on This is a test comment")


class TestTagModel(TestCase):

    def setUp(self):
        self.user = AppUser.objects.create_user(
            username="test_user",
            password="test_password"
        )
        self.post = Post.objects.create(
            author=self.user,
            title="Test post",
            text="This is a test post",
            published=True
        )
        self.tag = Tag.objects.create(
            name = "test tag name",
            post=self.post
        )


    def test_tag_creation(self):
        self.assertEqual(self.tag.name, "test tag name")
        self.assertEqual(self.tag.post.title , "Test post")


    def test_tag_str_method(self):
        self.assertEqual(str(self.tag), "test tag name")
