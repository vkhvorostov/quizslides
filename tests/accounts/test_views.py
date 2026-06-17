import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from django.test import Client


@pytest.mark.django_db
class TestSignupView:

    def test_signup_get(self):
        client = Client()
        response = client.get(reverse('accounts:signup'))
        assert response.status_code == 200
        assert 'form' in response.context

    def test_signup_post_valid(self):
        client = Client()
        data = {
            'username': 'newuser',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123',
        }
        response = client.post(reverse('accounts:signup'), data)
        # После успешной регистрации должен быть редирект на login
        assert response.status_code == 302
        assert response.url == reverse('accounts:login')
        # Проверяем, что пользователь создан
        assert User.objects.filter(username='newuser').exists()

    def test_signup_post_invalid(self):
        client = Client()
        data = {
            'username': 'newuser',
            'password1': 'pass',
            'password2': 'pass2',  # не совпадают
        }
        response = client.post(reverse('accounts:signup'), data)
        assert response.status_code == 200
        assert 'form' in response.context
        assert response.context['form'].errors


@pytest.mark.django_db
class TestProfileView:

    def test_profile_requires_login(self):
        client = Client()
        response = client.get(reverse('accounts:profile'))
        # Должен быть редирект на страницу входа (или 403)
        assert response.status_code == 302
        # Проверяем, что редирект на login (с учетом настроек)
        assert 'login' in response.url

    def test_profile_authenticated(self, user):
        client = Client()
        client.force_login(user)
        response = client.get(reverse('accounts:profile'))

        # Редирект на главную страницу
        assert response.status_code == 302
        assert response.url == reverse('index')

        response_follow = client.get(reverse('accounts:profile'), follow=True)
        assert response_follow.status_code == 200