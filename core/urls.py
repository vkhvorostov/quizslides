from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('create/', views.create_presentation, name='create_presentation'),
]
