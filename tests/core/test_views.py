import json
import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from core.models import Presentation, Slide


@pytest.mark.django_db
class TestCreatePresentationView:

    def test_create_presentation_requires_login(self):
        from django.test import Client
        client = Client()
        response = client.post(reverse('core:create_presentation'))
        # Должен быть редирект на login (т.к. @login_required)
        assert response.status_code == 302
        assert 'login' in response.url

    def test_create_presentation_get_not_allowed(self, user):
        from django.test import Client
        client = Client()
        client.force_login(user)
        response = client.get(reverse('core:create_presentation'))
        assert response.status_code == 405
        data = json.loads(response.content)
        assert data['success'] is False

    def test_create_presentation_post_valid(self, user):
        from django.test import Client
        client = Client()
        client.force_login(user)
        data = {'title': 'My New Presentation'}
        response = client.post(reverse('core:create_presentation'), data)
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is True
        assert 'id' in data
        assert data['name'] == 'My New Presentation'
        presentation = Presentation.objects.get(id_presentation=data['id'])
        assert presentation.id_user == user
        assert presentation.name == 'My New Presentation'

    def test_create_presentation_post_empty_title(self, user):
        from django.test import Client
        client = Client()
        client.force_login(user)
        data = {'title': ''}
        response = client.post(reverse('core:create_presentation'), data)
        assert response.status_code == 400
        data = json.loads(response.content)
        assert data['success'] is False
        assert 'error' in data


@pytest.mark.django_db
class TestEditorView:

    def test_editor_requires_login(self):
        from django.test import Client
        client = Client()
        presentation = Presentation.objects.create(
            id_user=User.objects.create_user('temp', 'temp@example.com', 'pass'),
            name='Test'
        )
        response = client.get(reverse('core:editor', args=[presentation.id_presentation]))
        assert response.status_code == 302
        assert 'login' in response.url

    def test_editor_owner_access(self, user, presentation):
        from django.test import Client
        client = Client()
        client.force_login(user)
        response = client.get(reverse('core:editor', args=[presentation.id_presentation]))
        assert response.status_code == 200
        assert 'presentation' in response.context
        assert 'slides' in response.context

    def test_editor_not_owner(self, user):
        from django.test import Client
        client = Client()
        other_user = User.objects.create_user('other', 'other@example.com', 'pass')
        presentation = Presentation.objects.create(
            id_user=other_user,
            name='Other Presentation'
        )
        client.force_login(user)
        response = client.get(reverse('core:editor', args=[presentation.id_presentation]))
        assert response.status_code == 404


@pytest.mark.django_db
class TestUpdateTitleView:

    def test_update_title_requires_login(self):
        from django.test import Client
        client = Client()
        presentation = Presentation.objects.create(
            id_user=User.objects.create_user('temp', 'temp@example.com', 'pass'),
            name='Test'
        )
        response = client.post(
            reverse('core:update_title', args=[presentation.id_presentation]),
            data=json.dumps({'title': 'New Title'}),
            content_type='application/json'
        )
        assert response.status_code == 302
        assert 'login' in response.url

    def test_update_title_valid(self, user, presentation):
        from django.test import Client
        client = Client()
        client.force_login(user)
        new_title = 'Updated Title'
        response = client.post(
            reverse('core:update_title', args=[presentation.id_presentation]),
            data=json.dumps({'title': new_title}),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is True
        presentation.refresh_from_db()
        assert presentation.name == new_title

    def test_update_title_empty(self, user, presentation):
        from django.test import Client
        client = Client()
        client.force_login(user)
        response = client.post(
            reverse('core:update_title', args=[presentation.id_presentation]),
            data=json.dumps({'title': ''}),
            content_type='application/json'
        )
        assert response.status_code == 400
        data = json.loads(response.content)
        assert data['success'] is False

    def test_update_title_not_owner(self, user):
        from django.test import Client
        client = Client()
        other_user = User.objects.create_user('other', 'other@example.com', 'pass')
        presentation = Presentation.objects.create(
            id_user=other_user,
            name='Other Presentation'
        )
        client.force_login(user)
        response = client.post(
            reverse('core:update_title', args=[presentation.id_presentation]),
            data=json.dumps({'title': 'Hacked'}),
            content_type='application/json'
        )
        assert response.status_code == 404


@pytest.mark.django_db
class TestAddSlideView:

    def test_add_slide_requires_login(self):
        """Требуется аутентификация."""
        from django.test import Client
        client = Client()
        presentation = Presentation.objects.create(
            id_user=User.objects.create_user('temp', 'temp@example.com', 'pass'),
            name='Test'
        )
        response = client.post(reverse('core:add_slide', args=[presentation.id_presentation]))
        assert response.status_code == 302
        assert 'login' in response.url

    def test_add_slide_valid(self, user, presentation):
        from django.test import Client

        client = Client()
        client.force_login(user)

        response = client.post(
            reverse('core:add_slide', args=[presentation.id_presentation]),
            data=json.dumps({'type': 'CONTENT'}),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is True
        assert 'id_slide' in data
        assert data['number'] == 1  # первый слайд
        assert Slide.objects.filter(id_presentation=presentation).count() == 1

    def test_add_slide_multiple(self, user, presentation):
        from django.test import Client
        client = Client()
        client.force_login(user)

        # Первый слайд
        response = client.post(
            reverse('core:add_slide', args=[presentation.id_presentation]),
            data=json.dumps({'type': 'CONTENT'}),
            content_type='application/json'
        )
        data = json.loads(response.content)
        first_number = data['number']

        # Второй слайд
        response = client.post(
            reverse('core:add_slide', args=[presentation.id_presentation]),
            data=json.dumps({'type': 'POLL'}),
            content_type='application/json'
        )
        data = json.loads(response.content)
        assert data['number'] == first_number + 1
        assert Slide.objects.filter(id_presentation=presentation).count() == 2

    def test_add_slide_not_owner(self, user):
        from django.test import Client
        client = Client()
        other_user = User.objects.create_user('other', 'other@example.com', 'pass')
        presentation = Presentation.objects.create(
            id_user=other_user,
            name='Other Presentation'
        )
        client.force_login(user)
        response = client.post(reverse('core:add_slide', args=[presentation.id_presentation]))
        assert response.status_code == 404