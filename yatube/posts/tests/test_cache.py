from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from ..models import Post
from django.core.cache import cache

User = get_user_model()


class PostCacheTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        # Создаем авторизованный клиент
        self.user = User.objects.create_user(username='test')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_cache(self):
        post_test = Post.objects.create(
            text='Test',
            author=self.user
        )

        response_1 = self.authorized_client.get(reverse('posts:index')).content
        post_test.delete()
        response_2 = self.authorized_client.get(reverse('posts:index')).content
        self.assertEquals(response_1, response_2)
        cache.clear()
        response_3 = self.authorized_client.get(reverse('posts:index')).content
        self.assertNotEqual(response_2, response_3)
