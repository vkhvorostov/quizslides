import pytest
from django.contrib.auth import get_user_model
from core.models import (
    Session, Member, Reaction, Presentation, Slide,
    Widget, WordCloud, AnswerOption, Quiz, Vote, TypeReaction
)

User = get_user_model()


@pytest.mark.django_db
class TestSessionModel:

    def test_create_session(self, user):
        session = Session.objects.create(
            status=True,
            time_end='2025-12-31T23:59:59Z',
            max_count_people=100,
            code='ABC123',
            id_user=user
        )
        assert session.id_session is not None
        assert session.status is True
        assert session.code == 'ABC123'
        assert session.id_user == user

    def test_session_str(self, user):
        session = Session.objects.create(
            status=False,
            time_end='2025-12-31T23:59:59Z',
            max_count_people=50,
            code='TEST',
            id_user=user
        )
        # По умолчанию __str__ возвращает что? Обычно id.
        # Можно добавить метод __str__ в модель, но пока просто проверяем, что строка не пустая.
        assert str(session) != ''


@pytest.mark.django_db
class TestMemberModel:

    def test_create_member(self, user):
        session = Session.objects.create(
            status=True,
            time_end='2025-12-31T23:59:59Z',
            max_count_people=10,
            code='MEM',
            id_user=user
        )
        member = Member.objects.create(
            id_session=session,
            name='John Doe'
        )
        assert member.id_member is not None
        assert member.name == 'John Doe'
        assert member.id_session == session


@pytest.mark.django_db
class TestReactionModel:

    def test_create_reaction(self, user):
        session = Session.objects.create(
            status=True,
            time_end='2025-12-31T23:59:59Z',
            max_count_people=10,
            code='REACT',
            id_user=user
        )
        reaction = Reaction.objects.create(
            id_session=session,
            type=TypeReaction.COOL,
            quantity=5
        )
        assert reaction.id_reaction is not None
        assert reaction.type == TypeReaction.COOL
        assert reaction.quantity == 5


@pytest.mark.django_db
class TestPresentationModel:

    def test_create_presentation(self, user):
        presentation = Presentation.objects.create(
            id_user=user,
            name='Test Presentation',
            status=True
        )
        assert presentation.id_presentation is not None
        assert presentation.name == 'Test Presentation'
        assert presentation.status is True
        assert presentation.id_user == user

    def test_presentation_with_session(self, user):
        session = Session.objects.create(
            status=True,
            time_end='2025-12-31T23:59:59Z',
            max_count_people=10,
            code='PRES',
            id_user=user
        )
        presentation = Presentation.objects.create(
            id_user=user,
            id_session=session,
            name='Session Presentation',
            status=False
        )
        assert presentation.id_session == session


@pytest.mark.django_db
class TestSlideModel:

    def test_create_slide(self, user):
        presentation = Presentation.objects.create(
            id_user=user,
            name='Pres for slide',
            status=True
        )
        slide = Slide.objects.create(
            number=1,
            picture=None,
            status=True,
            id_presentation=presentation
        )
        assert slide.id_slide is not None
        assert slide.number == 1
        assert slide.id_presentation == presentation


@pytest.mark.django_db
class TestWidgetModel:

    def test_create_widget(self, user):
        presentation = Presentation.objects.create(
            id_user=user,
            name='Pres for widget',
            status=True
        )
        slide = Slide.objects.create(
            number=1,
            picture=None,
            status=True,
            id_presentation=presentation
        )
        widget = Widget.objects.create(id_slide=slide)
        assert widget.id_widget is not None
        assert widget.id_slide == slide


@pytest.mark.django_db
class TestWordCloudModel:

    def test_create_wordcloud(self, user):
        presentation = Presentation.objects.create(
            id_user=user,
            name='Pres for wordcloud',
            status=True
        )
        slide = Slide.objects.create(
            number=1,
            picture=None,
            status=True,
            id_presentation=presentation
        )
        widget = Widget.objects.create(id_slide=slide)
        wordcloud = WordCloud.objects.create(
            word_limit=10,
            question='What is your favorite color?',
            id_widget=widget
        )
        assert wordcloud.id_word_cloud is not None
        assert wordcloud.question == 'What is your favorite color?'


@pytest.mark.django_db
class TestAnswerOptionModel:

    def test_create_answer_option(self, user):
        presentation = Presentation.objects.create(
            id_user=user,
            name='Pres for answer',
            status=True
        )
        slide = Slide.objects.create(
            number=1,
            picture=None,
            status=True,
            id_presentation=presentation
        )
        widget = Widget.objects.create(id_slide=slide)
        answer = AnswerOption.objects.create(
            number=1,
            text='Option A',
            id_widget=widget
        )
        assert answer.id_answer_option is not None
        assert answer.text == 'Option A'


@pytest.mark.django_db
class TestQuizModel:

    def test_create_quiz(self, user):
        presentation = Presentation.objects.create(
            id_user=user,
            name='Pres for quiz',
            status=True
        )
        slide = Slide.objects.create(
            number=1,
            picture=None,
            status=True,
            id_presentation=presentation
        )
        widget = Widget.objects.create(id_slide=slide)
        quiz = Quiz.objects.create(
            max_time='00:05:00',
            changeability=True,
            id_widget=widget
        )
        assert quiz.id_quiz is not None
        assert quiz.changeability is True


@pytest.mark.django_db
class TestVoteModel:


    def test_create_vote(self, user):
  
        session = Session.objects.create(
            status=True,
            time_end='2025-12-31T23:59:59Z',
            max_count_people=10,
            code='VOTE',
            id_user=user
        )
        member = Member.objects.create(
            id_session=session,
            name='Voter'
        )
        presentation = Presentation.objects.create(
            id_user=user,
            name='Pres for vote',
            status=True
        )
        slide = Slide.objects.create(
            number=1,
            picture=None,
            status=True,
            id_presentation=presentation
        )
        widget = Widget.objects.create(id_slide=slide)
        quiz = Quiz.objects.create(
            max_time='00:03:00',
            changeability=False,
            id_widget=widget
        )
        vote = Vote.objects.create(
            id_member=member,
            id_quiz=quiz,
            id_presentation=presentation,
            id_widget=widget
        )
        assert vote.id_vote is not None
        assert vote.id_member == member
        assert vote.id_quiz == quiz