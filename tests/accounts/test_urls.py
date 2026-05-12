import pytest
from django.urls import reverse, resolve
from accounts import views
from django.contrib.auth import views as auth_views


@pytest.mark.django_db
class TestAccountsUrls:

    def test_signup_url(self):

        url = reverse('accounts:signup')
        assert url == '/accounts/signup/'
        resolver = resolve(url)
        assert resolver.func == views.signup_view
        assert resolver.namespace == 'accounts'

    def test_login_url(self):
        url = reverse('accounts:login')
        assert url == '/accounts/login/'
        resolver = resolve(url)
        # Это класс-based view, поэтому сравниваем .view_class
        assert resolver.func.view_class == auth_views.LoginView
        assert resolver.namespace == 'accounts'

    def test_logout_url(self):
        url = reverse('accounts:logout')
        assert url == '/accounts/logout/'
        resolver = resolve(url)
        assert resolver.func.view_class == auth_views.LogoutView

    def test_profile_url(self):
        url = reverse('accounts:profile')
        assert url == '/accounts/profile/'
        resolver = resolve(url)
        assert resolver.func == views.profile_view