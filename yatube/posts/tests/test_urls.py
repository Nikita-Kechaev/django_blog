from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from posts.models import Group, Post

User = get_user_model()


class PostsURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author_post = User.objects.create_user(username='author_post')
        cls.user = User.objects.create_user(username='test_user')
        cls.post = Post.objects.create(
            text='Очень тяжело делать тесты',
            author=cls.author_post
        )
        cls.group = Group.objects.create(
            title='test_group',
            slug='test_group',
            description='Ужас как сложно'
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsURLTest.user)
        self.author_post_client = Client()
        self.author_post_client.force_login(PostsURLTest.author_post)
        self.list_of_users = [
            self.guest_client,
            self.authorized_client,
            self.author_post_client
        ]

    def test_users_urls_reposne_and_redirect(self):
        """
        Проверяем response_status и redirect страниц для:
        1 : неавторизированного пользователя,
        2 : авторизированного пользователя,
        3 : авторизированного пользователя aka автора поста.
        (в urls_response.value содежатся списки для response_status
         в порядке, указанном выше).
        (в urls_redirect.value содержатся списки ссылок
        на которые перенаправляются пользователи).
        """
        urls_response = {
            '/unexisting_page/': [404, 404, 404],
            '/': [200, 200, 200],
            f'/group/{PostsURLTest.group}/': [200, 200, 200],
            f'/profile/{PostsURLTest.author_post}/': [200, 200, 200],
            f'/posts/{PostsURLTest.post.id}/': [200, 200, 200],
            '/create/': [302, 200, 200],
            f'/posts/{PostsURLTest.post.id}/edit/': [302, 302, 200],
            f'/posts/{PostsURLTest.post.id}/comment/': [302, 302, 302],
            f'/profile/{PostsURLTest.author_post}/follow/': [302, 302, 302]
        }
        urls_redirect = {
            '/create/': [
                '/auth/login/?next=/create/'
            ],
            f'/posts/{PostsURLTest.post.id}/edit/': [
                f'/auth/login/?next=/posts/{PostsURLTest.post.id}/edit/',
                f'/posts/{PostsURLTest.post.id}/'
            ],
            f'/posts/{PostsURLTest.post.id}/comment/': [
                f'/auth/login/?next=/posts/{PostsURLTest.post.id}/comment/',
                f'/posts/{PostsURLTest.post.id}/',
                f'/posts/{PostsURLTest.post.id}/'
            ],
            f'/profile/{PostsURLTest.author_post}/follow/': [
                '/auth/login/?next=/profile/'
                f'{PostsURLTest.author_post}/follow/',
                f'/profile/{PostsURLTest.author_post}/',
                f'/profile/{PostsURLTest.author_post}/'
            ]
        }
        for us in self.list_of_users:
            for adress, url_resonse in urls_response.items():
                with self.subTest():
                    response = us.get(adress)
                    if response.status_code == 302:
                        self.assertRedirects(
                            response,
                            urls_redirect[adress][
                                self.list_of_users.index(us)
                            ]
                        )
                    self.assertEqual(
                        response.status_code,
                        url_resonse[self.list_of_users.index(us)])

    def test_url_uses_correct_template(self):
        """
        Проверим соответствие URL адресов и
        используемых шаблонов.
        В templates ссылки а также шаблоны
        которые используют пользователи :
        1  - гость 2 - авторизированный 3 - автор поста.
        """
        templates = {
            '/': [
                'posts/index.html',
                'posts/index.html',
                'posts/index.html'
            ],
            f'/group/{PostsURLTest.group}/': [
                'posts/group_list.html',
                'posts/group_list.html',
                'posts/group_list.html'
            ],
            f'/profile/{PostsURLTest.author_post}/': [
                'posts/profile.html',
                'posts/profile.html',
                'posts/profile.html'
            ],
            f'/posts/{PostsURLTest.post.id}/': [
                'posts/post_detail.html',
                'posts/post_detail.html',
                'posts/post_detail.html',
            ],
            '/create/': [
                'users/login.html',
                'posts/create_post.html',
                'posts/create_post.html'
            ],
            f'/posts/{PostsURLTest.post.id}/edit/': [
                'users/login.html',
                'posts/post_detail.html',
                'posts/create_post.html'
            ]
        }
        for us in self.list_of_users:
            for url, template in templates.items():
                with self.subTest():
                    response = us.get(url, follow=True)
                    self.assertTemplateUsed(
                        response,
                        template[self.list_of_users.index(us)],
                    )
