from django.utils import translation

class ForceEnglishDefaultMiddleware:
    """Middleware, который устанавливает английский язык по умолчанию для всех пользователей"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.COOKIES.get('django_language'):
            translation.activate('en')
            request.LANGUAGE_CODE = 'en'
        return self.get_response(request)
