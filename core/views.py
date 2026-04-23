from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Presentation


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
