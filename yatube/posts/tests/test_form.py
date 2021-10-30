import shutil
import tempfile
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Group, Post, Comment

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateEditFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_author')
        cls.group = Group.objects.create(
            title='TestGroup1',
            slug='TestGroup1',
            description='TestGroup1'
        )
        cls.test_post = Post.objects.create(
            text='Тест №0',
            group=cls.group,
            author=cls.user
        )
        cls.test_post_2 = Post.objects.create(
            text='Тест №0_1',
            group=cls.group,
            author=cls.user
        )
        cls.test_comment = Comment.objects.create(
            text='Тестовый комментарий №0 к тестовому посту',
            author=cls.user,
            post=cls.test_post
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.user_1_client = Client()
        self.user_1_client.force_login(PostCreateEditFormTests.user)

    def test_create_post(self):
        """
        Проверим формы создания поста.
        """
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тест №1',
            'group': PostCreateEditFormTests.group.pk
        }
        response = self.user_1_client.post(
            reverse(
                'posts:post_create'
            ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': self.user}
            )
        )
        self.assertEqual(
            Post.objects.count(),
            post_count + 1
        )
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=form_data['group'],
                author=PostCreateEditFormTests.user
            ).exists()
        )

    def test_edit_post(self):
        """
        Проверим формы редактирования поста.
        """
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тест №2',
            'group': PostCreateEditFormTests.group.pk
        }
        response = self.user_1_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostCreateEditFormTests.test_post.id}
            ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostCreateEditFormTests.test_post.id}
            )
        )
        self.assertEqual(
            Post.objects.count(),
            post_count
        )
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=form_data['group'],
                author=PostCreateEditFormTests.user
            ).exists()
        )

    def test_image_form_context(self):
        """
        Проверим, что в базе данных создаётся
        корректный пост с картинкой.
        """
        post_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тест №3',
            'group': PostCreateEditFormTests.group.pk,
            'image': uploaded
        }
        self.user_1_client.post(
            reverse(
                'posts:post_create'
            ),
            data=form_data,
            follow=True
        )
        self.assertEqual(
            Post.objects.count(),
            post_count + 1
        )
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=form_data['group'],
                author=PostCreateEditFormTests.user,
                image='posts/small.gif'
            ).exists()
        )

    def test_comment_create(self):
        """
        Проверим, что при что при создании комментария, он начинает
        отображаться на странице post_detail.
        """
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Тестовый комментарий №1 к тестовому посту',
        }
        self.user_1_client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': PostCreateEditFormTests.test_post.id}
            ),
            data=form_data,
            follow=False
        )
        self.assertEqual(comment_count + 1, Comment.objects.count())
        self.assertTrue(
            Comment.objects.filter(
                post=PostCreateEditFormTests.test_post,
                text=form_data['text'],
                author=PostCreateEditFormTests.user
            ).exists()
        )
