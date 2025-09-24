from django.shortcuts import render
from .models import Joke, Quote
from itertools import chain
from operator import attrgetter
from .forms import KeywordForm, LanguageForm
import openai
from django.conf import settings
from django.core.paginator import Paginator

# Set the OpenAI API key
openai.api_key = settings.OPENAI_API_KEY

def joke_generator(request):
    form = KeywordForm()
    language_form = LanguageForm()
    generated_text = None     
    generated_type = None      


    if request.method == "POST":
        form = KeywordForm(request.POST)
        language_form = LanguageForm(request.POST)
        if form.is_valid() and language_form.is_valid():
            keyword = form.cleaned_data['keyword']
            language = language_form.cleaned_data['language']

            if 'generate_joke' in request.POST:
                # Генерация шутки
                try:
                    response = openai.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are a joke generator."},
                            {"role": "user", "content": f"Tell a joke about {keyword} only in {language} language. Make it original and creative."}
                        ],
                        temperature=0.7
                    )
                    joke_text = response.choices[0].message.content.strip()
                except Exception:
                    joke_text = "Sorry, I couldn't generate a joke at the moment. Please try again later."
                Joke.objects.create(keyword=keyword, text=joke_text, type='anecdote')
                generated_text = joke_text
                generated_type = 'anecdote'

            elif 'generate_quote' in request.POST:
                # Генерация цитаты
                try:
                    response = openai.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are a motivational quote generator."},
                            {"role": "user", "content": f"Give me a motivational quote about {keyword} only in {language} language."}
                        ],
                        temperature=0.7
                    )
                    quote_text = response.choices[0].message.content.strip()
                except Exception:
                    quote_text = "Sorry, I couldn't generate a quote at the moment. Please try again later."
                Quote.objects.create(keyword=keyword, text=quote_text, type='quote')
                generated_text = quote_text
                generated_type = 'quote'

    # История: объединяем шутки и цитаты
    jokes = Joke.objects.all()
    quotes = Quote.objects.all()
    history = sorted(
        chain(jokes, quotes),
        key=attrgetter('timestamp'),
        reverse=True
    )

    paginator = Paginator(history, 5)  # 10 строк на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)


    return render(request, 'joke_generator.html', {
        'form': form,
        'language_form': language_form,
        'generated_text': generated_text,
        'generated_type': generated_type,
        'history': page_obj,
    })