from typing import Iterable
from django.db import models
from django.utils.translation import gettext as _


class UserProfile(models.Model):
    first_name = models.CharField(
        _('Имя'),
        max_length=120
    )
    last_name = models.CharField(
        _('Фамилия'),
        max_length=120
    )
    group = models.CharField(
        _('Группа'),
        max_length=120
    )
    registration_date = models.DateField(
        _('Дата регистрации'),
        auto_now_add=True
    )
    last_registration_date = models.DateField(
        _('Дата последней регистрации'),
        auto_now=True
    )
    result_quiz = models.ManyToManyField('QuizResult', related_name='result_quiz_user', blank=True, null=True)

    def __str__(self) -> str:
        return f'Студент: {self.first_name} {self.last_name} Группа: {self.group}'
    
    class Meta:
        verbose_name = _('Студент')
        verbose_name_plural = _('Студенты')



class Category(models.Model):
    name = models.CharField(
        _('Название'),
        max_length=255
    )

    def __str__(self) -> str:
        return f"Категория: {self.name}"
    
    class Meta:
        verbose_name = _('Категория')
        verbose_name_plural = _('Категории')



"""Это Доступные ответы"""
class Question(models.Model):
    quiz = models.ForeignKey('Quiz', null=True, blank=True, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='question_category')
    text = models.TextField(_('Текст вопроса'))

    def __str__(self) -> str:
        return f'{self.category} Вопрос: {self.text}'


class AccessAnswer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='access_answers')
    answer = models.CharField(_('Ответ'), max_length=255)
    is_true = models.BooleanField(_('Ответ правильный?'), default=False)

    def __str__(self) -> str:
        return f'Ответ: {self.answer} он правильный? {self.is_true if False else "Нет" if True else "Да"}'




class QuizResult(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    correct_answers = models.IntegerField(
        _('Количество правильных ответов'),
        default=0
    )
    total_questions = models.IntegerField(
        _('Общее количество вопросов'),
        default=0
    )
    percentage = models.FloatField(
        _('Процент правильных ответов'),
        default=0
    )

class Quiz(models.Model):
    user = models.ManyToManyField(UserProfile, related_name='quiz_user', blank=True)
    theme = models.CharField(
        _('Тема квиза'),
        max_length=120
    )
    questions = models.ManyToManyField(
        Question, 
        related_name='quiz_questions',
        verbose_name=_('вопросы квиза'),
    )
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE,
        related_name='quiz_category',
        verbose_name=_('Категория')
    )


