from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.core.cache import cache

from posts.models import Group, Post

User = get_user_model()


class TestCache(TestCase):
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

    def setUp(self):
        self.user_1_client = Client()
        self.user_1_client.force_login(TestCache.user)

    def test_cache(self):
        """
        Проверим, что до очистки кэша контент сохраняется даже
        после принудительного удаления объекта из базы данных
        """
        response_1 = self.user_1_client.get(
            reverse(
                'posts:index'
            )
        )
        TestCache.test_post.delete()
        response_2 = self.user_1_client.get(
            reverse(
                'posts:index'
            )
        )
        self.assertEqual(response_1.content, response_2.content)
        cache.clear()
        response_3 = self.user_1_client.get(
            reverse(
                'posts:index'
            )
        )
        self.assertNotEqual(response_1.content, response_3.content)
