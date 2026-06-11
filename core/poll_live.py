from django.utils import timezone

from .models import AnswerOption, Member, PollVote, Presentation, Session, Slide


def get_active_presentation(session):
    return Presentation.objects.filter(
        id_session=session, status=True
    ).select_related('id_session').first()


def get_current_slide(presentation, session):
    slides = list(presentation.slides.order_by('number'))
    if not slides:
        return None, slides, 0
    index = max(1, min(session.current_slide_number, len(slides)))
    return slides[index - 1], slides, index


def poll_results_for_slide(slide):
    widget = slide.widgets.first()
    if not widget:
        return {'options': [], 'total_voters': 0}

    options = list(widget.answer_options.order_by('number'))
    total_voters = PollVote.objects.filter(id_slide=slide).count()
    results = []
    for opt in options:
        count = PollVote.objects.filter(
            id_slide=slide, id_answer_option=opt
        ).count()
        percent = round(100 * count / total_voters, 1) if total_voters else 0
        results.append({
            'id': opt.id_answer_option,
            'text': opt.text,
            'count': count,
            'percent': percent,
            'is_correct': opt.is_correct,
        })
    return {'options': results, 'total_voters': total_voters}


def get_poll_time_left(session, slide):
    if not slide or not slide.timer or slide.timer <= 0:
        return None
    if not session.current_slide_started_at:
        return slide.timer
    elapsed = (timezone.now() - session.current_slide_started_at).total_seconds()
    remaining = slide.timer - int(elapsed)
    return max(0, remaining)


def build_session_state(session, member=None):
    presentation = get_active_presentation(session)
    if not presentation:
        return {'active': False, 'error': 'Презентация не запущена'}

    slide, slides, index = get_current_slide(presentation, session)
    payload = {
        'active': True,
        'presentation_id': presentation.id_presentation,
        'current_slide': index,
        'total_slides': len(slides),
        'slide_type': slide.slide_type if slide else 'CONTENT',
        'question': slide.content if slide else '',
        'options': _poll_options_payload(slide, include_correct=False) if slide and slide.slide_type == 'POLL' else [],
        'results': None,
        'my_vote_option_id': None,
        'timer': 0,
        'remaining_seconds': 0,
        'allow_change_answer': False,
    }

    if slide and slide.slide_type == 'POLL':
        payload['results'] = poll_results_for_slide(slide)
        payload['timer'] = slide.timer or 0
        payload['remaining_seconds'] = get_poll_time_left(session, slide) or 0
        payload['allow_change_answer'] = slide.allow_change_answer
        if member:
            vote = PollVote.objects.filter(
                id_slide=slide, id_member=member
            ).first()
            if vote:
                payload['my_vote_option_id'] = vote.id_answer_option_id

    return payload


def _poll_options_payload(slide, include_correct=False):
    widget = slide.widgets.first()
    if not widget:
        return []
    payload = []
    for opt in widget.answer_options.order_by('number'):
        item = {'id': opt.id_answer_option, 'number': opt.number, 'text': opt.text}
        if include_correct:
            item['is_correct'] = opt.is_correct
        payload.append(item)
    return payload


def get_member_from_request(request, session):
    member_id = request.session.get('poll_member_id')
    if not member_id:
        return None
    return Member.objects.filter(
        id_member=member_id, id_session=session
    ).first()
