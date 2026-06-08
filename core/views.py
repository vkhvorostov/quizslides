from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.views.decorators.http import require_POST

from .models import Presentation, Session, Slide


SESSION_CODE_ALPHABET = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'


def _generate_session_code():
    while True:
        code = get_random_string(6, allowed_chars=SESSION_CODE_ALPHABET)
        if not Session.objects.filter(code=code, status=True).exists():
            return code


def _create_active_session(user):
    return Session.objects.create(
        status=True,
        time_end=timezone.now() + timedelta(hours=4),
        max_count_people=100,
        code=_generate_session_code(),
        id_user=user,
    )


@login_required
def create_presentation(request):
    if request.method == 'POST':
        name = request.POST.get('title', '').strip()
        if name:
            presentation = Presentation.objects.create(
                name=name,
                id_user=request.user,
                status=False
            )

            return JsonResponse({
                'success': True,
                'id': presentation.id_presentation,
                'name': presentation.name
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Название не может быть пустым'
            }, status=400)
    return JsonResponse({'success': False, 'error': 'Метод не разрешен'},
                        status=405)


@login_required
def editor_view(request, presentation_id):
    presentation = get_object_or_404(Presentation, id_presentation=presentation_id, id_user=request.user)

    slides = presentation.slides.all().order_by('number')
    return render(request, 'core/editor.html', {
        'presentation': presentation,
        'slides': slides
    })


@login_required
@require_POST
def start_presentation(request, presentation_id):
    presentation = get_object_or_404(
        Presentation,
        id_presentation=presentation_id,
        id_user=request.user,
    )

    if not presentation.slides.exists():
        messages.error(request, 'Добавьте хотя бы один слайд перед запуском')
        return redirect('core:editor', presentation_id=presentation.id_presentation)

    session = presentation.id_session
    if session is None or not session.status:
        session = _create_active_session(request.user)

    presentation.id_session = session
    presentation.status = True
    presentation.save(update_fields=['id_session', 'status'])

    return redirect('core:present_presentation', presentation_id=presentation.id_presentation)


@login_required
def present_presentation(request, presentation_id):
    presentation = get_object_or_404(
        Presentation,
        id_presentation=presentation_id,
        id_user=request.user,
    )

    if not presentation.status or presentation.id_session is None or not presentation.id_session.status:
        messages.info(request, 'Сначала запустите презентацию')
        return redirect('core:editor', presentation_id=presentation.id_presentation)

    current_slide = presentation.slides.order_by('number').first()
    if current_slide is None:
        messages.error(request, 'Добавьте хотя бы один слайд перед запуском')
        return redirect('core:editor', presentation_id=presentation.id_presentation)

    return render(request, 'core/presenter.html', {
        'presentation': presentation,
        'session': presentation.id_session,
        'current_slide': current_slide,
    })

@login_required
def update_title(request, presentation_id):

    if request.method == 'POST':
        presentation = get_object_or_404(Presentation, id_presentation=presentation_id, id_user=request.user)
        try:
            data = json.loads(request.body)
            new_title = data.get('title', '').strip()
            if new_title:
                presentation.name = new_title
                presentation.save()
                return JsonResponse({'success': True})
        except (json.JSONDecodeError, KeyError):
            pass
    return JsonResponse({'success': False}, status=400)

@login_required
def add_slide(request, presentation_id):
    if request.method == 'POST':
        presentation = get_object_or_404(Presentation, id_presentation=presentation_id, id_user=request.user)

        last_slide = presentation.slides.order_by('number').last()
        next_number = (last_slide.number + 1) if last_slide else 1

        data = json.loads(request.body)
        slide_type = data.get('type', 'CONTENT')

        new_slide = Slide.objects.create(
            id_presentation=presentation,
            number=next_number,
            status=True,
            slide_type=slide_type
        )
        
        return JsonResponse({
            'success': True, 
            'id_slide': new_slide.id_slide, 
            'number': new_slide.number
        })
    return JsonResponse({'success': False}, status=400)

@login_required
def update_slide_content(request, slide_id):

    if request.method != 'POST':
        return JsonResponse({'success': False}, status=405)

    slide = get_object_or_404(
        Slide,
        id_slide=slide_id,
        id_presentation__id_user=request.user
    )

    slide.content = request.POST.get('content', '')

    if 'picture' in request.FILES:
        slide.picture = request.FILES['picture']

    slide.save()

    return JsonResponse({
        'success': True,
        'picture_url': slide.picture.url if slide.picture else None
    })

@login_required
def get_slide(request, slide_id):

    slide = get_object_or_404(
        Slide,
        id_slide=slide_id,
        id_presentation__id_user=request.user
    )

    return JsonResponse({
        'success': True,
        'id': slide.id_slide,
        'content': slide.content,
        'slide_type': slide.slide_type,
        'picture_url': slide.picture.url if slide.picture else None
    })
@login_required
def delete_slide(request, slide_id):
    if request.method != 'POST':
        return JsonResponse({'success': False}, status=405)

    slide = get_object_or_404(
        Slide,
        id_slide=slide_id,
        id_presentation__id_user=request.user
    )
    presentation = slide.id_presentation
    slide.delete()

    # Перенумеровываем оставшиеся слайды
    with transaction.atomic():
        for index, s in enumerate(
            presentation.slides.order_by('number'), start=1
        ):
            s.number = index
            s.save(update_fields=['number'])

    return JsonResponse({'success': True})


def reorder_slides(request, presentation_id):
    if request.method == 'POST':
        presentation = get_object_or_404(Presentation, id_presentation=presentation_id, id_user=request.user)
        try:
            data = json.loads(request.body)
            slide_ids = data.get('slide_ids', [])
            
            with transaction.atomic():
                for index, slide_id in enumerate(slide_ids, start=1):
                    Slide.objects.filter(
                        id_slide=slide_id, 
                        id_presentation=presentation
                    ).update(number=index)
                    
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
            
    return JsonResponse({'success': False}, status=405)
