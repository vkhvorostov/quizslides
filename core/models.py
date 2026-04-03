from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

class TypeReaction(models.TextChoices):
    """Типы реакций"""
    COOL = 'Cool',
    BAD = 'Bad'

class Session(models.Model):
    """Сессия"""
    id_session = models.AutoField(primary_key=True)
    status = models.BooleanField(default=False)
    time_begin = models.DateTimeField(auto_now_add=True)
    time_end = models.DateTimeField()
    max_count_people = models.IntegerField()
    code = models.CharField(max_length=10)
    id_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='sessions')

class Member(models.Model):
    """Участник"""
    id_member = models.AutoField(primary_key=True)
    id_session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='members')
    name = models.CharField(max_length=50)

class Reaction(models.Model):
    """Реакция"""
    id_reaction = models.AutoField(primary_key=True)
    id_session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='reactions')
    type = models.CharField(max_length=10, choices=TypeReaction.choices)
    quantity = models.IntegerField(default=0)

class Presentation(models.Model):
    """Презентация"""
    id_presentation = models.AutoField(primary_key=True)
    id_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='presentations')
    id_session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='presentations_in_session')
    name = models.CharField(max_length=50)
    status = models.BooleanField(default=False)

class Slide(models.Model):
    """Слайд"""
    id_slide = models.AutoField(primary_key=True)
    number = models.IntegerField()
    picture = models.ImageField(upload_to='slides/', null=True, blank=True)
    status = models.BooleanField(default=False)
    id_presentation = models.ForeignKey(Presentation, on_delete=models.CASCADE, related_name='slides')

class Widget(models.Model):
    """Виджет"""
    id_widget = models.AutoField(primary_key=True)
    id_slide = models.ForeignKey(Slide, on_delete=models.CASCADE, related_name='widgets')

class WordCloud(models.Model):
    """Облако слов"""
    id_word_cloud = models.AutoField(primary_key=True)
    word_limit = models.IntegerField()
    question = models.CharField(max_length=50)
    id_widget = models.ForeignKey(Widget, on_delete=models.CASCADE, related_name='word_clouds')

class AnswerOption(models.Model):
    """Вариант ответа"""
    id_answer_option = models.AutoField(primary_key=True)
    number = models.IntegerField()
    text = models.CharField(max_length=50)
    id_widget = models.ForeignKey(Widget, on_delete=models.CASCADE, related_name='answer_options')

class Quiz(models.Model):
    """Опрос"""
    id_quiz = models.AutoField(primary_key=True)
    max_time = models.TimeField()
    changeability = models.BooleanField()
    id_widget = models.ForeignKey(Widget, on_delete=models.CASCADE, related_name='quizes')

class Vote(models.Model):
    """Голосование"""
    id_vote = models.AutoField(primary_key=True)
    id_member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='votes')
    id_quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='votes_in_quiz')
    id_presentation = models.ForeignKey(Presentation, on_delete=models.CASCADE, related_name='votes_in_presentation')
    id_widget = models.ForeignKey(Widget, on_delete=models.CASCADE, related_name='votes_in_widget')