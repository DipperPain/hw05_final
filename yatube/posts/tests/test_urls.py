from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from ..models import Group, Post
from django.urls import reverse


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.index_reverse = reverse('posts:index')

    def test_homepage(self):
        response = self.guest_client.get(self.index_reverse)
        self.assertEqual(response.status_code, 200)


User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создадим запись в БД для проверки доступности адреса group/test-slug/
        Group.objects.create(
            title='Тестовое сообщество',
            slug='test-slug',
            description='Тестовое описание'
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем пользователя
        self.user = User.objects.create_user(username='test')
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)
        self.post_test = Post.objects.create(
            text='Test',
            author=self.user
        )

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Шаблоны по адресам
        templates_url_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={'slug': 'test-slug'}
            ): 'posts/group_list.html',
            reverse(
                'posts:/profile/', kwargs={'username': 'test'}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': f'{self.post_test.id}'}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': f'{self.post_test.id}'}
            ): 'posts/post_create.html',
            '/create/': 'posts/post_create.html',
        }

        templates_url_names_noname = {
            '/': 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={'slug': 'test-slug'}
            ): 'posts/group_list.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': f'{self.post_test.id}'}
            ): 'posts/post_detail.html',

        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)

        for adress, template in templates_url_names_noname.items():
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_unexist(self):
        """Страница /недоступна любому пользователю."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404)

    def test_url_guest_create(self):
        """Страница по адресу /create/ перенаправит анонимного
        пользователя на страницу логина.
        """
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/create/'
        )

    def test_url_guest_edit(self):
        """Страница по адресу /edit/ перенаправит анонимного
        пользователя на страницу логина.
        """
        response = self.guest_client.get(
            f'/posts/{self.post_test.id}/edit/', follow=True
        )
        self.assertRedirects(
            response, f'/auth/login/?next=/posts/{self.post_test.id}/edit/'
        )

    def test_unexist_test(self):
        """Страница /недоступна любому пользователю."""
        response = self.authorized_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404)

    def test_guest_comment_recive(self):
        """Страница по адресу /comment/ перенаправит анонимного
        пользователя на страницу логина.
        """
        response = self.guest_client.get(reverse(
            'posts:add_comment',
            kwargs={'post_id': f'{self.post_test.id}'}),
            follow=True
        )
        self.assertRedirects(
            response, f'/auth/login/?next=/posts/{self.post_test.id}/comment'
        )

    def test_form_comment(self):

        form_data = {
            'text': 'Тестовый текст',
        }
        # Отправляем POST-запрос
        self.authorized_client.post(
            reverse('posts:add_comment',
                    kwargs={'post_id': f'{self.post_test.id}'}),
            data=form_data,
            follow=True
        )
        response = self.authorized_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': f'{self.post_test.id}'}
                    )
        )
        comment_object = response.context['comments'][0]
        comment_text_0 = comment_object.text
        self.assertEqual(comment_text_0, 'Тестовый текст')
