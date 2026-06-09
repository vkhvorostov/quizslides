import pytest
from django.urls import resolve, reverse

from core import views


@pytest.mark.django_db
class TestSlideApiUrls:

    def test_get_slide_url(self):
        url = reverse('core:get_slide', args=[7])
        assert url == '/api/slide/7/'
        assert resolve(url).func == views.get_slide

    def test_update_slide_content_url(self):
        url = reverse('core:update_slide_content', args=[3])
        assert url == '/api/slide/3/update-content/'
        assert resolve(url).func == views.update_slide_content

    def test_reorder_slides_url(self):
        url = reverse('core:reorder_slides', args=[1])
        assert url == '/api/presentation/1/reorder-slides/'
        assert resolve(url).func == views.reorder_slides
