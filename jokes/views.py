import openai
from django.conf import settings
from django.core.paginator import Paginator
from django.shortcuts import render
from django.http import JsonResponse

from .forms import KeywordForm
from .models import Joke

# Set the OpenAI API key
openai.api_key = settings.OPENAI_API_KEY

def joke_generator(request):
    form = KeywordForm()
    generated_text = None
    generated_joke_id = None

    if request.method == "POST":
        # Handle joke explanation - return JSON
        if "explain_joke" in request.POST:
            try:
                joke_id = request.POST.get("joke_id")
                joke = Joke.objects.get(id=joke_id)
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that explains jokes in a friendly way."},
                        {"role": "user", "content": f"Explain this joke in simple words, so everyone can understand it. Write it as a natural paragraph (no numbering or bullet points): '{joke.text}'\n\nExplain what makes it funny, the wordplay/punchline, and how it relates to the keyword '{joke.keyword}'."},
                    ],
                    temperature=0.7,
                )
                explanation = response.choices[0].message.content.strip()
                return JsonResponse({"success": True, "explanation": explanation})
            except (Joke.DoesNotExist, Exception):
                return JsonResponse({"success": False, "explanation": "Could not explain this joke."})
        
        # Handle rating submission - don't process as form
        if "rate_joke" in request.POST:
            try:
                joke_id = request.POST.get("joke_id")
                rating = int(request.POST.get("rating"))
                if 1 <= rating <= 10:
                    joke = Joke.objects.get(id=joke_id)
                    joke.rating = rating
                    joke.save()
            except (ValueError, Joke.DoesNotExist):
                pass
            # Don't process further - just return with empty form
            form = KeywordForm()
        else:
            # Handle joke generation
            form = KeywordForm(request.POST)
            if form.is_valid():
                keyword = form.cleaned_data["keyword"]

                if "generate_joke" in request.POST:
                    try:
                        response = openai.chat.completions.create(
                            model="ft:gpt-3.5-turbo-0125:korariko::DQ1ft67K",
                            messages=[
                                {"role": "system","content": "You are a professional comedy writer specializing in clever wordplay and safe-but-edgy humor. Apply the Benign Violation principle — break an expectation or norm, but keep it safe and clever."},
                                {"role": "user","content": f"""Generate a short, clever joke about: {keyword}. Joke should visible include the keyword '{keyword}'.""" },
                                    ],
                            temperature=0.9,
                        )
                        joke_text = response.choices[0].message.content.strip()
                    except Exception:
                        joke_text = "Sorry, I couldn't generate a joke at the moment. Please try again later."
                    joke_obj = Joke.objects.create(keyword=keyword, text=joke_text)
                    generated_text = joke_text
                    generated_joke_id = joke_obj.id

                form = KeywordForm()

    history = Joke.objects.order_by("-timestamp")

    paginator = Paginator(history, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "joke_generator.html",
        {
            "form": form,
            "generated_text": generated_text,
            "generated_joke_id": generated_joke_id,
            "history": page_obj,
        },
    )
