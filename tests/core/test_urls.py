import pytest
from django.urls import reverse, resolve
from core import views


@pytest.mark.django_db
class TestCoreUrls:

    def test_create_presentation_url(self):
        url = reverse('core:create_presentation')
        assert url == '/create/'
        resolver = resolve(url)
        assert resolver.func == views.create_presentation
        assert resolver.namespace == 'core'

    def test_editor_url(self):
        url = reverse('core:editor', args=[1])
        assert url == '/editor/1/'
        resolver = resolve('/editor/1/')
        assert resolver.func == views.editor_view
        assert resolver.kwargs == {'presentation_id': 1}

    def test_update_title_url(self):
        url = reverse('core:update_title', args=[5])
        assert url == '/api/presentation/5/update-title/'
        resolver = resolve('/api/presentation/5/update-title/')
        assert resolver.func == views.update_title
        assert resolver.kwargs == {'presentation_id': 5}

    def test_add_slide_url(self):
        url = reverse('core:add_slide', args=[10])
        assert url == '/api/presentation/10/add-slide/'
        resolver = resolve('/api/presentation/10/add-slide/')
        assert resolver.func == views.add_slide
        assert resolver.kwargs == {'presentation_id': 10}