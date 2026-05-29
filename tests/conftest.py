import pytest
from django.contrib.auth import get_user_model
from core.models import Presentation, Slide, Session

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def session(db, user):
    return Session.objects.create(
        status=True,
        time_end='2025-12-31T23:59:59Z',
        max_count_people=100,
        code='TEST123',
        id_user=user
    )


@pytest.fixture
def presentation(db, user):
    return Presentation.objects.create(
        id_user=user,
        name='Test Presentation',
        status=True
    )


@pytest.fixture
def slide(db, presentation):
    return Slide.objects.create(
        number=1,
        picture=None,
        status=True,
        id_presentation=presentation
    )