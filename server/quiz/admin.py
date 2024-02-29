from django.contrib import admin
from .models import UserProfile, Category, AccessAnswer, Question, QuizResult, Quiz


class AccessAnswerInline(admin.TabularInline):
    model = AccessAnswer
    extra = 1
    verbose_name = 'Доступный ответ'
    verbose_name_plural = 'Доступные ответы'


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    verbose_name = 'Вопрос'
    verbose_name_plural = 'Вопросы'
    show_change_link = True

    # def access_answers_list(self, instance):
    #     return ", ".join([answer.answer for answer in instance.access_answers.all()])

    # fields = ('text', 'access_answers_list',)
    # readonly_fields = ('access_answers_list',)


class QuizAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]
    list_display = ('theme', 'category', 'user_list')
    search_fields = ['theme']

    def user_list(self, obj):
        return ", ".join([user.first_name for user in obj.user.all()])
    user_list.short_description = 'Пользователи'


class QuestionAdmin(admin.ModelAdmin):
    inlines = [AccessAnswerInline]
    list_display = ('category', 'text')
    search_fields = ['text']

    @property
    def access_answers(self):
        return ", ".join([answer.answer for answer in self.accessanswer_set.all()])


class QuizResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'correct_answers', 'total_questions', 'percentage')
    search_fields = ['user__first_name', 'user__last_name', 'category__name']


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'group', 'registration_date', 'last_registration_date')
    search_fields = ['first_name', 'last_name', 'group']


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ['name']


admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(AccessAnswer)
admin.site.register(QuizResult, QuizResultAdmin)
admin.site.register(Quiz, QuizAdmin)
