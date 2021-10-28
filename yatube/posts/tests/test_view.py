from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms
from ..models import Group, Post


User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создадим запись в БД
        Group.objects.create(
            title='Тестовое сообщество',
            slug='test-slug',
            description='Тестовое описание'
        )

    def setUp(self):
        # Создаем авторизованный клиент
        self.user = User.objects.create_user(username='test')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post_test = Post.objects.create(
            text='Test',
            author=self.user
        )
    # Проверяем используемые шаблоны

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "имя_html_шаблона: reverse(name)"
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={'slug': 'test-slug'}
            ): 'posts/group_list.html',
            reverse(
                'posts:/profile/', kwargs={'username': f'{self.user.username}'}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': f'{self.post_test.id}'}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': f'{self.post_test.id}'}
            ): 'posts/post_create.html',
            reverse(
                'posts:post_create'
            ): 'posts/post_create.html',
        }
        # Проверяем, что при обращении к name вызывается соответствующий HTML
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)


class PostContextTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создадим запись в БД

    def setUp(self):
        # Создаем авторизованный клиент
        self.user = User.objects.create_user(username='test')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(
            title='Заголовок',
            slug='test-slug',
        )
        self.post_test = Post.objects.create(
            text='Test',
            author=self.user,
            group=self.group
        )

    def test_post_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        first_object = response.context['page_obj'][0]
        post_author_0 = first_object.author.username
        post_text_0 = first_object.text
        post_group_0 = first_object.group.title
        self.assertEqual(post_author_0, 'test')
        self.assertEqual(post_text_0, 'Test')
        self.assertEqual(post_group_0, f'{self.group}')

    def test_post_group_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'})
        )
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        first_object = response.context['page_obj'][0]
        post_author_0 = first_object.author.username
        post_text_0 = first_object.text
        post_group_0 = first_object.group.title
        self.assertEqual(post_author_0, 'test')
        self.assertEqual(post_text_0, 'Test')
        self.assertEqual(post_group_0, f'{self.group}')

    def test_post_profile_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:/profile/',
                kwargs={'username': f'{self.user.username}'}
            )
        )
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        first_object = response.context['page_obj'][0]
        post_author_0 = first_object.author.username
        post_text_0 = first_object.text
        post_group_0 = first_object.group.title
        self.assertEqual(post_author_0, 'test')
        self.assertEqual(post_text_0, 'Test')
        self.assertEqual(post_group_0, f'{self.group}')

    def test_post_detail_pages_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = (self.authorized_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': f'{self.post_test.id}'})))
        self.assertEqual(response.context.get('post').text, 'Test')
        self.assertEqual(response.context.get('post').author.username, 'test')

    def test_create_correct_context(self):
        """Шаблон home сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        # Словарь ожидаемых типов полей формы:
        # указываем, объектами какого класса должны быть поля формы
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        # Проверяем, типы полей формы в словаре context
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)

    def test_edit_correct_context(self):
        """Шаблон home сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': f'{self.post_test.id}'})
        )
        # Словарь ожидаемых типов полей формы:
        # указываем, объектами какого класса должны быть поля формы
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)


class PaginatorViewsTest(TestCase):
    # Здесь создаются фикстуры: клиент и 13 тестовых записей.
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создадим запись в БД

    def setUp(self):
        # Создаем авторизованный клиент
        self.group = Group.objects.create(
            title='Тестовое сообщество',
            slug='test-slug',
            description='Тестовое описание'
        )
        self.user = User.objects.create_user(username='test')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        for i in range(13):
            self.post_test = Post.objects.create(
                text='Test',
                author=self.user,
                group=self.group
            )

    def test_first_page_contains_ten_records(self):
        response = self.authorized_client.get(reverse('posts:index'))
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        # Проверка: на второй странице должно быть три поста.
        response = self.authorized_client.get(
            reverse('posts:index') + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_first_page_group(self):
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'})
        )
        # Проверка: количество постов на первой странице равно 10
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_group(self):
        # Проверка: на второй странице должно быть три поста.
        response = self.authorized_client.get(
            reverse(
                'posts:group_list', kwargs={'slug': 'test-slug'}
            ) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_first_page_user(self):
        response = self.authorized_client.get(
            reverse(
                'posts:/profile/', kwargs={'username': f'{self.user.username}'}
            )
        )
        # Проверка: количество постов на первой странице равно 10
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_user(self):
        # Проверка: на второй странице должно быть три поста.
        response = self.authorized_client.get(
            reverse(
                'posts:/profile/', kwargs={'username': f'{self.user.username}'}
            ) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)
