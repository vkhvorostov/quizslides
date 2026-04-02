from django.shortcuts import render
from django.views.generic import TemplateView


class HomeView(TemplateView):
    """Главная страница платформы QuizSlides"""
    template_name = 'home.html'


def about_view(request):
    """Страница 'О проекте'"""
    return render(request, 'about.html')