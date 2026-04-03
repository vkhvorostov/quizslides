from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView
from quizslides.views import HomeView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
]
