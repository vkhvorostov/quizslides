import json
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.views.decorators.http import require_POST

from .models import AnswerOption, Member, PollVote, Presentation, Session, Slide, Widget
from .poll_live import (
    build_session_state,
    get_active_presentation,
    get_current_slide,
    get_member_from_request,
    poll_results_for_slide,
)


SESSION_CODE_ALPHABET = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'


def _ensure_poll_widget(slide):
    widget = slide.widgets.first()
    if widget:
        return widget
    widget = Widget.objects.create(id_slide=slide)
    AnswerOption.objects.create(id_widget=widget, number=1, text='Вариант 1')
    AnswerOption.objects.create(id_widget=widget, number=2, text='Вариант 2')
    return widget


def _poll_options_payload(slide):
    widget = slide.widgets.first()
    if not widget:
        return []
    return [
        {'id': opt.id_answer_option, 'number': opt.number, 'text': opt.text}
        for opt in widget.answer_options.order_by('number')
    ]


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

    slides = list(presentation.slides.order_by('number'))
    if not slides:
        messages.error(request, 'Добавьте хотя бы один слайд перед запуском')
        return redirect('core:editor', presentation_id=presentation.id_presentation)

    try:
        current_index = int(request.GET.get('slide', 1))
    except (TypeError, ValueError):
        current_index = 1
    current_index = max(1, min(current_index, len(slides)))

    session = presentation.id_session
    if session.current_slide_number != current_index:
        session.current_slide_number = current_index
        session.save(update_fields=['current_slide_number'])

    current_slide = slides[current_index - 1]
    poll_results = None
    if current_slide.slide_type == 'POLL':
        _ensure_poll_widget(current_slide)
        poll_results = poll_results_for_slide(current_slide)

    return render(request, 'core/present.html', {
        'presentation': presentation,
        'session': session,
        'current_slide': current_slide,
        'current_index': current_index,
        'total_slides': len(slides),
        'poll_results': poll_results,
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
        if slide_type == 'POLL':
            _ensure_poll_widget(new_slide)

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

    payload = {
        'success': True,
        'id': slide.id_slide,
        'content': slide.content,
        'slide_type': slide.slide_type,
        'picture_url': slide.picture.url if slide.picture else None,
    }
    if slide.slide_type == 'POLL':
        _ensure_poll_widget(slide)
        payload['answer_options'] = _poll_options_payload(slide)
    return JsonResponse(payload)


@login_required
def update_poll_slide(request, slide_id):
    if request.method != 'POST':
        return JsonResponse({'success': False}, status=405)

    slide = get_object_or_404(
        Slide,
        id_slide=slide_id,
        id_presentation__id_user=request.user,
    )
    if slide.slide_type != 'POLL':
        return JsonResponse({'success': False, 'error': 'Слайд не является опросом'}, status=400)
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Неверный JSON'}, status=400)

    content = data.get('content', '').strip()
    options = data.get('options', [])
    if not options:
        return JsonResponse({'success': False, 'error': 'Добавьте хотя бы один вариант'}, status=400)

    slide.content = content
    slide.save(update_fields=['content'])

    widget = _ensure_poll_widget(slide)
    widget.answer_options.all().delete()
    for index, text in enumerate(options, start=1):
        text = str(text).strip()[:50]
        if text:
            AnswerOption.objects.create(
                id_widget=widget, number=index, text=text
            )

    return JsonResponse({
        'success': True,
        'answer_options': _poll_options_payload(slide),
    })


@login_required
def delete_slide(request, slide_id):
    if request.method != 'POST':
        return JsonResponse({'success': False}, status=405)

    slide = get_object_or_404(
        Slide,
        id_slide=slide_id,
        id_presentation__id_user=request.user,
    )
    presentation = slide.id_presentation

    with transaction.atomic():
        slide.delete()
        for index, s in enumerate(
            presentation.slides.order_by('number'), start=1
        ):
            s.number = index
            s.save(update_fields=['number'])

    return JsonResponse({'success': True})


@login_required
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


def join_session(request):
    if request.method != 'POST':
        return redirect('index')

    code = request.POST.get('code', '').strip()
    session = Session.objects.filter(code=code, status=True).first()
    if not session:
        messages.error(request, 'Код не найден или сессия завершена.')
        return redirect('index')

    presentation = get_active_presentation(session)
    if not presentation:
        messages.error(request, 'Презентация ещё не запущена организатором.')
        return redirect('index')

    members_count = session.members.count()
    if members_count >= session.max_count_people:
        messages.error(request, 'Комната заполнена.')
        return redirect('index')

    member = Member.objects.create(
        id_session=session,
        name=f'Участник {members_count + 1}',
    )
    request.session['poll_member_id'] = member.id_member
    request.session['poll_session_code'] = code
    return redirect('core:participant', code=code)


def participant_view(request, code):
    session = get_object_or_404(Session, code=code, status=True)
    presentation = get_active_presentation(session)
    if not presentation:
        messages.error(request, 'Ожидайте запуска презентации организатором.')
        return redirect('index')

    member = get_member_from_request(request, session)
    if not member:
        members_count = session.members.count()
        if members_count >= session.max_count_people:
            messages.error(request, 'Комната заполнена.')
            return redirect('index')
        member = Member.objects.create(
            id_session=session,
            name=f'Участник {members_count + 1}',
        )
        request.session['poll_member_id'] = member.id_member
        request.session['poll_session_code'] = code

    return render(request, 'core/participant.html', {
        'session': session,
        'presentation': presentation,
        'member': member,
    })


def session_poll_state(request, code):
    session = get_object_or_404(Session, code=code, status=True)
    member = get_member_from_request(request, session)
    state = build_session_state(session, member)
    return JsonResponse({'success': True, **state})


def cast_poll_vote(request, code):
    if request.method != 'POST':
        return JsonResponse({'success': False}, status=405)

    session = get_object_or_404(Session, code=code, status=True)
    member = get_member_from_request(request, session)
    if not member:
        return JsonResponse({'success': False, 'error': 'Сначала присоединитесь по коду'}, status=403)

    presentation = get_active_presentation(session)
    if not presentation:
        return JsonResponse({'success': False, 'error': 'Презентация не активна'}, status=400)

    slide, _, _ = get_current_slide(presentation, session)
    if not slide or slide.slide_type != 'POLL':
        return JsonResponse({'success': False, 'error': 'Сейчас нельзя голосовать'}, status=400)

    try:
        data = json.loads(request.body)
        option_id = int(data.get('answer_option_id'))
    except (TypeError, ValueError, json.JSONDecodeError):
        return JsonResponse({'success': False, 'error': 'Неверный вариант'}, status=400)

    option = get_object_or_404(
        AnswerOption,
        id_answer_option=option_id,
        id_widget__id_slide=slide,
    )

    PollVote.objects.update_or_create(
        id_slide=slide,
        id_member=member,
        defaults={'id_answer_option': option},
    )

    return JsonResponse({
        'success': True,
        'results': poll_results_for_slide(slide),
        'my_vote_option_id': option.id_answer_option,
    })


@login_required
def presentation_poll_results(request, presentation_id):
    presentation = get_object_or_404(
        Presentation, id_presentation=presentation_id, id_user=request.user
    )
    session = presentation.id_session
    if not session:
        return JsonResponse({'success': False}, status=400)

    slide, _, index = get_current_slide(presentation, session)
    if not slide or slide.slide_type != 'POLL':
        return JsonResponse({
            'success': True,
            'slide_type': slide.slide_type if slide else None,
            'results': None,
        })

    return JsonResponse({
        'success': True,
        'slide_type': 'POLL',
        'current_slide': index,
        'question': slide.content,
        'results': poll_results_for_slide(slide),
    })
