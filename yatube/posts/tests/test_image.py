import shutil
import tempfile
from django.contrib.auth import get_user_model
from ..forms import PostForm
from ..models import Post, Group
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TaskCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.user = User.objects.create_user(username='test')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(
            title='Заголовок',
            slug='test-slug',
        )

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        # Подсчитаем количество записей в Task
        post_count = Post.objects.count()
        self.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        self.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=self.small_gif,
            content_type='image/gif'
        )
        # Для тестирования загрузки изображений
        # берём байт-последовательность картинки,
        # состоящей из двух пикселей: белого и чёрного

        form_data = {
            'title': 'Тестовый заголовок',
            'text': 'Тестовый текст',
            'image': self.uploaded,
        }
        # Отправляем POST-запрос
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), post_count + 1)

    def test_post_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        test_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='test1.gif',
            content=test_gif,
            content_type='image/gif'
        )
        self.post_test = Post.objects.create(
            text='Test',
            author=self.user,
            group=self.group,
            image=uploaded
        )
        response = self.authorized_client.get(reverse('posts:index'))

        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        first_object = response.context['page_obj'][0]
        post_author_0 = first_object.author.username
        post_text_0 = first_object.text
        post_group_0 = first_object.group.title
        post_image_0 = first_object.image
        self.assertEqual(post_author_0, 'test')
        self.assertEqual(post_text_0, 'Test')
        self.assertEqual(post_group_0, f'{self.group}')
        self.assertEqual(post_image_0, 'posts/test1.gif')

    def test_post_profile_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        test_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='test2.gif',
            content=test_gif,
            content_type='image/gif'
        )
        self.post_test = Post.objects.create(
            text='Test',
            author=self.user,
            group=self.group,
            image=uploaded
        )
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
        post_image_0 = first_object.image
        self.assertEqual(post_author_0, 'test')
        self.assertEqual(post_text_0, 'Test')
        self.assertEqual(post_group_0, f'{self.group}')
        self.assertEqual(post_image_0, 'posts/test2.gif')

    def test_post_group_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        test_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='test3.gif',
            content=test_gif,
            content_type='image/gif'
        )
        self.post_test = Post.objects.create(
            text='Test',
            author=self.user,
            group=self.group,
            image=uploaded
        )
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'})
        )
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        first_object = response.context['page_obj'][0]
        post_author_0 = first_object.author.username
        post_text_0 = first_object.text
        post_group_0 = first_object.group.title
        post_image_0 = first_object.image
        self.assertEqual(post_author_0, 'test')
        self.assertEqual(post_text_0, 'Test')
        self.assertEqual(post_group_0, f'{self.group}')
        self.assertEqual(post_image_0, 'posts/test3.gif')

    def test_post_detail_pages_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        test_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='test4.gif',
            content=test_gif,
            content_type='image/gif'
        )
        self.post_test = Post.objects.create(
            text='Test',
            author=self.user,
            group=self.group,
            image=uploaded
        )
        response = (self.authorized_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': f'{self.post_test.id}'})))
        self.assertEqual(response.context.get('post').image, 'posts/test4.gif')
