import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse


@pytest.mark.django_db
class TestLoginFlow:

    def test_login_page_opens(self):
        response = Client().get(reverse('accounts:login'))
        assert response.status_code == 200

    def test_valid_credentials_redirect_to_profile(self):
        User.objects.create_user('alice', 'a@example.com', 'secretpass123')
        client = Client()
        response = client.post(
            reverse('accounts:login'),
            {'username': 'alice', 'password': 'secretpass123'},
        )
        assert response.status_code == 302
        assert response.url == reverse('accounts:profile')

    def test_invalid_credentials_show_login_form(self):
        User.objects.create_user('bob', 'b@example.com', 'rightpass123')
        client = Client()
        response = client.post(
            reverse('accounts:login'),
            {'username': 'bob', 'password': 'wrong'},
        )
        assert response.status_code == 200
        assert 'form' in response.context
        assert response.context['form'].errors


@pytest.mark.django_db
class TestLogoutFlow:

    def test_logout_redirects_home(self, user):
        client = Client()
        client.force_login(user)
        response = client.post(reverse('accounts:logout'))
        assert response.status_code == 302
        assert response.url == '/'

    def test_after_logout_profile_requires_login(self, user):
        client = Client()
        client.force_login(user)
        client.post(reverse('accounts:logout'))
        response = client.get(reverse('accounts:profile'))
        assert response.status_code == 302
        assert 'login' in response.url
