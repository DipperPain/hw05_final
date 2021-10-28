from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from ..models import Group, Post
User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        # Создаем пользователя
        self.user = User.objects.create_user(username='test')
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(
            title='Тестовое сообщество',
            slug='test-slug',
            description='Тестовое описание'
        )

    def test_create(self):
        post_count = Post.objects.count()
        form_data = {
            'text': 'Текст',
            'group': f'{self.group.id}',
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )

        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertEqual(response.status_code, 200)

    def test_edit(self):
        form_data = {
            'text': 'Текст2',
            'group': f'{self.group.id}',
        }
        post_test = Post.objects.create(text='Тест', author=self.user)
        self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': f'{post_test.id}'}),
            data=form_data,
            follow=True
        )
        self.post_test = Post.objects.filter(
            text='Текст2',
            group=f'{self.group.id}'
        ).exists()
        self.assertEqual(self.post_test, True)
