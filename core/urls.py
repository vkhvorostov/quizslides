from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('create/', views.create_presentation, name='create_presentation'),
    path('editor/<int:presentation_id>/', views.editor_view, name='editor'),
    path('api/presentation/<int:presentation_id>/update-title/', views.update_title, name='update_title'),
    path('api/presentation/<int:presentation_id>/add-slide/', views.add_slide, name='add_slide'),
    path('api/presentation/<int:presentation_id>/reorder-slides/', views.reorder_slides, name='reorder_slides'),
]
