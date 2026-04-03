from django.contrib import admin
from .models import (Session, Member, Reaction, Presentation,
                     Slide, Widget, Quiz, Vote, AnswerOption, WordCloud)

admin.site.register(Session)
admin.site.register(Member)
admin.site.register(Reaction)
admin.site.register(Presentation)
admin.site.register(Slide)
admin.site.register(Widget)
admin.site.register(Quiz)
admin.site.register(Vote)
admin.site.register(AnswerOption)
admin.site.register(WordCloud)