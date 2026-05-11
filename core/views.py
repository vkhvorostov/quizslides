from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Presentation, Slide
import json


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
        
        new_slide = Slide.objects.create(
            id_presentation=presentation,
            number=next_number,
            status=True
        )
        
        return JsonResponse({
            'success': True, 
            'id_slide': new_slide.id_slide, 
            'number': new_slide.number
        })
    return JsonResponse({'success': False}, status=400)