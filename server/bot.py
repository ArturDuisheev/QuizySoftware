# Импорты и инициализация Django
import os
import telebot
from django.core.wsgi import get_wsgi_application
from django.conf import settings
from telebot import types

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.core.settings')
application = get_wsgi_application()

# Импорт моделей Django
from quiz.models import UserProfile, Quiz, Category, Question, AccessAnswer, QuizResult

# Инициализация бота
bot = telebot.TeleBot("6922982086:AAGab4glS5YqEAcyFJMUI9GlydLsgJ6Uj5A")

# Обработка команды /start для регистрации пользователя
@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    user, created = UserProfile.objects.get_or_create(id=user_id)

    if not created and user.registration_date != user.last_registration_date:
        bot.send_message(user_id, "Вы уже прошли регистрацию сегодня. Приходите завтра!")
    else:
        bot.send_message(user_id, "Добро пожаловать! Пожалуйста, заполните Имя:")
        bot.register_next_step_handler(message, process_first_name)
# Обработчик ввода имени пользователя
def process_first_name(message):
    user_id = message.from_user.id
    user = UserProfile.objects.get(id=user_id)

    user.first_name = message.text
    user.save()
    bot.send_message(user_id, "Отлично! Теперь введите вашу фамилию:")
    bot.register_next_step_handler(message, process_last_name)

# Обработчик ввода фамилии пользователя
def process_last_name(message):
    user_id = message.from_user.id
    user = UserProfile.objects.get(id=user_id)

    user.last_name = message.text
    user.save()
    bot.send_message(user_id, "Хорошо! Теперь введите номер вашей группы:")
    bot.register_next_step_handler(message, process_group)

def process_group(message):
    user_id = message.from_user.id
    user = UserProfile.objects.get(id=user_id)

    user.group = message.text
    user.save()

    bot.send_message(user_id, "Регистрация завершена! Теперь вы можете участвовать в квизах. Для просмотра доступных квизов воспольозуйтесь командой: /participate")

@bot.message_handler(commands=["participate"])
def participate(message):
    user_id = message.from_user.id
    user, created = UserProfile.objects.get_or_create(id=user_id)

    if not created and user.registration_date != user.last_registration_date:
        bot.send_message(user_id, "Вы не прошли регистрацию. Воспользуйтесь командой /start для регистрации.")
        return

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    categories = Category.objects.all()

    for category in categories:
        keyboard.add(types.KeyboardButton(category.name))

    bot.send_message(user_id, "Выберите категорию:", reply_markup=keyboard)
    bot.register_next_step_handler(message, process_category_selection, user)

def process_category_selection(message, user):
    user_id = message.from_user.id

    selected_category_name = message.text
    category = Category.objects.get(name=selected_category_name)

    quiz = Quiz.objects.filter(category=category).first()

    if quiz:
        user.current_quiz = quiz
        user.save()

        first_question = Question.objects.filter(quiz=quiz).first()

        if first_question:
            user.current_question = first_question
            user.save()
            
            bot.send_message(user_id, first_question.text)
            for answer in AccessAnswer.objects.filter(question=first_question):
                bot.send_message(user_id, answer.answer)
            bot.send_message(user_id, "Введите номер правильного ответа (например, '1' или '2'):")
            bot.register_next_step_handler(message, process_answer, user)
        else:
            bot.send_message(user_id, "Извините, в данной категории нет активных вопросов.")
    else:
        bot.send_message(user_id, "Извините, в данной категории нет активных квизов.")

def process_answer(message, user):
    user_id = message.from_user.id

    try:
        selected_answer_index = int(message.text) - 1
        selected_answer = AccessAnswer.objects.filter(question=user.current_question)[selected_answer_index]

        update_user_results(user, selected_answer)

        next_question = Question.objects.filter(quiz=user.current_quiz, id__gt=user.current_question.id).first()

        if next_question:
            user.current_question = next_question
            user.save()

            bot.send_message(user_id, next_question.text)
            for answer in AccessAnswer.objects.filter(question=next_question):
                bot.send_message(user_id, answer.answer)
            bot.send_message(user_id, "Введите номер правильного ответа (например, '1' или '2'):")
            bot.register_next_step_handler(message, process_answer, user)
        else:
            display_final_scores(user)
    except ValueError:
        bot.send_message(user_id, "Пожалуйста, введите корректный номер ответа.")
        bot.register_next_step_handler(message, process_answer, user)
        

def display_final_scores(user):
    user_id = user.id
    quiz_result = QuizResult.objects.get(user=user, category=user.current_quiz.category)

    bot.send_message(user_id, f"Поздравляем! Вы завершили квиз.")
    bot.send_message(user_id, f"Ваши итоговые баллы: {quiz_result.correct_answers} из {quiz_result.total_questions} ({quiz_result.percentage:.2f}%)")

def update_user_results(user, selected_answer):
    user_id = user.id
    quiz_result, created = QuizResult.objects.get_or_create(
        user=user,
        category=user.current_quiz.category,
        defaults={'correct_answers': 0, 'total_questions': 0, 'percentage': 0}
    )

    quiz_result.total_questions += 1
    
    if selected_answer.is_true:
        quiz_result.correct_answers += 1

    quiz_result.percentage = (quiz_result.correct_answers / quiz_result.total_questions) * 100
    quiz_result.save()
    

if __name__ == "__main__":
    bot.polling(none_stop=True)
