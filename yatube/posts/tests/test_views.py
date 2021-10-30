from django import forms
import shutil
import tempfile
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.core.cache import cache
from posts.models import Follow, Group, Post, Comment

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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
        cls.user = User.objects.create_user(username='user')
        cls.user_author = User.objects.create_user(username='user_author')
        cls.group_1 = Group.objects.create(
            title='test_group_1',
            slug='test_group_1'
        )
        cls.group_2 = Group.objects.create(
            title='test_group_2',
            slug='test_group_2'
        )
        cls.post = Post.objects.create(
            text='Тест №без номера',
            author=cls.user_author,
            group=cls.group_2,
            image=uploaded
        )
        cls.comment = Comment.objects.create(
            text='Тестовый комментарий №0 к тестовому посту',
            author=cls.user,
            post=cls.post
        )
        posts_list = [
            Post(
                text=f'Тест №{i}',
                group=cls.group_1,
                author=cls.user_author
            ) for i in range(13)
        ]
        Post.objects.bulk_create(posts_list)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostPagesTests.user)
        self.author_post_client = Client()
        self.author_post_client.force_login(PostPagesTests.user_author)
        self.list_of_users = [
            self.guest_client,
            self.authorized_client,
            self.author_post_client
        ]

    def test_pages_uses_correct_template(self):
        """
        Проверяем шаблоны в View - функциях.
        Для гостя, авторизованного, автора поста.
        """
        templates_pages_names = {
            reverse('posts:index'): [
                'posts/index.html',
                'posts/index.html',
                'posts/index.html'
            ],
            reverse(
                'posts:group_list',
                kwargs={'slug': PostPagesTests.group_1.slug}
            ): [
                'posts/group_list.html',
                'posts/group_list.html',
                'posts/group_list.html'
            ],
            reverse(
                'posts:profile',
                kwargs={'username': self.user}
            ): [
                'posts/profile.html',
                'posts/profile.html',
                'posts/profile.html'
            ],
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostPagesTests.post.id}
            ): [
                'posts/post_detail.html',
                'posts/post_detail.html',
                'posts/post_detail.html'
            ],
            reverse(
                'posts:post_create'
            ): [
                'users/login.html',
                'posts/create_post.html',
                'posts/create_post.html'
            ],
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostPagesTests.post.id}
            ): [
                'users/login.html',
                'posts/post_detail.html',
                'posts/create_post.html'
            ]
        }
        for us in self.list_of_users:
            for name, template in templates_pages_names.items():
                with self.subTest():
                    response = us.get(name, follow=True)
                    self.assertTemplateUsed(
                        response,
                        template[self.list_of_users.index(us)]
                    )

    def test_paginator(self):
        """
        Проверим кол-во постов на 1 - 2 страницах.
        """
        page_count_dict = {
            reverse(
                'posts:index'
            ): 10,
            reverse(
                'posts:index'
            ) + '?page=2': 4,
            reverse(
                'posts:group_list',
                kwargs={'slug': PostPagesTests.group_1.slug}
            ): 10,
            reverse(
                'posts:group_list',
                kwargs={'slug': PostPagesTests.group_1.slug}
            ) + '?page=2': 3,
            reverse(
                'posts:profile',
                kwargs={'username': PostPagesTests.user_author}
            ): 10,
            reverse(
                'posts:profile',
                kwargs={'username': PostPagesTests.user_author}
            ) + '?page=2': 4,

        }
        for page_name, page_count in page_count_dict.items():
            with self.subTest():
                response = self.authorized_client.get(page_name)
                obj_count = len(
                    response.context.get(
                        'page_obj'
                    ).object_list
                )
                self.assertEqual(obj_count, page_count)

    def test_index_contex(self):
        """
        Проверяем, что передаём в view.index верный context.
        """
        cache.clear()
        post_list = list(Post.objects.all()[:10])
        response = self.guest_client.get(reverse('posts:index'))
        response_list = response.context.get('page_obj').object_list
        self.assertEqual(post_list, response_list)

    def test_group_context(self):
        """
        Проверяем, что передаём в view.group_list верный context.
        """
        posts_list = list(PostPagesTests.group_1.posts.all()[:10])
        response = self.guest_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': PostPagesTests.group_1.slug}
            )
        )
        obj_list = response.context.get('page_obj').object_list
        self.assertEqual(posts_list, obj_list)

    def test_profile_context(self):
        """
        Проверяем, что передаём в view.profile верный context.
        """
        posts_list = list(PostPagesTests.user_author.posts.all()[:10])
        respons = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': PostPagesTests.user_author}
            )
        )
        obj_list = respons.context.get('page_obj').object_list
        self.assertEqual(posts_list, obj_list)

    def test_post_detail_context(self):
        """
        Проверяем, что на страницу post_detail передаётся
        корректная запись.
        """
        post = PostPagesTests.post
        test_comment = post.comments.all()[0]
        response = self.guest_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': post.id}
            )
        )
        obj = response.context.get('post')
        obj_comment = obj.comments.all()[0]
        self.assertEqual(post, obj)
        self.assertEqual(test_comment, obj_comment)

    def test_post_edit_form(self):
        """
        Проверяем контекст на странице post_edit.
        """
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        post = PostPagesTests.post
        response = self.author_post_client.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': post.id}
            )
        )
        obj = response.context.get('form')
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = obj.fields.get(value)
                self.assertIsInstance(form_field, expected)
        self.assertEqual(post.text, obj.instance.text)
        self.assertEqual(post.group, obj.instance.group)

    def test_post_create_context(self):
        """
        Проверяем поля формы на странице post_create.
        """
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        response = self.author_post_client.get(
            reverse(
                'posts:post_create'
            )
        )
        form = response.context.get('form')
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = form.fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_if_post_has_group_view(self):
        """
        Проверим, что при создании поста, он отображается на странице
        группы, которой он принадлежит и автора кто его создал,
        и не отображается на странице группы, которой не принадлежит.
        """
        post = Post.objects.create(
            text='Тест №13',
            group=PostPagesTests.group_2,
            author=PostPagesTests.user_author
        )
        page_list_with_post = [
            reverse(
                'posts:group_list',
                kwargs={'slug': post.group}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': post.author}
            )
        ]
        group_page_without_post = reverse(
            'posts:group_list',
            kwargs={'slug': PostPagesTests.group_1.slug}
        )
        response = self.authorized_client.get(group_page_without_post)
        obj_list = response.context.get('page_obj').paginator.object_list
        self.assertNotIn(post, obj_list)
        for page in page_list_with_post:
            response = self.authorized_client.get(page)
            obj_list = response.context.get('page_obj').paginator.object_list
            with self.subTest():
                self.assertIn(post, obj_list)

    def test_follower_context(self):
        """
        Проверим, что созданный автором пост отображается
        в follower-ленте тех, кто подписан на данного автора,
        """
        Follow.objects.create(
            user=PostPagesTests.user,
            author=PostPagesTests.user_author
        )
        response = self.authorized_client.get(
            reverse(
                'posts:follow_index'
            )
        )
        obj_list = response.context.get('page_obj').paginator.object_list
        post = PostPagesTests.post
        self.assertIn(post, obj_list)

    def test_follow(self):
        """
        Проверка follow и unfollow
        """
        self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': PostPagesTests.user_author}
            )
        )
        self.assertTrue(
            Follow.objects.filter(
                user=PostPagesTests.user,
                author=PostPagesTests.user_author
            ).exists()
        )

    def test_unfollow(self):
        Follow.objects.create(
            user=PostPagesTests.user,
            author=PostPagesTests.user_author
        )
        self.authorized_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': PostPagesTests.user_author}
            )
        )
        self.assertFalse(
            Follow.objects.filter(
                user=PostPagesTests.user,
                author=PostPagesTests.user_author
            ).exists()
        )
