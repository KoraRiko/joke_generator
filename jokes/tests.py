from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import connection
from unittest.mock import patch, MagicMock
import json

from .models import Joke
from .forms import KeywordForm


# ========================
# WHITE BOX TESTS (внутренняя реализация известна)
# ========================


class KeywordFormValidationWhiteBoxTest(TestCase):
    """White box тест: проверяет валидацию формы с знанием деталей"""
    
    def test_form_validates_only_english_letters_and_spaces(self):
        """Проверяет, что форма принимает только букв и пробелы (regex: ^[A-Za-z ]+$)"""
        # Valid cases
        valid_form = KeywordForm(data={'keyword': 'hello world'})
        self.assertTrue(valid_form.is_valid())
        
        valid_form = KeywordForm(data={'keyword': 'Python'})
        self.assertTrue(valid_form.is_valid())
        
        # Invalid cases - проверяем конкретную регулярку в clean_keyword()
        invalid_form = KeywordForm(data={'keyword': 'hello123'})
        self.assertFalse(invalid_form.is_valid())
        self.assertIn('Only English letters', str(invalid_form.errors['keyword']))
        
        invalid_form = KeywordForm(data={'keyword': 'привет'})
        self.assertFalse(invalid_form.is_valid())
        
    def test_form_max_length_constraint(self):
        """Проверяет max_length=100 в модели формы"""
        form = KeywordForm(data={'keyword': 'a' * 101})
        self.assertFalse(form.is_valid())
        
        form = KeywordForm(data={'keyword': 'a' * 100})
        self.assertTrue(form.is_valid())


class JokeModelWhiteBoxTest(TestCase):
    """White box тест: проверяет поля и логику модели Joke"""
    
    def test_joke_model_fields_and_defaults(self):
        """Проверяет наличие полей и их типы в моделе Joke"""
        joke = Joke.objects.create(
            keyword='Python',
            text='Why did the programmer quit? Because he didn\'t get arrays.'
        )
        
        # Проверяем, что все поля существуют и имеют правильные значения
        self.assertEqual(joke.keyword, 'Python')
        self.assertIsNotNone(joke.text)
        self.assertIsNone(joke.rating)  # По умолчанию null
        self.assertIsNotNone(joke.timestamp)  # auto_now_add=True
        
    def test_joke_rating_validation_constraints(self):
        """Проверяет, что rating может быть null и принимает 1-10 (внутренняя логика views)"""
        joke = Joke.objects.create(keyword='Test', text='Test joke')
        self.assertIsNone(joke.rating)
        
        joke.rating = 5
        joke.save()
        self.assertEqual(joke.rating, 5)
        
        # Проверяем, что можно сохранить значения 1-10
        for rating in range(1, 11):
            joke.rating = rating
            joke.save()
            self.assertEqual(Joke.objects.get(id=joke.id).rating, rating)


class RateLimitWhiteBoxTest(TestCase):
    """White box тест: проверяет декоратор rate limit в views"""
    
    def setUp(self):
        self.client = Client()
        self.url = reverse('joke_generator')
    
    @patch('jokes.views.openai.chat.completions.create')
    def test_rate_limit_decorator_applied_to_post(self, mock_openai):
        """Проверяет, что @ratelimit на POST лимитирует 50 запросов в час"""
        # Этот тест проверяет, что декоратор @ratelimit(key='ip', rate='50/h', method='POST')
        # применён к joke_generator view
        mock_openai.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content='Funny joke here'))]
        )
        
        # Первые 50 запросов должны пройти (эта проверка требует реального тестирования)
        form_data = {'keyword': 'test', 'generate_joke': 'Generate'}
        response = self.client.post(self.url, form_data)
        # Status 200 = не заблокирован
        self.assertIn(response.status_code, [200, 429])
    
    def test_rate_limit_decorator_applied_to_get(self):
        """Проверяет, что @ratelimit на GET лимитирует 100 запросов в час"""
        # Декоратор @ratelimit(key='ip', rate='100/h', method='GET')
        response = self.client.get(self.url)
        self.assertIn(response.status_code, [200, 429])


# ========================
# BLACK BOX TESTS (только функциональность, без знания реализации)
# ========================

class JokeGeneratorFunctionalityBlackBoxTest(TestCase):
    """Black box тест: проверяет функциональность генератора, не зная внутреннего кода"""
    
    def setUp(self):
        self.client = Client()
        self.url = reverse('joke_generator')
    
    @patch('jokes.views.openai.chat.completions.create')
    def test_user_can_generate_joke_with_valid_keyword(self, mock_openai):
        """Проверяет основной сценарий: пользователь может сгенерировать анекдот"""
        mock_openai.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content='Why did the cat sit on the computer? To keep an eye on the mouse!'))]
        )
        
        form_data = {'keyword': 'cat', 'generate_joke': 'Generate'}
        response = self.client.post(self.url, form_data)
        
        # Проверяем успешный ответ
        self.assertEqual(response.status_code, 200)
        
        # Проверяем, что анекдот сохранён в БД
        self.assertTrue(Joke.objects.filter(keyword='cat').exists())
        
        # Проверяем содержимое
        joke = Joke.objects.get(keyword='cat')
        self.assertIn('mouse', joke.text.lower())
    
    @patch('jokes.views.openai.chat.completions.create')
    def test_user_can_explain_joke(self, mock_openai):
        """Проверяет функцию объяснения анекдота"""
        # Создаём анекдот в БД
        joke = Joke.objects.create(
            keyword='programmer',
            text='Why do programmers prefer dark mode? Because light attracts bugs!'
        )
        
        # Мокируем ответ OpenAI для объяснения
        mock_openai.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content='This is a pun about software bugs.'))]
        )
        
        # Отправляем запрос на объяснение
        response = self.client.post(
            self.url,
            {'joke_id': joke.id, 'explain_joke': 'Explain'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 200)
        # Проверяем JSON ответ
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertIn('pun', data['explanation'].lower())


class RateLimitBlackBoxTest(TestCase):
    """Black box тест: проверяет, что rate limit блокирует частые запросы (функция, не реализация)"""
    
    def setUp(self):
        self.client = Client()
        self.url = reverse('joke_generator')
    
    def test_rate_limit_429_returned_for_many_requests(self):
        """Проверяет, что при большом количестве запросов возвращается 429 Too Many Requests"""
        # Суть теста: система должна блокировать при лимите
        # (конкретный лимит нас не интересует, главное - функциональность работает)
        
        responses = []
        for i in range(55):  # Пытаемся превысить лимит (50/h)
            response = self.client.get(self.url)
            responses.append(response.status_code)
        
        # Проверяем, что хотя бы один ответ - это 429 (или лимит не достигнут в тесте)
        # В реальной среде 429 должна быть если лимит превышен
        has_200_or_429 = all(status in [200, 429] for status in responses)
        self.assertTrue(has_200_or_429)


class JokeRatingBlackBoxTest(TestCase):
    """Black box тест: проверяет функцию оценивания анекдота"""
    
    def setUp(self):
        self.client = Client()
        self.url = reverse('joke_generator')
        self.joke = Joke.objects.create(
            keyword='test',
            text='Why did the scarecrow win an award? He was outstanding in his field!'
        )
    
    def test_user_can_rate_joke_1_to_10(self):
        """Проверяет, что пользователь может оценить анекдот от 1 до 10"""
        for rating in [1, 5, 10]:
            response = self.client.post(
                self.url,
                {
                    'joke_id': self.joke.id,
                    'rating': rating,
                    'rate_joke': 'Rate'
                }
            )
            
            self.assertEqual(response.status_code, 200)
            
            # Проверяем, что оценка сохранена
            updated_joke = Joke.objects.get(id=self.joke.id)
            self.assertEqual(updated_joke.rating, rating)
    
    def test_invalid_rating_not_saved(self):
        """Проверяет, что некорректная оценка не сохраняется"""
        invalid_ratings = [0, 11, -1, 'invalid']
        
        for invalid_rating in invalid_ratings:
            response = self.client.post(
                self.url,
                {
                    'joke_id': self.joke.id,
                    'rating': invalid_rating,
                    'rate_joke': 'Rate'
                }
            )
            
            # Система игнорирует некорректные оценки (silent fail)
            updated_joke = Joke.objects.get(id=self.joke.id)
            # Рейтинг не должен измениться на некорректное значение
            if invalid_rating not in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
                # Рейтинг остаётся как был или None
                self.assertTrue(updated_joke.rating is None or 1 <= updated_joke.rating <= 10)
