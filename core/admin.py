from django.contrib import admin
from .models import (Session, Member, Reaction, Presentation,
                     Slide, Widget, Quiz, Vote, AnswerOption, WordCloud)

# --- Inlines (Вложенные формы) ---


class MemberInline(admin.TabularInline):
    model = Member
    extra = 0


class ReactionInline(admin.TabularInline):
    model = Reaction
    extra = 0


class SlideInline(admin.TabularInline):
    model = Slide
    extra = 0


class WidgetInline(admin.TabularInline):
    model = Widget
    extra = 0


class AnswerOptionInline(admin.TabularInline):
    model = AnswerOption
    extra = 0


# --- Admin Classes (Настройки отображения в админке) ---

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('code', 'id_user', 'status', 'time_begin',
                    'time_end', 'max_count_people')
    list_filter = ('status', 'time_begin')
    search_fields = ('code', 'id_user__username')
    list_editable = ('status',)
    inlines = [MemberInline, ReactionInline]


@admin.register(Presentation)
class PresentationAdmin(admin.ModelAdmin):
    list_display = ('name', 'id_user', 'id_session', 'status')
    list_filter = ('status',)
    search_fields = ('name', 'id_user__username', 'id_session__code')
    list_editable = ('status',)
    inlines = [SlideInline]


@admin.register(Slide)
class SlideAdmin(admin.ModelAdmin):
    list_display = ('id_presentation', 'number', 'status', 'has_picture')
    list_filter = ('status',)
    search_fields = ('id_presentation__name',)
    list_editable = ('status',)
    inlines = [WidgetInline]

    def has_picture(self, obj):
        return bool(obj.picture)
    has_picture.boolean = True
    has_picture.short_description = 'Картинка'


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'id_session')
    search_fields = ('name', 'id_session__code')


@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    list_display = ('id_session', 'type', 'quantity')
    list_filter = ('type',)
    search_fields = ('id_session__code',)


@admin.register(Widget)
class WidgetAdmin(admin.ModelAdmin):
    list_display = ('id_widget', 'id_slide')
    search_fields = ('id_slide__id_presentation__name',)
    inlines = [AnswerOptionInline]


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('id_quiz', 'id_widget', 'max_time', 'changeability')
    list_filter = ('changeability',)


@admin.register(WordCloud)
class WordCloudAdmin(admin.ModelAdmin):
    list_display = ('question', 'word_limit', 'id_widget')
    search_fields = ('question',)


@admin.register(AnswerOption)
class AnswerOptionAdmin(admin.ModelAdmin):
    list_display = ('text', 'number', 'id_widget')
    search_fields = ('text',)
    ordering = ('id_widget', 'number')


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('id_vote', 'id_member', 'id_quiz', 'id_presentation')
    search_fields = ('id_member__name', 'id_presentation__name')
