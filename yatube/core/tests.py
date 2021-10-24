from django.contrib.auth import get_user_model
from django.test import Client, TestCase


User = get_user_model()


class CorePagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')

    def setUp(self):
        self.guest_client = Client()
        self.auth_user_client = Client()
        self.auth_user_client.force_login(CorePagesTest.user)
        self.user_list = [
            self.guest_client,
            self.auth_user_client
        ]

    def test_404_page_template(self):
        """
        Проверим, что несуществующая страница вернёт нужный шаблон.
        Для гостя и неавторизированноо пользователя.
        """
        templates = {
            '/qwerty_123_lalaland': [
                'core/404.html',
                'core/404.html',
            ]
        }
        for us in self.user_list:
            for url, template in templates.items():
                response = us.get(url)
                self.assertTemplateUsed(
                    response,
                    template[self.user_list.index(us)]
                )
