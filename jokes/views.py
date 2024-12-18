from django.shortcuts import render
from .models import Joke
from .forms import KeywordForm, LanguageForm
import openai
from django.conf import settings

# Set the OpenAI API key
openai.api_key = settings.OPENAI_API_KEY

def joke_generator(request):
    # Initialize the forms and fetch jokes in reverse chronological order
    form = KeywordForm()
    language_form = LanguageForm()
    jokes = Joke.objects.all().order_by('-timestamp')  # Display jokes in reverse chronological order
    recent_joke = None

    # Handle form submission
    if request.method == "POST":
        form = KeywordForm(request.POST)
        language_form = LanguageForm(request.POST)
        
        # Check if both forms are valid
        if form.is_valid() and language_form.is_valid():  # Corrected this line
            # Get the keyword and language from the forms
            keyword = form.cleaned_data['keyword']
            language = language_form.cleaned_data['language']  # Access the 'language' field
            
            # Generate a joke using OpenAI ChatGPT API
            try:
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",  # You can update the model to a more recent version
                    messages=[ 
                        {"role": "system", "content": "You are a joke generator."},
                        {"role": "user", "content": f"Tell a joke about {keyword} only in {language} language. Make it original and creative."}
                    ],
                    temperature=0.7
                )
                joke_text =response.choices[0].message.content.strip()
            except Exception as e:
                joke_text = "Sorry, I couldn't generate a joke at the moment. Please try again later."

            # Save the joke to the database
            new_joke = Joke.objects.create(keyword=keyword, joke=joke_text)
            
            # Get the most recent joke after saving it
            recent_joke = Joke.objects.latest('timestamp')  # Get the latest joke by timestamp

    # Always fetch jokes in reverse chronological order for display
    jokes = Joke.objects.all().order_by('-timestamp')  # Reload jokes after adding the new one

    # Render the template with the form and the list of jokes
    return render(request, 'joke_generator.html', {
        'form': form, 
        'language_form': language_form, 
        'jokes': jokes, 
        'recent_joke': recent_joke,
        })
