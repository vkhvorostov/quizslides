import json

import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse

from core.models import Presentation, Slide


@pytest.mark.django_db
class TestGetSlideView:

    def test_owner_gets_slide_json(self, user, presentation):
        slide = Slide.objects.create(
            id_presentation=presentation,
            number=1,
            content='Привет',
            slide_type='CONTENT',
            status=True,
        )
        client = Client()
        client.force_login(user)
        response = client.get(reverse('core:get_slide', args=[slide.id_slide]))

        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is True
        assert data['content'] == 'Привет'
        assert data['slide_type'] == 'CONTENT'

    def test_other_user_gets_404(self, user):
        other = User.objects.create_user('other', 'o@example.com', 'pass')
        presentation = Presentation.objects.create(id_user=other, name='Чужая', status=True)
        slide = Slide.objects.create(
            id_presentation=presentation, number=1, status=True
        )
        client = Client()
        client.force_login(user)
        response = client.get(reverse('core:get_slide', args=[slide.id_slide]))
        assert response.status_code == 404

    def test_get_slide_requires_login(self, presentation):
        slide = Slide.objects.create(
            id_presentation=presentation, number=1, status=True
        )
        response = Client().get(reverse('core:get_slide', args=[slide.id_slide]))
        assert response.status_code == 302
        assert 'login' in response.url


@pytest.mark.django_db
class TestUpdateSlideContentView:

    def test_post_updates_content(self, user, presentation):
        slide = Slide.objects.create(
            id_presentation=presentation, number=1, status=True
        )
        client = Client()
        client.force_login(user)
        response = client.post(
            reverse('core:update_slide_content', args=[slide.id_slide]),
            {'content': 'Новый текст'},
        )

        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is True
        slide.refresh_from_db()
        assert slide.content == 'Новый текст'

    def test_update_slide_requires_login(self, presentation):
        slide = Slide.objects.create(
            id_presentation=presentation, number=1, status=True
        )
        response = Client().post(
            reverse('core:update_slide_content', args=[slide.id_slide]),
            {'content': 'x'},
        )
        assert response.status_code == 302
        assert 'login' in response.url

    def test_update_slide_other_user_gets_404(self, user):
        other = User.objects.create_user('other2', 'o2@example.com', 'pass')
        presentation = Presentation.objects.create(id_user=other, name='X', status=True)
        slide = Slide.objects.create(
            id_presentation=presentation, number=1, status=True
        )
        client = Client()
        client.force_login(user)
        response = client.post(
            reverse('core:update_slide_content', args=[slide.id_slide]),
            {'content': 'hack'},
        )
        assert response.status_code == 404

    def test_update_slide_get_not_allowed(self, user, presentation):
        slide = Slide.objects.create(
            id_presentation=presentation, number=1, status=True
        )
        client = Client()
        client.force_login(user)
        response = client.get(
            reverse('core:update_slide_content', args=[slide.id_slide])
        )
        assert response.status_code == 405


@pytest.mark.django_db
class TestReorderSlidesView:

    def test_reorder_changes_numbers(self, user, presentation):
        s1 = Slide.objects.create(id_presentation=presentation, number=1, status=True)
        s2 = Slide.objects.create(id_presentation=presentation, number=2, status=True)
        client = Client()
        client.force_login(user)
        response = client.post(
            reverse('core:reorder_slides', args=[presentation.id_presentation]),
            data=json.dumps({'slide_ids': [s2.id_slide, s1.id_slide]}),
            content_type='application/json',
        )

        assert response.status_code == 200
        assert json.loads(response.content)['success'] is True
        s1.refresh_from_db()
        s2.refresh_from_db()
        assert s2.number == 1
        assert s1.number == 2

    def test_reorder_other_user_gets_404(self, user):
        other = User.objects.create_user('other3', 'o3@example.com', 'pass')
        presentation = Presentation.objects.create(id_user=other, name='Y', status=True)
        client = Client()
        client.force_login(user)
        response = client.post(
            reverse('core:reorder_slides', args=[presentation.id_presentation]),
            data=json.dumps({'slide_ids': []}),
            content_type='application/json',
        )
        assert response.status_code == 404

    def test_reorder_invalid_json_returns_400(self, user, presentation):
        client = Client()
        client.force_login(user)
        response = client.post(
            reverse('core:reorder_slides', args=[presentation.id_presentation]),
            data='not json',
            content_type='application/json',
        )
        assert response.status_code == 400


@pytest.mark.django_db
class TestAddSlideView:

    def test_add_slide_with_type(self, user, presentation):
        client = Client()
        client.force_login(user)
        response = client.post(
            reverse('core:add_slide', args=[presentation.id_presentation]),
            data=json.dumps({'type': 'QUIZ'}),
            content_type='application/json',
        )
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is True
        slide = Slide.objects.get(id_slide=data['id_slide'])
        assert slide.slide_type == 'QUIZ'

    def test_add_slide_requires_login(self, presentation):
        response = Client().post(
            reverse('core:add_slide', args=[presentation.id_presentation]),
            data=json.dumps({'type': 'CONTENT'}),
            content_type='application/json',
        )
        assert response.status_code == 302
        assert 'login' in response.url
