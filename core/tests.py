from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Presentation, Session, Slide


User = get_user_model()


class StartPresentationTests(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(
			username='author',
			password='strong-password-123',
		)
		self.client.force_login(self.user)
		self.presentation = Presentation.objects.create(
			name='Демо презентация',
			id_user=self.user,
		)

	def test_start_presentation_requires_at_least_one_slide(self):
		response = self.client.post(
			reverse('core:start_presentation', args=[self.presentation.id_presentation]),
			follow=True,
		)

		self.presentation.refresh_from_db()

		self.assertRedirects(
			response,
			reverse('core:editor', args=[self.presentation.id_presentation]),
		)
		self.assertContains(response, 'Добавьте хотя бы один слайд перед запуском')
		self.assertFalse(self.presentation.status)
		self.assertIsNone(self.presentation.id_session)
		self.assertEqual(Session.objects.count(), 0)

	def test_start_presentation_creates_active_session_and_shows_presenter_screen(self):
		Slide.objects.create(
			id_presentation=self.presentation,
			number=1,
			status=True,
		)

		response = self.client.post(
			reverse('core:start_presentation', args=[self.presentation.id_presentation]),
			follow=True,
		)

		self.presentation.refresh_from_db()
		session = self.presentation.id_session

		self.assertRedirects(
			response,
			reverse('core:present_presentation', args=[self.presentation.id_presentation]),
		)
		self.assertTrue(self.presentation.status)
		self.assertIsNotNone(session)
		self.assertTrue(session.status)
		self.assertEqual(session.id_user, self.user)
		self.assertGreaterEqual(session.time_end, timezone.now() + timedelta(hours=3, minutes=59))
		self.assertLessEqual(session.time_end, timezone.now() + timedelta(hours=4, minutes=1))
		self.assertContains(response, self.presentation.name)
		self.assertContains(response, session.code)
		self.assertContains(response, 'Слайд 1')
