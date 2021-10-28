from django.test import TestCase, Client
from django.urls import reverse


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.reverse_author = reverse('about:author')
        self.reverse_tech = reverse('about:tech')

    def test_author(self):
        response = self.guest_client.get(self.reverse_author)
        # Утверждаем, что для прохождения теста код должен быть равен 200
        self.assertEqual(response.status_code, 200)

    def test_tech(self):
        response = self.guest_client.get(self.reverse_tech)
        # Утверждаем, что для прохождения теста код должен быть равен 200
        self.assertEqual(response.status_code, 200)
