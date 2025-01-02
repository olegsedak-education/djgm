from pathlib import Path
from django.conf import settings
from faker import Faker
from django.core.management.base import BaseCommand
from PIL import Image as PILImage
import random
from web.models import AppUser, UserProfile, Post, Image


fake = Faker()

IMAGE_DIR = settings.IMAGE_DIR
MEDIA_ROOT = settings.MEDIA_ROOT

NUMBER_OF_TEST_USERS = 3
MAX_TEST_IMAGES = 5
MAX_IMAGE_SIZE = (1600, 1600)
MIN_POSTS_PER_USER = 1
MAX_POSTS_PER_USER = 5
MIN_IMAGES_PER_POST = 1
MAX_IMAGES_PER_POST = 5
IMAGE_FILE_EXTENSIONS = ['.jpg', '.jpeg', '.png']
TEST_IMAGES_DIR = Path('images_for_test')
PASSWORD_FOR_ALL_FAKE_USERS = 'Alltestuserspassword'


def generate_unique_usernames(number_of_users):
    usernames = set()
    while len(usernames) <= number_of_users:
        username = fake.user_name()
        usernames.add(username)
    return usernames


def get_random_test_images():
    all_images_in_image_dir = [f for f in TEST_IMAGES_DIR.iterdir() if f.suffix in IMAGE_FILE_EXTENSIONS]

    if not all_images_in_image_dir:
        print(f"No test images found in the directory {TEST_IMAGES_DIR}")
        return []
    max_images_to_get = MAX_TEST_IMAGES if len(all_images_in_image_dir) >= MAX_TEST_IMAGES else all_images_in_image_dir
    return random.sample(all_images_in_image_dir, max_images_to_get)


def optimize_image_convert_to_webp_and_save_at_new_path(image_path):
    img = PILImage.open(image_path)
    img.thumbnail(MAX_IMAGE_SIZE,PILImage.LANCZOS)
    webp_image_name = image_path.with_suffix('.webp').name
    webp_image_path = Path(IMAGE_DIR) / webp_image_name
    img.save(webp_image_path, 'webp', quality=85)
    return webp_image_path


def create_fake_records_in_db():
    usernames = generate_unique_usernames(NUMBER_OF_TEST_USERS)
    for username in usernames:
        user = AppUser.objects.create_user(
            username=username,
            email=fake.email(),
            password=PASSWORD_FOR_ALL_FAKE_USERS
        )
        profile = UserProfile.objects.create(
            user=user,
            bio=fake.text(max_nb_chars=100),
            birth_date=fake.date_of_birth(minimum_age=18)
        )
        print(f"User {username}  created")

    users = AppUser.objects.all()
    test_images = get_random_test_images()

    for user in users:
        number_of_posts = random.randint(MIN_POSTS_PER_USER, MAX_POSTS_PER_USER)
        for _ in range(number_of_posts+1):
            post = Post.objects.create(
                title=fake.sentence(),
                text=fake.sentence(),
                author=user
            )
            number_of_images = random.randint(MIN_IMAGES_PER_POST, MAX_IMAGES_PER_POST)
            for _ in  range(number_of_images+1):
                image_path = random.choice(test_images)
                webp_image_path = optimize_image_convert_to_webp_and_save_at_new_path(image_path)
                image = Image.objects.create(
                    image=webp_image_path.relative_to(MEDIA_ROOT).as_posix()
                )
                post.images.add(image)
                print(f"Image for post {post.id} created: {image}")


class Command(BaseCommand):
    help = 'Fill database with fake data'

    def handle(self, *args, **kwargs):
        create_fake_records_in_db()
        self.stdout.write(self.style.SUCCESS('Database filled with fake data successfully!'))
