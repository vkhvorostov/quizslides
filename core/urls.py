from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('join/', views.join_session, name='join_session'),
    path('participant/<str:code>/', views.participant_view, name='participant'),
    path('api/session/<str:code>/state/', views.session_poll_state, name='session_poll_state'),
    path('api/session/<str:code>/vote/', views.cast_poll_vote, name='cast_poll_vote'),
    path('create/', views.create_presentation, name='create_presentation'),
    path('editor/<int:presentation_id>/', views.editor_view, name='editor'),
    path('presentation/<int:presentation_id>/start/', views.start_presentation, name='start_presentation'),
    path('presentation/<int:presentation_id>/', views.present_presentation, name='present_presentation'),
    path(
        'api/presentation/<int:presentation_id>/poll-results/',
        views.presentation_poll_results,
        name='presentation_poll_results',
    ),
    path('api/presentation/<int:presentation_id>/update-title/', views.update_title, name='update_title'),
    path('api/presentation/<int:presentation_id>/add-slide/', views.add_slide, name='add_slide'),
    path('api/slide/<int:slide_id>/update-content/', views.update_slide_content, name='update_slide_content'),
    path('api/slide/<int:slide_id>/update-poll/', views.update_poll_slide, name='update_poll_slide'),
    path('api/slide/<int:slide_id>/', views.get_slide, name='get_slide'),
    path('api/slide/<int:slide_id>/delete/', views.delete_slide, name='delete_slide'),
    path('api/presentation/<int:presentation_id>/reorder-slides/', views.reorder_slides, name='reorder_slides'),
]
