import pytest

from core.models import Presentation, Slide


@pytest.mark.django_db
def test_slide_default_type_and_content(user):
    presentation = Presentation.objects.create(
        id_user=user, name='Презентация', status=True
    )
    slide = Slide.objects.create(
        id_presentation=presentation, number=1, status=True
    )
    assert slide.slide_type == 'CONTENT'
    assert slide.content == ''


@pytest.mark.django_db
def test_deleting_presentation_deletes_slides(user):
    presentation = Presentation.objects.create(
        id_user=user, name='Удаляемая', status=True
    )
    Slide.objects.create(id_presentation=presentation, number=1, status=True)
    Slide.objects.create(id_presentation=presentation, number=2, status=True)
    presentation_id = presentation.id_presentation
    presentation.delete()
    assert not Slide.objects.filter(id_presentation_id=presentation_id).exists()
